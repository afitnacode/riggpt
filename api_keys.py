"""
api_keys.py - API Integration Configuration Manager
IC-7610 Voice Agent

Manages API keys and provider configurations for third-party TTS and other
integrations. Keys are stored in a JSON file on disk with optional obfuscation.
New providers can be added by appending to PROVIDER_REGISTRY.

Storage: /home/riggpt/api_keys.json
Format:  { "provider_id": { "field_id": "value", ... }, ... }

Security note: Keys are stored in plaintext in the JSON file.
Protect the file with filesystem permissions (chmod 600).
This is appropriate for a self-hosted amateur radio automation tool.
If you need stronger protection, set RIGGPT_KEY_FILE to a path on
an encrypted volume, or provide keys via environment variables which
take precedence over stored values.
"""

import os
import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Any

logger = logging.getLogger('ic7610.apikeys')


def _ascii(s) -> str:
    """Strip non-ASCII from external API responses so Flask latin-1
    encoder never chokes on Unicode in error messages."""
    return str(s).encode('ascii', errors='replace').decode('ascii')



KEY_FILE = os.environ.get(
    'RIGGPT_KEY_FILE',
    '/home/riggpt/api_keys.json'
)

# ─────────────────────────────────────────────────────────────
# Provider Registry
#
# Each entry defines a TTS/API provider. Fields are rendered as
# form inputs in the Settings -> API Integrations panel.
#
# Field types:
#   password  - masked input, stored encrypted-at-rest (obfuscated)
#   text      - plain text input
#   select    - dropdown; include 'options': [{'value':..,'label':..}]
#   url       - URL input with validation
#
# env_override: if set, this env var takes precedence over stored value
# test_fn:      callable(config_dict) -> (bool, str) - tests connectivity
# ─────────────────────────────────────────────────────────────

