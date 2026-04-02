#!/usr/bin/env python3
"""
memory.py  --  RigGPT runtime memory interface
===============================================
Called by app.py at trip start and per-turn to retrieve relevant
Discord community context from Qdrant.

Import pattern in app.py:
    from memory import RigGPTMemory
    _memory = RigGPTMemory()   # init once at startup

Usage in _buildCtx:
    ctx = _memory.build_context(topic, turn_n, agent_side)
    # Returns a prose string ready to inject into the system prompt.
"""

import json
import logging
import time
from typing import Optional

import requests

log = logging.getLogger("riggpt.memory")

# Collection names (must match riggpt-ingest.py)
COL_MESSAGES = "discord_messages"
COL_PROFILES = "user_profiles"
COL_THEMES   = "channel_themes"
COL_THREADS  = "conversation_threads"

# How many search results to pull per query
MSG_SEARCH_LIMIT     = 6
PROFILE_SEARCH_LIMIT = 4


class RigGPTMemory:
    """
    Lightweight runtime interface to the Qdrant memory store.
    Does NOT depend on qdrant-client — uses REST API directly so
    it adds zero new hard dependencies to the RigGPT install.
    """

    def __init__(self, qdrant_host: str = "http://192.168.40.15:6333",
                 ollama_host: str = "http://192.168.40.15:11434",
                 embed_model: str = "nomic-embed-text"):
        self.qdrant_host = qdrant_host.rstrip("/")
        self.ollama_host = ollama_host.rstrip("/")
        self.embed_model = embed_model
        self._available: Optional[bool] = None   # None = not checked yet
        self._channel_themes: Optional[dict] = None
        self._themes_fetched_at: float = 0.0

    # ── availability ──────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """
        Check if Qdrant is reachable. Cached for 60s so it doesn't add
        latency to every turn.
        """
        now = time.time()
        if self._available is not None:
            if now - getattr(self, "_checked_at", 0) < 60:
                return self._available
        try:
            r = requests.get(f"{self.qdrant_host}/healthz", timeout=3)
            self._available = r.status_code == 200
        except Exception:
            self._available = False
        self._checked_at = now
        return self._available

    # ── embedding ─────────────────────────────────────────────────────────

    def _embed(self, text: str) -> Optional[list]:
        """Embed a single text via Ollama. Returns None on failure."""
        try:
            r = requests.post(
                f"{self.ollama_host}/api/embed",
                json={"model": self.embed_model, "input": [text]},
                timeout=15
            )
            r.raise_for_status()
            return r.json()["embeddings"][0]
        except Exception as e:
            log.warning(f"Embed failed: {e}")
            return None

    # ── qdrant queries ────────────────────────────────────────────────────

    def _qdrant_search(self, collection: str, vector: list,
                       limit: int = 5, score_threshold: float = 0.4) -> list:
        """Vector search against a Qdrant collection. Returns payload dicts."""
        try:
            r = requests.post(
                f"{self.qdrant_host}/collections/{collection}/points/search",
                json={
                    "vector":           vector,
                    "limit":            limit,
                    "with_payload":     True,
                    "score_threshold":  score_threshold,
                },
                timeout=10
            )
            r.raise_for_status()
            return [p["payload"] for p in r.json().get("result", [])]
        except Exception as e:
            log.warning(f"Qdrant search failed ({collection}): {e}")
            return []

    def _qdrant_scroll_first(self, collection: str, limit: int = 1) -> list:
        """Scroll (no vector) — used to fetch the single channel themes doc."""
        try:
            r = requests.post(
                f"{self.qdrant_host}/collections/{collection}/points/scroll",
                json={"limit": limit, "with_payload": True,
                      "with_vector": False},
                timeout=10
            )
            r.raise_for_status()
            return [p["payload"] for p in r.json().get("result", {}).get("points", [])]
        except Exception as e:
            log.warning(f"Qdrant scroll failed ({collection}): {e}")
            return []

    # ── public API ────────────────────────────────────────────────────────

    def get_channel_themes(self, max_age_seconds: int = 3600) -> Optional[dict]:
        """
        Return the channel-level community profile.
        Cached in memory; refreshes at most once per hour.
        """
        now = time.time()
        if (self._channel_themes is not None and
                now - self._themes_fetched_at < max_age_seconds):
            return self._channel_themes

        results = self._qdrant_scroll_first(COL_THEMES, limit=1)
        if results:
            self._channel_themes = results[0]
            self._themes_fetched_at = now
        return self._channel_themes

    def search_messages(self, query: str,
                        limit: int = MSG_SEARCH_LIMIT) -> list[dict]:
        """Semantic search across stored Discord messages."""
        vec = self._embed(query)
        if vec is None:
            return []
        return self._qdrant_search(COL_MESSAGES, vec, limit=limit,
                                   score_threshold=0.45)

    def search_profiles(self, query: str,
                        limit: int = PROFILE_SEARCH_LIMIT) -> list[dict]:
        """Find user profiles relevant to a topic."""
        vec = self._embed(query)
        if vec is None:
            return []
        return self._qdrant_search(COL_PROFILES, vec, limit=limit,
                                   score_threshold=0.35)

    def search_threads(self, query: str, limit: int = 4) -> list[dict]:
        """Find past conversation threads relevant to a topic."""
        vec = self._embed(query)
        if vec is None:
            return []
        return self._qdrant_search(COL_THREADS, vec, limit=limit,
                                   score_threshold=0.40)

    def build_context(self, topic: str, turn_n: int = 0,
                      agent_side: str = "a") -> str:
        """
        Build the memory context string to inject into a system prompt.

        Returns a prose paragraph (or empty string if memory unavailable)
        covering:
          - Community character and recurring culture
          - Audience profiles relevant to the current topic
          - Specific past messages semantically close to the topic

        The text is written as the agent's own background knowledge —
        no headers, no labels, no brackets. Just character memory.
        """
        if not self.is_available():
            return ""

        parts = []

        # 1. Channel-level community DNA — injected every turn, cached
        themes = self.get_channel_themes()
        if themes:
            char   = themes.get("community_character", "")
            humor  = themes.get("humor_culture", "")
            care   = themes.get("what_they_care_about", "")
            jokes  = themes.get("running_jokes_or_references", [])
            phrases = themes.get("distinctive_phrases", [])
            tech   = themes.get("technical_culture", "")

            community_prose = _join_nonempty([
                char,
                f"Their humor runs toward: {humor}" if humor else "",
                f"Technically, {tech}" if tech else "",
                f"What they actually care about: {care}" if care else "",
                f"Running references in this community: {', '.join(jokes[:4])}." if jokes else "",
                f"Phrases you might hear: {', '.join(phrases[:4])}." if phrases else "",
            ])
            if community_prose:
                parts.append(community_prose)

        # 2. Per-turn: search messages and profiles relevant to current topic
        #    Alternate query angle per agent so A and B get different facets
        query_angle = topic if agent_side == "a" else f"{topic} reaction disagreement opinion"

        profiles = self.search_profiles(query_angle)
        if profiles:
            profile_lines = []
            for p in profiles[:3]:
                style  = p.get("communication_style", "")
                role   = p.get("audience_role", "")
                themes_list = p.get("dominant_topics", [])
                h_style = p.get("humor_style", "")
                recur  = p.get("recurring_themes", [])

                name   = p.get("display_name") or p.get("author_username", "")
                intro  = (f"{name} is a {role}" if (name and role) else
                          (name if name else (f"One regular is a {role}" if role else "One regular")))
                line_parts = [intro] if intro else []
                if not line_parts:
                    line_parts.append("One regular")
                if style:
                    line_parts.append(style)
                if themes_list:
                    line_parts.append(f"Their usual territory: {', '.join(themes_list[:3])}.")
                if h_style:
                    line_parts.append(f"Humor style: {h_style}.")
                if recur:
                    line_parts.append(f"They often return to: {', '.join(recur[:2])}.")

                if line_parts:
                    profile_lines.append(" ".join(line_parts))

            if profile_lines:
                parts.append(
                    "The people listening to you right now include: " +
                    " Another is ".join(profile_lines) + "."
                )

        # 3. Conversation threads relevant to the topic — early turns only
        if turn_n <= 3:
            threads = self.search_threads(topic, limit=3)
            if threads:
                thread_lines = []
                for t in threads:
                    summary = t.get("summary", "").strip()
                    names   = t.get("participant_displays") or t.get("participant_usernames", [])
                    who     = ", ".join(names[:3]) if names else ""
                    if summary:
                        entry = summary
                        if who:
                            entry = f"[{who}] {entry}"
                        thread_lines.append(entry)
                if thread_lines:
                    parts.append(
                        "Past conversations in this community on related topics: " +
                        " | ".join(thread_lines) + "."
                    )

        # 4. Semantically similar past messages — inject on early turns only
        #    (keeps it fresh; later turns rely more on live Discord lookback)
        if turn_n <= 3:
            past_msgs = self.search_messages(topic, limit=5)
            if past_msgs:
                # Deduplicate similar content
                seen = set()
                unique = []
                for m in past_msgs:
                    sig = m.get("content", "")[:40].lower()
                    if sig not in seen:
                        seen.add(sig)
                        unique.append(m["content"])

                if unique:
                    parts.append(
                        "This community has talked about similar things before. "
                        "Some things that have come up: " +
                        " Also: ".join(f'"{t}"' for t in unique[:3]) + "."
                    )

        return "\n\n".join(parts)

    def build_briefing(self, topic: str) -> str:
        """
        Generate a pre-trip briefing paragraph for both agents.
        Called once at trip start, injected into turn-0 system context.
        Covers: community stance on the topic, relevant past threads,
        notable community members who care about this subject.
        Returns prose string or empty string if memory unavailable.
        """
        if not self.is_available():
            return ""

        parts = []

        # Past threads on this topic
        threads = self.search_threads(topic, limit=4)
        if threads:
            thread_bits = []
            for t in threads:
                summary = t.get("summary", "").strip()
                names   = t.get("participant_displays") or t.get("participant_usernames", [])
                who     = ", ".join(names[:2]) if names else ""
                if summary:
                    thread_bits.append(f"[{who}] {summary}" if who else summary)
            if thread_bits:
                parts.append(
                    "Before this debate began, here is what your audience has already "
                    "said about this topic: " +
                    " | ".join(thread_bits) + "."
                )

        # Community members who care about this topic
        profiles = self.search_profiles(topic, limit=4)
        if profiles:
            interested = []
            for p in profiles:
                name   = p.get("display_name") or p.get("author_username", "")
                role   = p.get("audience_role", "")
                topics = p.get("dominant_topics", [])
                humor  = p.get("humor_style", "")
                if name:
                    desc = name
                    if role:
                        desc += f" ({role})"
                    if topics:
                        desc += f" — usually talks about {topics[0]}"
                    if humor:
                        desc += f", humor style: {humor}"
                    interested.append(desc)
            if interested:
                parts.append(
                    "Community members most likely to be watching and reacting: " +
                    "; ".join(interested[:3]) + "."
                )

        # Channel themes for general grounding
        themes = self.get_channel_themes()
        if themes:
            jokes = themes.get("running_jokes_or_references", [])
            if jokes:
                parts.append(
                    "Running references you can drop naturally: " +
                    ", ".join(jokes[:4]) + "."
                )

        return "\n\n".join(parts)

    def status_dict(self) -> dict:
        """Return a status summary for the /api/memory/status endpoint."""
        available = self.is_available()
        result = {
            "available":    available,
            "qdrant_host":  self.qdrant_host,
            "embed_model":  self.embed_model,
        }
        if not available:
            return result

        for col in [COL_MESSAGES, COL_PROFILES, COL_THEMES, COL_THREADS]:
            try:
                r = requests.get(
                    f"{self.qdrant_host}/collections/{col}",
                    timeout=5
                )
                if r.status_code == 200:
                    result[col] = r.json()["result"]["points_count"]
                else:
                    result[col] = 0
            except Exception:
                result[col] = -1

        themes = self.get_channel_themes()
        if themes:
            result["themes_generated_at"] = themes.get("generated_at", "")
            result["primary_topics"] = themes.get("primary_topics", [])

        return result

    # ── write operations ──────────────────────────────────────────────────

    def _qdrant_upsert(self, collection: str, point_id: str,
                       vector: list, payload: dict) -> bool:
        """Upsert a single point into a Qdrant collection."""
        try:
            r = requests.put(
                f"{self.qdrant_host}/collections/{collection}/points",
                json={
                    "points": [{
                        "id": point_id,
                        "vector": vector,
                        "payload": payload,
                    }]
                },
                timeout=10,
            )
            r.raise_for_status()
            return True
        except Exception as e:
            log.warning(f"Qdrant upsert failed ({collection}): {e}")
            return False

    def store_summary(self, summary: str, participants: list[str],
                      topics: list[str], message_count: int,
                      channel: str = '') -> bool:
        """Store a conversation summary as a vector in conversation_threads."""
        if not self.is_available():
            return False
        vec = self._embed(summary)
        if vec is None:
            return False
        import hashlib, datetime
        ts = datetime.datetime.utcnow().isoformat() + 'Z'
        point_id = hashlib.md5(f"{ts}:{summary[:50]}".encode()).hexdigest()
        payload = {
            "summary":                summary,
            "participant_usernames":  participants,
            "participant_displays":   participants,
            "primary_topics":         topics,
            "message_count":          message_count,
            "channel":                channel,
            "generated_at":           ts,
            "source":                 "dbot_auto_summary",
        }
        return self._qdrant_upsert(COL_THREADS, point_id, vec, payload)


# ── helpers ───────────────────────────────────────────────────────────────

def _join_nonempty(parts: list, sep: str = " ") -> str:
    return sep.join(p.strip() for p in parts if p and p.strip())
