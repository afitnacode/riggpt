#!/usr/bin/env python3
"""
riggpt-ingest.py  --  Discord channel history ingestion for RigGPT memory
==========================================================================
One-time full history scan + efficient incremental delta re-ingestion.
Produces:
  - discord_messages collection  (raw messages, embedded for similarity search)
  - user_profiles collection     (per-user personality summaries)
  - channel_themes collection    (rolling topic clusters)

Usage:
  python3 riggpt-ingest.py --full          # first-time full history ingest
  python3 riggpt-ingest.py --delta         # incremental update (run via cron)
  python3 riggpt-ingest.py --profiles-only # rebuild profiles without re-ingesting
  python3 riggpt-ingest.py --status        # print collection stats

Config: edit CONFIG block below, or set environment variables.

Cron example (every 4 hours):
  0 */4 * * * /usr/bin/python3 /opt/riggpt/memory/riggpt-ingest.py --delta >> /var/log/riggpt-ingest.log 2>&1

Dependencies:
  pip3 install requests qdrant-client --break-system-packages
"""

import os, sys, json, time, hashlib, argparse, logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    UpdateStatus
)

# ── CONFIG ─────────────────────────────────────────────────────────────────
CONFIG = {
    # Discord
    "discord_token":    os.getenv("DISCORD_TOKEN",    ""),
    "discord_guild_id": os.getenv("DISCORD_GUILD_ID", ""),
    "discord_channel_id": os.getenv("DISCORD_CHANNEL_ID", ""),

    # Qdrant
    "qdrant_host": os.getenv("QDRANT_HOST", "http://192.168.40.15:6333"),

    # Ollama (for embeddings + summarisation)
    "ollama_host":       os.getenv("OLLAMA_HOST",       "http://192.168.40.15:11434"),
    "embed_model":       os.getenv("EMBED_MODEL",       "nomic-embed-text"),
    "summary_model":     os.getenv("SUMMARY_MODEL",     "qwen3:14b"),

    # Paths
    "checkpoint_file":  os.getenv("CHECKPOINT_FILE",
                                   "/home/riggpt/memory_checkpoint.json"),

    # Ingestion params
    "batch_size":         100,    # messages fetched per Discord API call (max 100)
    "embed_batch_size":   32,     # messages embedded per Ollama call
    "min_message_length": 8,      # skip very short messages (reactions, "lol", etc.)
    "profile_min_messages": 5,    # min messages before generating a user profile
    "rate_limit_delay":   0.5,    # seconds between Discord API calls
}

# Collection names
COL_MESSAGES = "discord_messages"
COL_PROFILES = "user_profiles"
COL_THEMES   = "channel_themes"
COL_THREADS  = "conversation_threads"

# Embedding dimension for nomic-embed-text
EMBED_DIM = 768

# ── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("riggpt-ingest")


