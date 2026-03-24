"""
TaxGenie AI - Memory Store Service
Redis-based session memory and result caching.
"""

import json
import logging
from typing import Optional, Any
from config import settings

logger = logging.getLogger(__name__)

# Try to import redis; fail gracefully in dev without Redis
try:
    import redis
    _redis_client: Optional[redis.Redis] = redis.from_url(
        settings.REDIS_URL, decode_responses=True
    )
    _redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis not available, using in-memory fallback: {e}")
    _redis_client = None
    REDIS_AVAILABLE = False

# In-memory fallback store
_memory_store: dict[str, str] = {}


def _set(key: str, value: str, ttl: int = settings.REDIS_SESSION_TTL) -> None:
    if _redis_client and REDIS_AVAILABLE:
        try:
            _redis_client.setex(key, ttl, value)
            return
        except Exception:
            pass
    _memory_store[key] = value


def _get(key: str) -> Optional[str]:
    if _redis_client and REDIS_AVAILABLE:
        try:
            return _redis_client.get(key)
        except Exception:
            pass
    return _memory_store.get(key)


def _delete(key: str) -> None:
    if _redis_client and REDIS_AVAILABLE:
        try:
            _redis_client.delete(key)
            return
        except Exception:
            pass
    _memory_store.pop(key, None)


# ─── Public API ───────────────────────────────────────────────────────────────

def save_session(session_id: str, data: Any) -> None:
    """Persist session data (analysis results, parsed form, etc.)."""
    payload = json.dumps(data, default=str)
    _set(f"session:{session_id}", payload)


def get_session(session_id: str) -> Optional[dict]:
    """Retrieve session data."""
    raw = _get(f"session:{session_id}")
    if raw:
        return json.loads(raw)
    return None


def save_chat_history(session_id: str, history: list) -> None:
    payload = json.dumps(history)
    _set(f"chat:{session_id}", payload)


def get_chat_history(session_id: str) -> list:
    raw = _get(f"chat:{session_id}")
    if raw:
        return json.loads(raw)
    return []


def append_chat_message(session_id: str, role: str, content: str) -> None:
    history = get_chat_history(session_id)
    history.append({"role": role, "content": content})
    save_chat_history(session_id, history)


def delete_session(session_id: str) -> None:
    _delete(f"session:{session_id}")
    _delete(f"chat:{session_id}")


def health_check() -> dict:
    return {
        "redis_available": REDIS_AVAILABLE,
        "fallback_keys": len(_memory_store) if not REDIS_AVAILABLE else "n/a"
    }
