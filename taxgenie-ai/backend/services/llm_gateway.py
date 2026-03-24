"""
LLM Gateway - Unified interface for multiple LLM providers
Uses LiteLLM for provider abstraction
"""

import litellm
from litellm import completion, acompletion, embedding
from typing import List, Dict, Any, Optional
import base64
from config import settings

# Configure LiteLLM
litellm.set_verbose = settings.DEBUG


class LLMGateway:
    """
    Unified gateway for all LLM calls
    Supports: OpenAI, Anthropic, with automatic fallback
    """
    
    def __init__(self):
        self.default_model = settings.PRIMARY_MODEL
        self.vision_model = settings.VISION_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> str:
        """
        Generate text completion
        """
        model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if json_mode and "gpt" in model:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = await acompletion(**kwargs)
        return response.choices[0].message.content
    
    async def generate_with_image(
        self,
        prompt: str,
        image_data: bytes,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate completion with image input (GPT-4V)
        """
        model = model or self.vision_model
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        })
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate chat completion with message history
        """
        model = model or self.default_model
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def get_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Get embeddings for texts
        """
        model = model or self.embedding_model
        
        response = await litellm.aembedding(
            model=model,
            input=texts
        )
        
        return [item["embedding"] for item in response.data]
    
    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Generate streaming completion
        """
        model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
llm = LLMGateway()