# ── CHECKPOINT ─────────────────────────────────────────────────────────────
def load_checkpoint() -> dict:
    p = Path(CONFIG["checkpoint_file"])
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def save_checkpoint(data: dict):
    p = Path(CONFIG["checkpoint_file"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


# ── DISCORD API ────────────────────────────────────────────────────────────
DISCORD_BASE = "https://discord.com/api/v10"

def discord_headers() -> dict:
    return {"Authorization": f"Bot {CONFIG['discord_token']}"}


def discord_get(path: str, params: dict = None) -> dict:
    """Single Discord API GET with retry on 429."""
    url = f"{DISCORD_BASE}{path}"
    for attempt in range(5):
        r = requests.get(url, headers=discord_headers(), params=params or {}, timeout=30)
        if r.status_code == 429:
            retry_after = float(r.json().get("retry_after", 5))
            log.warning(f"Rate limited, sleeping {retry_after:.1f}s")
            time.sleep(retry_after + 0.5)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Discord API failed after retries: {path}")


def fetch_messages_page(channel_id: str, before: str = None,
                        after: str = None, limit: int = 100) -> list:
    """Fetch one page of messages. Returns list, newest-first."""
    params = {"limit": limit}
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    return discord_get(f"/channels/{channel_id}/messages", params)


def fetch_all_messages_full(channel_id: str) -> list[dict]:
    """
    Full history fetch. Paginates backwards from present to the beginning.
    Checkpoint-resumable: saves oldest_id seen so far, resumes if interrupted.
    Returns messages in chronological order (oldest first).
    """
    cp = load_checkpoint()
    oldest_seen = cp.get("oldest_message_id")  # resume point
    messages = []
    before_id = oldest_seen  # start from where we left off (or None = latest)
    page_count = 0

    log.info(f"Full fetch: channel {channel_id}" +
             (f", resuming from before {oldest_seen}" if oldest_seen else ", starting from latest"))

    while True:
        page = fetch_messages_page(channel_id, before=before_id)
        if not page:
            log.info("Reached beginning of channel history.")
            break

        messages.extend(page)
        page_count += 1
        before_id = min(m["id"] for m in page)  # oldest id on this page

        # Save checkpoint after every page so we can resume
        cp["oldest_message_id"] = before_id
        save_checkpoint(cp)

        if page_count % 10 == 0:
            log.info(f"  Fetched {len(messages)} messages ({page_count} pages)...")

        time.sleep(CONFIG["rate_limit_delay"])

    # Reverse to chronological order
    messages.sort(key=lambda m: m["id"])
    log.info(f"Full fetch complete: {len(messages)} messages")
    return messages


def fetch_delta_messages(channel_id: str) -> list[dict]:
    """
    Incremental fetch: only messages newer than last known ID.
    Returns in chronological order.
    """
    cp = load_checkpoint()
    last_id = cp.get("last_ingested_id")

    if not last_id:
        log.warning("No checkpoint found for delta. Run --full first.")
        return []

    messages = []
    after_id = last_id

    while True:
        page = fetch_messages_page(channel_id, after=after_id)
        if not page:
            break
        # after= returns oldest-first
        messages.extend(page)
        after_id = max(m["id"] for m in page)
        time.sleep(CONFIG["rate_limit_delay"])

    messages.sort(key=lambda m: m["id"])
    log.info(f"Delta fetch: {len(messages)} new messages since {last_id}")
    return messages


# ── OLLAMA ─────────────────────────────────────────────────────────────────
def ollama_embed(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of texts via Ollama /api/embed.
    Returns list of float vectors, one per input text.
    """
    embeddings = []
    batch = CONFIG["embed_batch_size"]

    for i in range(0, len(texts), batch):
        chunk = texts[i:i+batch]
        # Ollama embed accepts list input
        r = requests.post(
            f"{CONFIG['ollama_host']}/api/embed",
            json={"model": CONFIG["embed_model"], "input": chunk},
            timeout=120
        )
        r.raise_for_status()
        data = r.json()
        # Response: {"embeddings": [[...], [...]]}
        embeddings.extend(data["embeddings"])

    return embeddings


def ollama_generate(prompt: str, system: str = None,
                    max_tokens: int = 500) -> str:
    """Single generation call via Ollama /api/generate."""
    payload = {
        "model":  CONFIG["summary_model"],
        "prompt": prompt,
        "stream": False,
        "think":  False,   # Qwen3: disable chain-of-thought / thinking mode
        "options": {"num_predict": max_tokens, "temperature": 0.3},
    }
    if system:
        payload["system"] = system

    r = requests.post(
        f"{CONFIG['ollama_host']}/api/generate",
        json=payload,
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()


# ── QDRANT ─────────────────────────────────────────────────────────────────
def get_qdrant() -> QdrantClient:
    return QdrantClient(url=CONFIG["qdrant_host"], timeout=30)


def ensure_collections(client: QdrantClient):
    """Create collections if they don't exist."""
    existing = {c.name for c in client.get_collections().collections}

    if COL_MESSAGES not in existing:
        client.create_collection(
            collection_name=COL_MESSAGES,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        # Payload indexes for fast filtering
        client.create_payload_index(COL_MESSAGES, "author_hash",
                                    field_schema="keyword")
        client.create_payload_index(COL_MESSAGES, "author_username",
                                    field_schema="keyword")
        client.create_payload_index(COL_MESSAGES, "timestamp_unix",
                                    field_schema="integer")
        log.info(f"Created collection: {COL_MESSAGES}")

    if COL_PROFILES not in existing:
        client.create_collection(
            collection_name=COL_PROFILES,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        client.create_payload_index(COL_PROFILES, "author_hash",
                                    field_schema="keyword")
        log.info(f"Created collection: {COL_PROFILES}")

    if COL_THEMES not in existing:
        client.create_collection(
            collection_name=COL_THEMES,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        log.info(f"Created collection: {COL_THEMES}")

    if COL_THREADS not in existing:
        client.create_collection(
            collection_name=COL_THREADS,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        client.create_payload_index(COL_THREADS, "participant_usernames",
                                    field_schema="keyword")
        client.create_payload_index(COL_THREADS, "timestamp_unix",
                                    field_schema="integer")
        log.info(f"Created collection: {COL_THREADS}")


def author_hash(user_id: str) -> str:
    """One-way hash of Discord user ID. Never store raw IDs or usernames."""
    return hashlib.sha256(f"riggpt:{user_id}".encode()).hexdigest()[:16]


def message_point_id(message_id: str) -> int:
    """Stable integer ID for a Discord message, used as Qdrant point ID."""
    # Discord snowflake IDs are large ints — use lower 63 bits for Qdrant
    return int(message_id) & 0x7FFFFFFFFFFFFFFF


def get_existing_ids(client: QdrantClient, point_ids: list[int]) -> set[int]:
    """Return which of the given point IDs already exist in COL_MESSAGES."""
    if not point_ids:
        return set()
    results = client.retrieve(
        collection_name=COL_MESSAGES,
        ids=point_ids,
        with_payload=False,
        with_vectors=False
    )
    return {r.id for r in results}


# ── MESSAGE PROCESSING ─────────────────────────────────────────────────────
def clean_message(content: str) -> str:
    """Strip Discord markup, URLs, excessive whitespace."""
    import re
    content = re.sub(r'<[#@][^>]{1,40}>', '', content)
    content = re.sub(r'<a?:[A-Za-z0-9_]{1,32}:\d+>', '', content)
    content = re.sub(r'https?://\S+', '[link]', content)
    content = re.sub(r'\s+', ' ', content).strip()
    return content


def filter_messages(messages: list[dict]) -> list[dict]:
    """Remove bot messages, very short messages, system messages."""
    out = []
    for m in messages:
        # Skip bots
        if m.get("author", {}).get("bot"):
            continue
        # Skip system messages (joins, pins, etc.)
        if m.get("type", 0) != 0:
            continue
        content = clean_message(m.get("content", ""))
        if len(content) < CONFIG["min_message_length"]:
            continue
        m["_clean_content"] = content
        out.append(m)
    return out


def upsert_messages(client: QdrantClient, messages: list[dict]) -> int:
    """
    Embed and upsert a batch of messages into COL_MESSAGES.
    Skips messages already present. Returns count of new messages added.
    """
    if not messages:
        return 0

    # Filter and check for existing IDs
    msgs = filter_messages(messages)
    if not msgs:
        return 0

    point_ids = [message_point_id(m["id"]) for m in msgs]
    existing  = get_existing_ids(client, point_ids)
    new_msgs  = [m for m, pid in zip(msgs, point_ids) if pid not in existing]

    if not new_msgs:
        log.info("  All messages already in collection — skipping.")
        return 0

    log.info(f"  Embedding {len(new_msgs)} new messages...")
    texts  = [m["_clean_content"] for m in new_msgs]
    embeds = ollama_embed(texts)

    points = []
    for m, vec in zip(new_msgs, embeds):
        ts = m.get("timestamp", "")
        try:
            ts_unix = int(datetime.fromisoformat(
                ts.replace("Z", "+00:00")).timestamp())
        except Exception:
            ts_unix = 0

        points.append(PointStruct(
            id=message_point_id(m["id"]),
            vector=vec,
            payload={
                "message_id":       m["id"],
                "author_hash":      author_hash(m["author"]["id"]),
                "author_id":        m["author"]["id"],
                "author_username":  m["author"].get("username", ""),
                "author_display":   (m["author"].get("global_name") or
                                    m["author"].get("username", "")),
                "content":          m["_clean_content"],
                "timestamp":        ts,
                "timestamp_unix":   ts_unix,
                "has_attachment":   bool(m.get("attachments")),
            }
        ))

    # Upsert in batches of 256
    for i in range(0, len(points), 256):
        client.upsert(COL_MESSAGES, points[i:i+256])

    return len(new_msgs)


# ── PROFILE GENERATION ─────────────────────────────────────────────────────
def get_messages_for_user(client: QdrantClient,
                          ahash: str, limit: int = 200) -> list[str]:
    """Retrieve stored messages for a given author hash."""
    results = client.scroll(
        collection_name=COL_MESSAGES,
        scroll_filter=Filter(
            must=[FieldCondition(key="author_hash",
                                 match=MatchValue(value=ahash))]
        ),
        limit=limit,
        with_payload=True,
        with_vectors=False
    )
    pts      = results[0]
    msgs     = [r.payload["content"] for r in pts]
    username = pts[0].payload.get("author_username", "") if pts else ""
    display  = pts[0].payload.get("author_display", username) if pts else ""
    return msgs, username, display


def build_user_profile(ahash: str, messages: list[str],
                       username: str = "", display_name: str = "") -> dict:
    """
    Generate a personality profile for a user given their message history.
    Returns a dict with profile fields.
    """
    # Sample messages evenly if there are too many
    sample = messages
    if len(messages) > 80:
        step = len(messages) // 80
        sample = messages[::step][:80]

    messages_text = "\n".join(f"- {m}" for m in sample)

    _name = display_name or username
    _name_str = ("This person goes by the name " + _name + ". ") if _name else ""
    system = (
        "You are a behavioral analyst. Analyze the provided chat messages and "
        "produce a concise personality and communication profile. "
        + _name_str +
        "Be specific, concrete, and honest. "
        "Output only valid JSON, no markdown, no preamble, no commentary. "
        "Do not include any text before or after the JSON object. /no_think"
    )

    prompt = f"""Analyze these chat messages from a single community member and produce a profile.

MESSAGES:
{messages_text}

Produce a JSON object with exactly these fields:
{{
  "message_count": <integer>,
  "communication_style": "<2-3 sentences: how they write, vocabulary level, sentence structure>",
  "dominant_topics": ["<topic1>", "<topic2>", "<topic3>"],
  "humor_style": "<how they make jokes, what they find funny, frequency>",
  "technical_depth": "<none/casual/moderate/deep — and what subjects>",
  "recurring_themes": ["<theme or running joke>", ...],
  "emotional_register": "<their typical mood/energy in the chat>",
  "audience_role": "<lurker/commentator/instigator/expert/clown/etc — brief description>"
}}"""

    raw = ollama_generate(prompt, system=system, max_tokens=600)

    # Strip Qwen3 <think>...</think> blocks and markdown fences
    import re
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    raw = re.sub(r'^```json?\s*', '', raw.strip())
    raw = re.sub(r'```$', '', raw.strip())
    # If multiple JSON objects, take the first complete one
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)

    try:
        profile = json.loads(raw)
    except json.JSONDecodeError:
        log.warning(f"  Profile JSON parse failed for {ahash}, using fallback")
        profile = {
            "message_count": len(messages),
            "communication_style": raw[:200],
            "dominant_topics": [],
            "humor_style": "unknown",
            "technical_depth": "unknown",
            "recurring_themes": [],
            "emotional_register": "unknown",
            "audience_role": "member"
        }

    profile["author_hash"]     = ahash
    profile["author_username"] = username
    profile["display_name"]    = display_name or username
    profile["message_count"]   = len(messages)
    profile["generated_at"]    = datetime.now(timezone.utc).isoformat()
    return profile


def upsert_profile(client: QdrantClient, profile: dict):
    """Embed and upsert a user profile into COL_PROFILES."""
    # Build a rich text description to embed
    name_str   = profile.get("display_name") or profile.get("author_username", "")
    name_pfx   = (" for " + name_str) if name_str else ""
    embed_text = (
        f"Community member profile{name_pfx}. "
        f"Topics: {', '.join(profile.get('dominant_topics', []))}. "
        f"Style: {profile.get('communication_style', '')} "
        f"Humor: {profile.get('humor_style', '')} "
        f"Technical depth: {profile.get('technical_depth', '')} "
        f"Role: {profile.get('audience_role', '')} "
        f"Themes: {', '.join(profile.get('recurring_themes', []))}"
    )

    vec = ollama_embed([embed_text])[0]

    # Use a stable ID from the author hash
    point_id = int(profile["author_hash"][:15], 16) & 0x7FFFFFFFFFFFFFFF

    client.upsert(COL_PROFILES, [PointStruct(
        id=point_id,
        vector=vec,
        payload=profile
    )])


def rebuild_profiles(client: QdrantClient, only_hashes: set[str] = None):
    """
    Rebuild user profiles. If only_hashes is given, only rebuild those users.
    Otherwise rebuilds all users with enough messages.
    """
    # Get all unique author hashes from messages collection
    all_hashes = set()
    offset = None
    while True:
        results, next_offset = client.scroll(
            collection_name=COL_MESSAGES,
            offset=offset,
            limit=1000,
            with_payload=["author_hash"],
            with_vectors=False
        )
        for r in results:
            all_hashes.add(r.payload["author_hash"])
        if next_offset is None:
            break
        offset = next_offset

    target_hashes = only_hashes & all_hashes if only_hashes else all_hashes
    log.info(f"Rebuilding profiles for {len(target_hashes)} users...")

    rebuilt = 0
    for ahash in target_hashes:
        messages, username, display = get_messages_for_user(client, ahash)
        if len(messages) < CONFIG["profile_min_messages"]:
            continue
        label = display or username or ahash[:8]
        log.info(f"  Profiling {label}... ({len(messages)} messages)")
        profile = build_user_profile(ahash, messages, username, display)
        upsert_profile(client, profile)
        rebuilt += 1
        # Pace the Ollama calls
        time.sleep(0.2)

    log.info(f"Profile rebuild complete: {rebuilt} profiles updated.")


# ── CONVERSATION THREADS ───────────────────────────────────────────────────

def cluster_threads(messages: list[dict], gap_seconds: int = 300) -> list[list[dict]]:
    """
    Cluster a chronologically sorted message list into conversation threads.
    A new thread starts when:
      - A message has a message_reference (reply) that starts a new chain, OR
      - More than gap_seconds have elapsed since the last message in the thread
    Returns list of threads, each thread is a list of message dicts.
    """
    if not messages:
        return []

    threads: list[list[dict]] = []
    current: list[dict] = [messages[0]]

    # Build a lookup: message_id -> index in messages list
    id_to_idx = {m["id"]: i for i, m in enumerate(messages)}

    for msg in messages[1:]:
        last = current[-1]

        # Check time gap
        try:
            last_ts = datetime.fromisoformat(
                last.get("timestamp", "").replace("Z", "+00:00")).timestamp()
            this_ts = datetime.fromisoformat(
                msg.get("timestamp",  "").replace("Z", "+00:00")).timestamp()
            gap = this_ts - last_ts
        except Exception:
            gap = 0

        # Is this message a reply to something in the current thread?
        ref_id = (msg.get("message_reference") or {}).get("message_id")
        in_thread = ref_id and any(m["id"] == ref_id for m in current)

        if in_thread or gap <= gap_seconds:
            current.append(msg)
        else:
            if len(current) >= 2:   # only keep threads with actual back-and-forth
                threads.append(current)
            current = [msg]

    if len(current) >= 2:
        threads.append(current)

    return threads


def summarise_thread(thread: list[dict]) -> Optional[str]:
    """
    Generate a 2-3 sentence summary of a conversation thread via Ollama.
    Returns None on failure.
    """
    lines = []
    for m in thread:
        name = (m["author"].get("global_name") or
                m["author"].get("username", "someone"))
        content = clean_message(m.get("content", ""))
        if content:
            lines.append(f"{name}: {content}")

    if not lines:
        return None

    convo_text = "\n".join(lines[:40])  # cap at 40 lines for token budget

    system = (
        "You summarise online chat conversations in 1-2 sentences. "
        "Be specific — mention what was actually said, any jokes, arguments, or conclusions. "
        "Name the participants if relevant. "
        "Output only the summary sentence(s), no preamble. /no_think"
    )
    prompt = f"Summarise this conversation:\n\n{convo_text}"

    try:
        return ollama_generate(prompt, system=system, max_tokens=120)
    except Exception as e:
        log.warning(f"Thread summary failed: {e}")
        return None


def build_threads(client: QdrantClient, messages: list[dict],
                  sample_rate: float = 0.4):
    """
    Cluster messages into threads, summarise a sample, embed and upsert.
    sample_rate: fraction of threads to summarise (keep cost down on full ingest).
    Threads under 2 messages are skipped.
    """
    filtered = filter_messages(messages)
    # Need full message dicts (not just cleaned), sort chronologically
    msg_map  = {m["id"]: m for m in messages if not m.get("author", {}).get("bot")}
    clean_msgs = [msg_map[m["id"]] for m in filtered if m["id"] in msg_map]
    clean_msgs.sort(key=lambda m: m["id"])

    threads = cluster_threads(clean_msgs)
    log.info(f"  Clustered {len(clean_msgs)} messages into {len(threads)} threads")

    if not threads:
        return

    # Sample threads to summarise — always include long threads (5+ messages)
    import random
    to_summarise = [t for t in threads if len(t) >= 5]
    shorter      = [t for t in threads if len(t) < 5]
    sample_n     = max(0, int(len(shorter) * sample_rate))
    to_summarise += random.sample(shorter, min(sample_n, len(shorter)))

    log.info(f"  Summarising {len(to_summarise)} threads...")

    points = []
    for thread in to_summarise:
        summary = summarise_thread(thread)
        if not summary:
            continue

        # Participant info
        participants = []
        seen_ids = set()
        for m in thread:
            uid = m["author"]["id"]
            if uid not in seen_ids:
                seen_ids.add(uid)
                participants.append({
                    "id":       uid,
                    "username": m["author"].get("username", ""),
                    "display":  (m["author"].get("global_name") or
                                 m["author"].get("username", "")),
                })

        try:
            ts = thread[0].get("timestamp", "")
            ts_unix = int(datetime.fromisoformat(
                ts.replace("Z", "+00:00")).timestamp())
        except Exception:
            ts_unix = 0

        # Embed the summary
        vec = ollama_embed([summary])
        if not vec:
            continue
        vec = vec[0]

        # Stable point ID from first message ID
        point_id = message_point_id(thread[0]["id"])

        points.append(PointStruct(
            id=point_id,
            vector=vec,
            payload={
                "summary":               summary,
                "message_count":         len(thread),
                "participant_count":     len(participants),
                "participants":          participants,
                "participant_usernames": [p["username"] for p in participants],
                "participant_displays":  [p["display"]  for p in participants],
                "timestamp":             thread[0].get("timestamp", ""),
                "timestamp_unix":        ts_unix,
                "first_message_id":      thread[0]["id"],
            }
        ))

    # Upsert in batches
    for i in range(0, len(points), 128):
        client.upsert(COL_THREADS, points[i:i+128])

    log.info(f"  {len(points)} thread summaries stored.")


# ── CHANNEL THEMES ─────────────────────────────────────────────────────────
def rebuild_channel_themes(client: QdrantClient):
    """
    Generate a high-level channel character summary from message samples.
    Stored as a single point in COL_THEMES, replaced on each run.
    """
    log.info("Rebuilding channel themes...")

    # Sample recent messages
    results, _ = client.scroll(
        collection_name=COL_MESSAGES,
        limit=300,
        with_payload=["content", "timestamp_unix"],
        with_vectors=False
    )
    # Sort by recency, take most recent 150
    pts = sorted(results, key=lambda r: r.payload.get("timestamp_unix", 0), reverse=True)
    sample_texts = [r.payload["content"] for r in pts[:150]]

    if not sample_texts:
        log.warning("No messages found for theme analysis.")
        return

    messages_text = "\n".join(f"- {t}" for t in sample_texts)

    system = (
        "You analyze online community chat history. Be specific, honest, and observant. "
        "Output only valid JSON, no markdown, no preamble, no commentary. "
        "Do not include any text before or after the JSON object. /no_think"
    )

    prompt = f"""Analyze these recent chat messages from an online community and characterize the channel.

MESSAGES:
{messages_text}

Produce a JSON object with exactly these fields:
{{
  "community_character": "<3-4 sentences: what this community is like overall, their vibe>",
  "primary_topics": ["<topic1>", "<topic2>", "<topic3>", "<topic4>", "<topic5>"],
  "humor_culture": "<how humor works in this community: types, frequency, targets>",
  "technical_culture": "<is this a technical community, and if so in what ways>",
  "running_jokes_or_references": ["<item>", ...],
  "emotional_climate": "<overall mood, tension levels, relationship feel>",
  "distinctive_phrases": ["<phrase or term unique to this community>", ...],
  "what_they_care_about": "<what actually matters to these people, stated plainly>"
}}"""

    raw = ollama_generate(prompt, system=system, max_tokens=800)

    import re
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    raw = re.sub(r'^```json?\s*', '', raw.strip())
    raw = re.sub(r'```$', '', raw.strip())
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)

    try:
        themes = json.loads(raw)
    except json.JSONDecodeError:
        log.warning("Theme JSON parse failed, storing raw text")
        themes = {"raw": raw[:1000]}

    themes["generated_at"] = datetime.now(timezone.utc).isoformat()
    themes["sample_size"]  = len(sample_texts)

    embed_text = (
        f"Channel community profile. "
        f"Topics: {', '.join(themes.get('primary_topics', []))}. "
        f"{themes.get('community_character', '')} "
        f"Humor: {themes.get('humor_culture', '')} "
        f"Technical: {themes.get('technical_culture', '')}"
    )
    vec = ollama_embed([embed_text])[0]

    # Fixed ID for the single channel themes document
    client.upsert(COL_THEMES, [PointStruct(
        id=1,
        vector=vec,
        payload=themes
    )])
    log.info("Channel themes updated.")


# ── QUERY HELPERS (used by RigGPT at runtime) ─────────────────────────────
def query_memory(client: QdrantClient, query_text: str,
                 collection: str = COL_MESSAGES,
                 limit: int = 5) -> list[dict]:
    """Semantic search against a collection. Returns payload dicts."""
    vec = ollama_embed([query_text])[0]
    results = client.search(
        collection_name=collection,
        query_vector=vec,
        limit=limit,
        with_payload=True
    )
    return [r.payload for r in results]


# ── MAIN ───────────────────────────────────────────────────────────────────
def validate_config():
    missing = []
    for k in ("discord_token", "discord_channel_id"):
        if not CONFIG[k]:
            missing.append(k)
    if missing:
        log.error(f"Missing config: {missing}")
        log.error("Set environment variables or edit CONFIG dict in this script.")
        sys.exit(1)


def cmd_status(client: QdrantClient):
    print("\n=== RigGPT Memory Status ===")
    for col in [COL_MESSAGES, COL_PROFILES, COL_THEMES, COL_THREADS]:
        try:
            info = client.get_collection(col)
            print(f"  {col:25s} {info.points_count:>8,} points")
        except Exception:
            print(f"  {col:25s} NOT FOUND")
    cp = load_checkpoint()
    print(f"\n  Checkpoint: {CONFIG['checkpoint_file']}")
    if cp:
        print(f"  Last ingested ID:   {cp.get('last_ingested_id', 'none')}")
        print(f"  Oldest message ID:  {cp.get('oldest_message_id', 'none')}")
    print()


def cmd_full(client: QdrantClient):
    validate_config()
    ensure_collections(client)

    channel_id = CONFIG["discord_channel_id"]
    messages   = fetch_all_messages_full(channel_id)

    if not messages:
        log.info("No messages fetched.")
        return

    # Ingest in batches
    total_new = 0
    batch     = CONFIG["batch_size"]
    for i in range(0, len(messages), batch):
        chunk   = messages[i:i+batch]
        new_cnt = upsert_messages(client, chunk)
        total_new += new_cnt
        if i % (batch * 10) == 0:
            log.info(f"  Progress: {i}/{len(messages)} messages processed...")

    # Save checkpoint: newest message ID
    if messages:
        newest_id = max(m["id"] for m in messages)
        cp = load_checkpoint()
        cp["last_ingested_id"] = newest_id
        save_checkpoint(cp)

    log.info(f"Full ingest complete: {total_new} new messages stored.")

    # Rebuild everything
    log.info("Building conversation threads...")
    build_threads(client, messages, sample_rate=0.4)
    rebuild_profiles(client)
    rebuild_channel_themes(client)


def cmd_delta(client: QdrantClient):
    validate_config()
    ensure_collections(client)

    channel_id = CONFIG["discord_channel_id"]
    messages   = fetch_delta_messages(channel_id)

    if not messages:
        log.info("No new messages. Nothing to do.")
        return

    new_cnt = upsert_messages(client, messages)

    # Track which users got new messages
    new_author_hashes = {
        author_hash(m["author"]["id"])
        for m in filter_messages(messages)
    }

    # Update checkpoint
    if messages:
        newest_id = max(m["id"] for m in messages)
        cp = load_checkpoint()
        cp["last_ingested_id"] = newest_id
        save_checkpoint(cp)

    log.info(f"Delta: {new_cnt} new messages, {len(new_author_hashes)} users with new activity.")

    # Rebuild threads for the new messages (sample_rate=1.0 — delta is small)
    if messages:
        log.info("Building conversation threads for delta...")
        build_threads(client, messages, sample_rate=1.0)

    # Only rebuild profiles for active users
    rebuild_profiles(client, only_hashes=new_author_hashes)

    # Rebuild channel themes (fast — just re-samples recent messages)
    rebuild_channel_themes(client)


def cmd_profiles_only(client: QdrantClient):
    ensure_collections(client)
    rebuild_profiles(client)
    rebuild_channel_themes(client)


def cmd_threads_only(client: QdrantClient):
    """Re-summarise threads from messages already in Qdrant.
    Scrolls all stored messages, re-clusters and re-summarises.
    """
    ensure_collections(client)
    log.info("Loading all stored messages for thread clustering...")

    # Reconstruct minimal message dicts from stored payloads
    raw_msgs = []
    offset   = None
    while True:
        results, next_offset = client.scroll(
            collection_name=COL_MESSAGES,
            offset=offset,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        for r in results:
            p = r.payload
            raw_msgs.append({
                "id":        p.get("message_id", str(r.id)),
                "content":   p.get("content", ""),
                "timestamp": p.get("timestamp", ""),
                "author": {
                    "id":          p.get("author_id", ""),
                    "username":    p.get("author_username", ""),
                    "global_name": p.get("author_display", ""),
                    "bot":         False,
                },
                "_clean_content": p.get("content", ""),
            })
        if next_offset is None:
            break
        offset = next_offset

    log.info(f"Loaded {len(raw_msgs)} messages. Building threads...")
    build_threads(client, raw_msgs, sample_rate=0.4)


# ── ENTRY POINT ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RigGPT Discord memory ingestion")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--full",          action="store_true",
                     help="Full history ingest (first run or complete rebuild)")
    grp.add_argument("--delta",         action="store_true",
                     help="Incremental update since last run")
    grp.add_argument("--profiles-only", action="store_true",
                     help="Rebuild profiles without re-ingesting messages")
    grp.add_argument("--threads-only",  action="store_true",
                     help="Rebuild conversation thread summaries from stored messages")
    grp.add_argument("--status",        action="store_true",
                     help="Print collection statistics")
    args = parser.parse_args()

    client = get_qdrant()

    if args.status:
        cmd_status(client)
    elif args.full:
        log.info("=== FULL INGEST ===")
        cmd_full(client)
    elif args.delta:
        log.info("=== DELTA UPDATE ===")
        cmd_delta(client)
    elif args.profiles_only:
        log.info("=== PROFILES REBUILD ===")
        cmd_profiles_only(client)
    elif args.threads_only:
        log.info("=== THREADS REBUILD ===")
        cmd_threads_only(client)