def _test_elevenlabs(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.elevenlabs.io/v1/user',
            headers={'xi-api-key': key},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            tier  = data.get('subscription', {}).get('tier', 'unknown')
            chars = data.get('subscription', {}).get('character_count', '?')
            limit = data.get('subscription', {}).get('character_limit', '?')
            return True, _ascii(f'Connected - tier: {tier}, chars used: {chars:,}/{limit:,}')
        elif r.status_code == 401:
            return False, 'Invalid API key (401 Unauthorized)'
        else:
            return False, f'Unexpected response: HTTP {r.status_code}'
    except requests.Timeout:
        return False, 'Connection timed out'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_speechify(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        # Speechify API v1 - list available voices as connectivity check
        r = requests.get(
            'https://api.sws.speechify.com/v1/voices',
            headers={
                'Authorization': f'Bearer {key}',
                'Accept':        'application/json',
            },
            timeout=8
        )
        if r.status_code == 200:
            data   = r.json()
            voices = data if isinstance(data, list) else data.get('voices', [])
            return True, _ascii(f'Connected - {len(voices)} voice(s) available')
        elif r.status_code == 401:
            return False, 'Invalid API key (401 Unauthorized)'
        elif r.status_code == 403:
            return False, 'Access denied - check API key permissions'
        else:
            return False, f'Unexpected response: HTTP {r.status_code}'
    except requests.Timeout:
        return False, 'Connection timed out'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_openai(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {key}'},
            timeout=8
        )
        if r.status_code == 200:
            models = [m['id'] for m in r.json().get('data', []) if 'tts' in m['id']]
            return True, _ascii(f'Connected - TTS models: {", ".join(models) or "none found"}')
        elif r.status_code == 401:
            return False, 'Invalid API key'
        else:
            return False, f'HTTP {r.status_code}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_azure(cfg: dict) -> tuple[bool, str]:
    key    = cfg.get('api_key', '').strip()
    region = cfg.get('region',  '').strip()
    if not key or not region:
        return False, 'API key and region are both required'
    try:
        r = requests.post(
            f'https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            headers={'Ocp-Apim-Subscription-Key': key},
            timeout=8
        )
        if r.status_code == 200:
            return True, _ascii(f'Connected - region: {region}')
        elif r.status_code == 401:
            return False, 'Invalid key or wrong region'
        else:
            return False, f'HTTP {r.status_code}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')



def _test_gemini(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://generativelanguage.googleapis.com/v1beta/models',
            params={'key': key},
            timeout=8
        )
        if r.status_code == 200:
            models = [m.get('name','').split('/')[-1] for m in r.json().get('models',[])
                      if 'generateContent' in m.get('supportedGenerationMethods',[])]
            return True, _ascii(f'Connected - {len(models)} generative model(s): {", ".join(models[:4])}')
        elif r.status_code == 400:
            return False, 'Invalid API key format'
        elif r.status_code == 403:
            return False, 'Invalid API key or API not enabled'
        else:
            return False, f'HTTP {r.status_code}: {r.text[:80]}'
    except requests.Timeout:
        return False, 'Connection timed out'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_openai_chat(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {key}'},
            timeout=8
        )
        if r.status_code == 200:
            models = [m['id'] for m in r.json().get('data', [])
                      if 'gpt' in m['id'] and 'instruct' not in m['id']]
            chat_models = [m for m in models if any(x in m for x in ['gpt-4o','gpt-4','gpt-3.5'])]
            return True, _ascii(f'Connected - chat models: {", ".join(sorted(set(chat_models))[:5])}')
        elif r.status_code == 401:
            return False, 'Invalid API key'
        else:
            return False, f'HTTP {r.status_code}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_anthropic(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.anthropic.com/v1/models',
            headers={
                'x-api-key':         key,
                'anthropic-version': '2023-06-01',
            },
            timeout=8
        )
        if r.status_code == 200:
            models = [m.get('id','') for m in r.json().get('data',[])]
            return True, _ascii(f'Connected - {len(models)} model(s): {", ".join(models[:3])}')
        elif r.status_code == 401:
            return False, 'Invalid API key'
        else:
            return False, f'HTTP {r.status_code}: {r.text[:80]}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_mistral(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.mistral.ai/v1/models',
            headers={'Authorization': f'Bearer {key}'},
            timeout=8
        )
        if r.status_code == 200:
            models = [m.get('id','') for m in r.json().get('data',[])]
            return True, _ascii(f'Connected - {len(models)} model(s): {", ".join(models[:4])}')
        elif r.status_code == 401:
            return False, 'Invalid API key'
        else:
            return False, f'HTTP {r.status_code}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_discord_ctrl(cfg: dict) -> tuple[bool, str]:
    token      = cfg.get('bot_token', '').strip()
    guild_id   = cfg.get('guild_id', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    if not token:
        return False, 'No bot token configured'
    try:
        r = requests.get(
            'https://discord.com/api/v10/users/@me',
            headers={'Authorization': f'Bot {token}'},
            timeout=8,
        )
        if r.status_code == 401:
            return False, 'Invalid bot token'
        if r.status_code != 200:
            return False, _ascii(f'HTTP {r.status_code}: {r.text[:120]}')
        bot_name = _ascii(r.json().get('username', 'unknown'))
        if channel_id:
            rc = requests.get(
                f'https://discord.com/api/v10/channels/{channel_id}',
                headers={'Authorization': f'Bot {token}'},
                timeout=8,
            )
            if rc.status_code == 404:
                return False, _ascii(f'Bot "{bot_name}" OK but channel {channel_id} not found')
            if rc.status_code == 403:
                return False, _ascii(f'Bot "{bot_name}" cannot read channel {channel_id} -- check permissions')
            if rc.status_code == 200:
                ch_name = _ascii('#' + rc.json().get('name', channel_id))
                return True, _ascii(f'Bot "{bot_name}" connected -- control channel: {ch_name}. Post !chaos to test.')
        return True, _ascii(f'Bot "{bot_name}" token valid (no channel ID to verify)')
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_fastkoko(cfg: dict) -> tuple[bool, str]:
    url = cfg.get('url', '').strip().rstrip('/')
    if not url:
        return False, 'No server URL configured'
    try:
        r = requests.get(f'{url}/v1/audio/voices', timeout=6)
        if r.status_code != 200:
            return False, _ascii(f'HTTP {r.status_code}: {r.text[:120]}')
        voices = r.json().get('voices', [])
        if not voices:
            return False, 'Server responded but returned no voices'
        return True, _ascii(f'OK -- {len(voices)} voices available (e.g. {voices[0]})')
    except requests.exceptions.ConnectionError:
        return False, _ascii(f'Cannot connect to {url} -- is FastKoko running?')
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_discord(cfg: dict) -> tuple[bool, str]:
    token      = cfg.get('bot_token', '').strip()
    guild_id   = cfg.get('guild_id', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    if not token:
        return False, 'No bot token configured'
    try:
        # Verify token by fetching bot identity
        r = requests.get(
            'https://discord.com/api/v10/users/@me',
            headers={'Authorization': f'Bot {token}'},
            timeout=8,
        )
        if r.status_code == 401:
            return False, 'Invalid bot token'
        if r.status_code != 200:
            return False, _ascii(f'HTTP {r.status_code}: {r.text[:120]}')
        bot = r.json()
        bot_name = _ascii(bot.get('username', 'unknown'))

        # If guild_id provided, verify bot is a member of that server
        if guild_id:
            rg = requests.get(
                f'https://discord.com/api/v10/guilds/{guild_id}',
                headers={'Authorization': f'Bot {token}'},
                timeout=8,
            )
            if rg.status_code in (403, 404):
                return False, _ascii(
                    f'Bot "{bot_name}" authenticated OK but is not a member of server {guild_id}. '
                    f'Invite the bot first: discord.com/developers/applications -> '
                    f'Your App -> OAuth2 -> URL Generator -> scope: bot, permission: Read Messages -> '
                    f'open the generated URL and add the bot to your server'
                )
            if rg.status_code == 200:
                guild_name = _ascii(rg.json().get('name', guild_id))
            else:
                guild_name = guild_id

            # If channel_id provided, verify bot can read that channel
            if channel_id:
                rc = requests.get(
                    f'https://discord.com/api/v10/channels/{channel_id}',
                    headers={'Authorization': f'Bot {token}'},
                    timeout=8,
                )
                if rc.status_code == 403:
                    return False, _ascii(f'Bot lacks permission to read channel {channel_id}')
                if rc.status_code == 404:
                    return False, _ascii(f'Channel {channel_id} not found')
                if rc.status_code == 200:
                    ch_name = _ascii(rc.json().get('name', channel_id))
                    return True, _ascii(f'Connected - bot: {bot_name}, server: {guild_name}, channel: #{ch_name}')

            return True, _ascii(f'Connected - bot: {bot_name}, server: {guild_name} (no channel set)')
        return True, _ascii(f'Connected - bot: {bot_name} (no server/channel configured yet)')
    except Exception as e:
        return False, _ascii(f'Error: {e}')


def _test_groq(cfg: dict) -> tuple[bool, str]:
    key = cfg.get('api_key', '').strip()
    if not key:
        return False, 'No API key configured'
    try:
        r = requests.get(
            'https://api.groq.com/openai/v1/models',
            headers={'Authorization': f'Bearer {key}'},
            timeout=8
        )
        if r.status_code == 200:
            models = [m.get('id','') for m in r.json().get('data',[])]
            return True, _ascii(f'Connected - {len(models)} model(s): {", ".join(models[:4])}')
        elif r.status_code == 401:
            return False, 'Invalid API key'
        else:
            return False, f'HTTP {r.status_code}'
    except Exception as e:
        return False, _ascii(f'Error: {e}')

# ── The registry ─────────────────────────────────────────────
PROVIDER_REGISTRY: list[dict] = [
    {
        'id':          'elevenlabs',
        'name':        'ElevenLabs',
        'description': 'High-quality neural TTS with custom voice cloning. Requires an ElevenLabs account.',
        'docs_url':    'https://elevenlabs.io/docs/api-reference/text-to-speech',
        'category':    'tts',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'sk-...',
                'required':    True,
                'env_override': 'ELEVENLABS_API_KEY',
                'help':        'Found at elevenlabs.io -> Profile -> API Keys',
            },
        ],
        'test_fn': _test_elevenlabs,
    },
    {
        'id':          'speechify',
        'name':        'Speechify',
        'description': 'Natural-sounding TTS with a large voice library. Requires a Speechify API subscription.',
        'docs_url':    'https://docs.sws.speechify.com',
        'category':    'tts',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'Bearer token from Speechify dashboard',
                'required':    True,
                'env_override': 'SPEECHIFY_API_KEY',
                'help':        'Found at app.speechify.com -> API -> Access Token',
            },
            {
                'id':          'default_voice',
                'label':       'Default Voice ID',
                'type':        'text',
                'placeholder': 'henry',
                'required':    False,
                'help':        'Voice ID from Speechify voice library. Leave blank to use the API default.',
            },
        ],
        'test_fn': _test_speechify,
    },
    {
        'id':          'openai',
        'name':        'OpenAI TTS',
        'description': 'OpenAI TTS-1 and TTS-1-HD models (Alloy, Echo, Fable, Onyx, Nova, Shimmer voices).',
        'docs_url':    'https://platform.openai.com/docs/guides/text-to-speech',
        'category':    'tts',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'sk-...',
                'required':    True,
                'env_override': 'OPENAI_API_KEY',
                'help':        'Found at platform.openai.com -> API Keys',
            },
            {
                'id':          'model',
                'label':       'Model',
                'type':        'select',
                'default':     'tts-1',
                'required':    False,
                'options': [
                    {'value': 'tts-1',    'label': 'TTS-1 (faster, lower latency)'},
                    {'value': 'tts-1-hd', 'label': 'TTS-1-HD (higher quality)'},
                ],
                'help': 'TTS-1-HD produces better audio but costs more per character.',
            },
            {
                'id':          'default_voice',
                'label':       'Default Voice',
                'type':        'select',
                'default':     'onyx',
                'required':    False,
                'options': [
                    {'value': 'alloy',   'label': 'Alloy - balanced, neutral'},
                    {'value': 'echo',    'label': 'Echo - clear, direct'},
                    {'value': 'fable',   'label': 'Fable - warm, narrative'},
                    {'value': 'onyx',    'label': 'Onyx - deep, authoritative'},
                    {'value': 'nova',    'label': 'Nova - bright, energetic'},
                    {'value': 'shimmer', 'label': 'Shimmer - soft, gentle'},
                ],
                'help': 'Default voice when none is specified in a transmission.',
            },
        ],
        'test_fn': _test_openai,
    },
    {
        'id':          'azure_tts',
        'name':        'Azure Cognitive Services TTS',
        'description': 'Microsoft Azure neural TTS with 400+ voices in 140+ languages.',
        'docs_url':    'https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech',
        'category':    'tts',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'Subscription Key',
                'type':        'password',
                'placeholder': '32-character hex key',
                'required':    True,
                'env_override': 'AZURE_TTS_KEY',
                'help':        'Azure portal -> Speech resource -> Keys and Endpoint -> KEY 1',
            },
            {
                'id':          'region',
                'label':       'Region',
                'type':        'text',
                'placeholder': 'eastus',
                'required':    True,
                'env_override': 'AZURE_TTS_REGION',
                'help':        'Azure region slug, e.g. eastus, westeurope, australiaeast',
            },
            {
                'id':          'default_voice',
                'label':       'Default Voice Name',
                'type':        'text',
                'placeholder': 'en-US-GuyNeural',
                'required':    False,
                'help':        'Full voice name from Azure voice gallery, e.g. en-US-JennyNeural',
            },
        ],
        'test_fn': _test_azure,
    },
    {
        'id':          'gemini',
        'name':        'Google Gemini',
        'description': 'Google Gemini generative AI models (Gemini 1.5 Flash, Pro, Ultra). Use for AI chat, generation, and analysis features.',
        'docs_url':    'https://ai.google.dev/docs',
        'category':    'llm',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'AIza...',
                'required':    True,
                'env_override': 'GEMINI_API_KEY',
                'help':        'Google AI Studio -> Get API Key (aistudio.google.com)',
            },
            {
                'id':          'default_model',
                'label':       'Default Model',
                'type':        'select',
                'default':     'gemini-1.5-flash',
                'required':    False,
                'options': [
                    {'value': 'gemini-1.5-flash',   'label': 'Gemini 1.5 Flash (fast, efficient)'},
                    {'value': 'gemini-1.5-pro',     'label': 'Gemini 1.5 Pro (powerful)'},
                    {'value': 'gemini-2.0-flash',   'label': 'Gemini 2.0 Flash (latest fast)'},
                ],
                'help': 'Model used when Gemini is selected for AI generation features.',
            },
        ],
        'test_fn': _test_gemini,
    },
    {
        'id':          'openai_chat',
        'name':        'OpenAI ChatGPT',
        'description': 'OpenAI GPT-4o and GPT-4 chat models for AI generation, debate, and analysis features.',
        'docs_url':    'https://platform.openai.com/docs/guides/chat-completions',
        'category':    'llm',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'sk-...',
                'required':    True,
                'env_override': 'OPENAI_API_KEY',
                'help':        'platform.openai.com -> API Keys. Same key as OpenAI TTS if already set.',
            },
            {
                'id':          'default_model',
                'label':       'Default Model',
                'type':        'select',
                'default':     'gpt-4o-mini',
                'required':    False,
                'options': [
                    {'value': 'gpt-4o-mini', 'label': 'GPT-4o Mini (fast, cheap)'},
                    {'value': 'gpt-4o',      'label': 'GPT-4o (powerful)'},
                    {'value': 'gpt-4-turbo', 'label': 'GPT-4 Turbo'},
                    {'value': 'gpt-3.5-turbo', 'label': 'GPT-3.5 Turbo (cheapest)'},
                ],
                'help': 'Model used when OpenAI Chat is selected for AI generation features.',
            },
        ],
        'test_fn': _test_openai_chat,
    },
    {
        'id':          'anthropic',
        'name':        'Anthropic Claude',
        'description': 'Anthropic Claude models for high-quality AI generation, analysis, and creative content.',
        'docs_url':    'https://docs.anthropic.com/en/api',
        'category':    'llm',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'sk-ant-...',
                'required':    True,
                'env_override': 'ANTHROPIC_API_KEY',
                'help':        'console.anthropic.com -> API Keys',
            },
            {
                'id':          'default_model',
                'label':       'Default Model',
                'type':        'select',
                'default':     'claude-3-5-haiku-latest',
                'required':    False,
                'options': [
                    {'value': 'claude-3-5-haiku-latest',  'label': 'Claude 3.5 Haiku (fast, efficient)'},
                    {'value': 'claude-3-5-sonnet-latest', 'label': 'Claude 3.5 Sonnet (powerful)'},
                    {'value': 'claude-3-opus-latest',     'label': 'Claude 3 Opus (most capable)'},
                ],
                'help': 'Model used when Claude is selected for AI generation features.',
            },
        ],
        'test_fn': _test_anthropic,
    },
    {
        'id':          'mistral',
        'name':        'Mistral AI',
        'description': 'Mistral open and commercial LLMs. Good balance of speed and capability.',
        'docs_url':    'https://docs.mistral.ai',
        'category':    'llm',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'your-mistral-key',
                'required':    True,
                'env_override': 'MISTRAL_API_KEY',
                'help':        'console.mistral.ai -> API Keys',
            },
            {
                'id':          'default_model',
                'label':       'Default Model',
                'type':        'select',
                'default':     'mistral-small-latest',
                'required':    False,
                'options': [
                    {'value': 'mistral-small-latest',  'label': 'Mistral Small (fast, cheap)'},
                    {'value': 'mistral-medium-latest', 'label': 'Mistral Medium'},
                    {'value': 'mistral-large-latest',  'label': 'Mistral Large (most capable)'},
                ],
                'help': 'Model used when Mistral is selected for AI generation.',
            },
        ],
        'test_fn': _test_mistral,
    },
    {
        'id':          'groq',
        'name':        'Groq (Fast Inference)',
        'description': 'Groq LPU inference - extremely fast responses for Llama 3, Mixtral, and Gemma. Free tier available.',
        'docs_url':    'https://console.groq.com/docs/openai',
        'category':    'llm',
        'enabled':     True,
        'fields': [
            {
                'id':          'api_key',
                'label':       'API Key',
                'type':        'password',
                'placeholder': 'gsk_...',
                'required':    True,
                'env_override': 'GROQ_API_KEY',
                'help':        'console.groq.com -> API Keys (free tier available)',
            },
            {
                'id':          'default_model',
                'label':       'Default Model',
                'type':        'select',
                'default':     'llama-3.3-70b-versatile',
                'required':    False,
                'options': [
                    {'value': 'llama-3.3-70b-versatile', 'label': 'Llama 3.3 70B Versatile'},
                    {'value': 'llama-3.1-8b-instant',    'label': 'Llama 3.1 8B Instant (fastest)'},
                    {'value': 'mixtral-8x7b-32768',      'label': 'Mixtral 8x7B'},
                    {'value': 'gemma2-9b-it',            'label': 'Gemma 2 9B'},
                ],
                'help': 'Groq provides very fast inference - great for real-time debate and generation.',
            },
        ],
        'test_fn': _test_groq,
    },
    {
        'id':          'discord',
        'name':        'Discord',
        'description': 'Monitor a Discord channel and feed messages into Acid Trip agent context. Requires a bot token with MESSAGE_CONTENT intent enabled.',
        'docs_url':    'https://discord.com/developers/docs/intro',
        'category':    'integration',
        'enabled':     True,
        'fields': [
            {
                'id':          'bot_token',
                'label':       'Bot Token',
                'type':        'password',
                'placeholder': 'MTxxxxxxxxxxxxxxxxxxxxxxxx.Gxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'required':    True,
                'env_override': 'DISCORD_BOT_TOKEN',
                'help':        'discord.com/developers/applications -> Your App -> Bot -> Token',
            },
            {
                'id':          'guild_id',
                'label':       'Server (Guild) ID',
                'type':        'text',
                'placeholder': '123456789012345678',
                'required':    True,
                'env_override': 'DISCORD_GUILD_ID',
                'help':        'Enable Developer Mode in Discord settings, then right-click server name -> Copy Server ID',
            },
            {
                'id':          'channel_id',
                'label':       'Channel ID',
                'type':        'text',
                'placeholder': '123456789012345678',
                'required':    True,
                'env_override': 'DISCORD_CHANNEL_ID',
                'help':        'Right-click channel name -> Copy Channel ID (requires Developer Mode)',
            },
            {
                'id':          'poll_interval',
                'label':       'Poll Interval (sec)',
                'type':        'text',
                'placeholder': '10',
                'required':    False,
                'default':     '10',
                'help':        'How often to fetch new messages from the channel (5-300 seconds)',
            },
            {
                'id':          'max_messages',
                'label':       'Messages to Fetch',
                'type':        'text',
                'placeholder': '5',
                'required':    False,
                'default':     '5',
                'help':        'Number of recent messages to retrieve per poll (1-20)',
            },
        ],
        'test_fn': _test_discord,
    },
    {
        'id':          'fastkoko',
        'name':        'FastKoko (Local)',
        'description': 'Local Kokoro TTS server (FastAPI/OpenAI-compatible). Runs on your LAN — no API key required, just the server URL.',
        'docs_url':    'https://github.com/remsky/Kokoro-FastAPI',
        'category':    'integration',
        'enabled':     True,
        'fields': [
            {
                'id':          'url',
                'label':       'Server URL',
                'type':        'text',
                'placeholder': 'http://192.168.40.15:8880',
                'required':    True,
                'env_override': 'FASTKOKO_URL',
                'help':        'Base URL of your FastKoko server — no trailing slash. Voices fetched from /v1/audio/voices, synthesis via /v1/audio/speech.',
            },
            {
                'id':          'default_voice',
                'label':       'Default Voice',
                'type':        'text',
                'placeholder': 'af_sarah',
                'required':    False,
                'env_override': 'FASTKOKO_VOICE',
                'help':        'Default voice ID used when no voice is specified. Leave blank to use af_sarah.',
            },
        ],
        'test_fn': _test_fastkoko,
    },
    {
        'id':          'discord_ctrl',
        'name':        'Discord Control Channel',
        'description': 'A separate Discord server/channel for operator commands. Uses the same bot token as the chaos monitor, but watches a different channel for !commands that control the running trip.',
        'docs_url':    '/trip/commands',
        'category':    'integration',
        'enabled':     True,
        'fields': [
            {
                'id':          'bot_token',
                'label':       'Bot Token',
                'type':        'password',
                'placeholder': 'MTxxxxxxxxxxxxxxxxxxxxxxxx.Gxxxxx.xxxxxxxxxxxxxxxxxx',
                'required':    True,
                'env_override': 'DISCORD_CTRL_BOT_TOKEN',
                'help':        'Can be the same token as the chaos monitor bot — the bot just needs to be in the control server.',
            },
            {
                'id':          'guild_id',
                'label':       'Control Server (Guild) ID',
                'type':        'text',
                'placeholder': '123456789012345678',
                'required':    True,
                'env_override': 'DISCORD_CTRL_GUILD_ID',
                'help':        'Right-click server name in Discord (Developer Mode on) -> Copy Server ID',
            },
            {
                'id':          'channel_id',
                'label':       'Control Channel ID',
                'type':        'text',
                'placeholder': '123456789012345678',
                'required':    True,
                'env_override': 'DISCORD_CTRL_CHANNEL_ID',
                'help':        'Right-click the control channel -> Copy Channel ID',
            },
            {
                'id':          'poll_interval',
                'label':       'Poll Interval (s)',
                'type':        'number',
                'placeholder': '10',
                'required':    False,
                'env_override': 'DISCORD_CTRL_POLL_INTERVAL',
                'help':        '5–300 seconds. Commands are processed within one poll interval.',
            },
        ],
        'test_fn': _test_discord_ctrl,
    },
]

