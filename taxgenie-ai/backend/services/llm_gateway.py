"""
TaxGenie AI - LLM Gateway Service
Unified LLM interface using LiteLLM for routing between OpenAI and Anthropic.
"""

import logging
from typing import Optional
import litellm
from config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.openai_key = settings.OPENAI_API_KEY
litellm.anthropic_key = settings.ANTHROPIC_API_KEY
litellm.set_verbose = False


async def llm_call(
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    response_format: Optional[dict] = None,
) -> str:
    """
    Make a single LLM call and return the text response.
    Handles both OpenAI and Anthropic models transparently via LiteLLM.
    """
    try:
        messages = [{"role": "user", "content": user_message}]

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # System prompt handling (different for anthropic vs openai)
        if "claude" in model.lower():
            kwargs["system"] = system_prompt
        else:
            kwargs["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

        if response_format:
            kwargs["response_format"] = response_format

        response = await litellm.acompletion(**kwargs)
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM call failed for model {model}: {e}")
        raise RuntimeError(f"LLM call failed: {str(e)}")


async def chat_completion(
    model: str,
    system_prompt: str,
    messages: list,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Multi-turn chat completion with message history.
    """
    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if "claude" in model.lower():
            kwargs["system"] = system_prompt
        else:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            kwargs["messages"] = full_messages

        response = await litellm.acompletion(**kwargs)
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise RuntimeError(f"Chat completion failed: {str(e)}")