# Index by id for O(1) lookup
_REGISTRY_BY_ID: dict[str, dict] = {p['id']: p for p in PROVIDER_REGISTRY}


# ─────────────────────────────────────────────────────────────
# Key Storage
# ─────────────────────────────────────────────────────────────

def _obfuscate(value: str) -> str:
    """Light XOR obfuscation - not encryption, just avoids plaintext in logs."""
    key = b'ic7610radioagent'
    enc = bytearray()
    for i, c in enumerate(value.encode()):
        enc.append(c ^ key[i % len(key)])
    return enc.hex()


def _deobfuscate(value: str) -> str:
    try:
        enc = bytes.fromhex(value)
        key = b'ic7610radioagent'
        return bytes(c ^ key[i % len(key)] for i, c in enumerate(enc)).decode()
    except Exception:
        return value  # already plaintext (legacy)


def load_config() -> dict:
    """Load all provider configs from disk."""
    try:
        if Path(KEY_FILE).exists():
            with open(KEY_FILE) as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load API key config: {e}")
    return {}


def save_config(config: dict) -> bool:
    """Save all provider configs to disk."""
    try:
        Path(KEY_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(KEY_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(KEY_FILE, 0o600)  # owner read/write only
        return True
    except Exception as e:
        logger.error(f"Could not save API key config: {e}")
        return False


def get_provider_config(provider_id: str) -> dict:
    """
    Get effective config for a provider, merging:
      1. Stored values from disk
      2. Environment variable overrides (highest priority)

    Password fields are deobfuscated before returning.
    """
    stored = load_config().get(provider_id, {})
    provider = _REGISTRY_BY_ID.get(provider_id, {})
    result   = {}

    for field in provider.get('fields', []):
        fid      = field['id']
        env_var  = field.get('env_override')
        stored_v = stored.get(fid, '')

        # Deobfuscate password fields
        if field['type'] == 'password' and stored_v:
            stored_v = _deobfuscate(stored_v)

        # Env override wins
        if env_var and os.environ.get(env_var, '').strip():
            result[fid] = os.environ[env_var].strip()
            result[f'_{fid}_source'] = 'env'
        elif stored_v:
            result[fid] = stored_v
            result[f'_{fid}_source'] = 'stored'
        else:
            result[fid] = field.get('default', '')
            result[f'_{fid}_source'] = 'default'

    return result


def get_key(provider_id: str, field_id: str = 'api_key') -> str:
    """Convenience: get a single field value for a provider."""
    return get_provider_config(provider_id).get(field_id, '')


def set_provider_config(provider_id: str, field_values: dict) -> bool:
    """
    Save field values for a provider.
    Password fields are obfuscated before storage.
    """
    provider = _REGISTRY_BY_ID.get(provider_id)
    if not provider:
        logger.warning(f"Unknown provider: {provider_id}")
        return False

    config = load_config()
    if provider_id not in config:
        config[provider_id] = {}

    for field in provider['fields']:
        fid = field['id']
        if fid in field_values:
            val = str(field_values[fid]).strip()
            if field['type'] == 'password' and val:
                config[provider_id][fid] = _obfuscate(val)
            else:
                config[provider_id][fid] = val

    return save_config(config)


def delete_provider_config(provider_id: str) -> bool:
    """Remove all stored config for a provider."""
    config = load_config()
    if provider_id in config:
        del config[provider_id]
        return save_config(config)
    return True


def mask_value(value: str) -> str:
    """Return a masked version of a secret for display."""
    if not value:
        return ''
    if len(value) <= 8:
        return '*' * len(value)
    return value[:4] + '*' * (len(value) - 8) + value[-4:]


def get_registry_for_api() -> list[dict]:
    """
    Return provider registry in a form safe for the API -
    includes field definitions but never actual key values.
    Includes configured/unconfigured status and source info.
    """
    result   = []
    config   = load_config()

    for provider in PROVIDER_REGISTRY:
        pid      = provider['id']
        stored   = config.get(pid, {})
        cfg      = get_provider_config(pid)

        fields_out = []
        for field in provider['fields']:
            fid       = field['id']
            raw_val   = cfg.get(fid, '')
            source    = cfg.get(f'_{fid}_source', 'default')
            has_value = bool(raw_val and raw_val != field.get('default', ''))

            f_out = {
                'id':          fid,
                'label':       field['label'],
                'type':        field['type'],
                'placeholder': field.get('placeholder', ''),
                'required':    field.get('required', False),
                'help':        field.get('help', ''),
                'has_value':   has_value,
                'source':      source,       # 'env', 'stored', or 'default'
                'masked':      mask_value(raw_val) if field['type'] == 'password' else (raw_val if not field.get('sensitive') else mask_value(raw_val)),
            }
            if field['type'] == 'select':
                f_out['options'] = field.get('options', [])
                f_out['current'] = raw_val or field.get('default', '')
            fields_out.append(f_out)

        # Overall configured status: all required fields have values
        required_fields = [f for f in provider['fields'] if f.get('required')]
        all_required_set = all(
            bool(cfg.get(f['id'], '').strip())
            for f in required_fields
        )

        result.append({
            'id':           pid,
            'name':         provider['name'],
            'description':  provider['description'],
            'docs_url':     provider.get('docs_url', ''),
            'category':     provider.get('category', 'other'),
            'enabled':      provider.get('enabled', True),
            'configured':   all_required_set,
            'fields':       fields_out,
        })

    return result


def test_provider(provider_id: str) -> tuple[bool, str]:
    """Run the provider's test function with current config."""
    provider = _REGISTRY_BY_ID.get(provider_id)
    if not provider:
        return False, f'Unknown provider: {provider_id}'
    test_fn = provider.get('test_fn')
    if not test_fn:
        return False, 'No test function defined for this provider'
    cfg = get_provider_config(provider_id)
    try:
        return test_fn(cfg)
    except Exception as e:
        return False, f'Test error: {e}'
