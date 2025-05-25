#!/usr/bin/env python3
"""
llm_adapters.py: Multimodal LLM adapter system for environment auditing.

This module provides a unified interface to multiple LLM providers,
allowing the audit tool to work with OpenAI, Anthropic, local models,
and others through a single API.
"""

import os
import json
import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    LOCAL_API = "local_api"


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 1200
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    provider: LLMProvider
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client."""
        pass
    
    @abstractmethod
    async def call_async(self, prompt: str) -> LLMResponse:
        """Make an async call to the LLM."""
        pass
    
    def call_sync(self, prompt: str) -> LLMResponse:
        """Make a synchronous call to the LLM."""
        return asyncio.run(self.call_async(prompt))
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the LLM provider is accessible."""
        pass


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI models (GPT-3.5, GPT-4, etc.)."""
    
    def _initialize_client(self):
        try:
            import openai
            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.config.base_url
            )
        except ImportError:
            raise ImportError("OpenAI package not installed: pip install openai")
    
    async def call_async(self, prompt: str) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **(self.config.extra_params or {})
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def test_connection(self) -> bool:
        try:
            # Simple test call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic models (Claude)."""
    
    def _initialize_client(self):
        try:
            import anthropic
            api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found")
            
            self.client = anthropic.Anthropic(
                api_key=api_key,
                base_url=self.config.base_url
            )
        except ImportError:
            raise ImportError("Anthropic package not installed: pip install anthropic")
    
    async def call_async(self, prompt: str) -> LLMResponse:
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}],
                **(self.config.extra_params or {})
            )
            
            return LLMResponse(
                content=response.content[0].text,
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
        except Exception as e:
            raise Exception(f"Anthropic API call failed: {str(e)}")
    
    def test_connection(self) -> bool:
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama local models."""
    
    def _initialize_client(self):
        self.base_url = self.config.base_url or "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def call_async(self, prompt: str) -> LLMResponse:
        try:
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API returned {response.status_code}: {response.text}")
            
            result = response.json()
            
            return LLMResponse(
                content=result["response"],
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                metadata={"eval_count": result.get("eval_count", 0)}
            )
        except Exception as e:
            raise Exception(f"Ollama API call failed: {str(e)}")
    
    def test_connection(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class HuggingFaceAdapter(BaseLLMAdapter):
    """Adapter for Hugging Face Inference API."""
    
    def _initialize_client(self):
        api_key = self.config.api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("Hugging Face API key not found")
        
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = self.config.base_url or "https://api-inference.huggingface.co"
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def call_async(self, prompt: str) -> LLMResponse:
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": self.config.temperature,
                    "max_new_tokens": self.config.max_tokens,
                    "return_full_text": False
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/models/{self.config.model}",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"HuggingFace API returned {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                content = result[0].get("generated_text", str(result))
            else:
                content = str(result)
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.HUGGINGFACE,
                model=self.config.model
            )
        except Exception as e:
            raise Exception(f"HuggingFace API call failed: {str(e)}")
    
    def test_connection(self) -> bool:
        try:
            # Test with a simple prompt
            payload = {"inputs": "test", "parameters": {"max_new_tokens": 1}}
            response = httpx.post(
                f"{self.base_url}/models/{self.config.model}",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False


class LocalAPIAdapter(BaseLLMAdapter):
    """Adapter for custom local APIs (compatible with OpenAI format)."""
    
    def _initialize_client(self):
        if not self.config.base_url:
            raise ValueError("Base URL required for local API")
        
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        self.headers = {"Content-Type": "application/json"}
        
        if self.config.api_key:
            self.headers["Authorization"] = f"Bearer {self.config.api_key}"
    
    async def call_async(self, prompt: str) -> LLMResponse:
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            response = await self.client.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Local API returned {response.status_code}: {response.text}")
            
            result = response.json()
            
            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                provider=LLMProvider.LOCAL_API,
                model=self.config.model,
                usage=result.get("usage")
            )
        except Exception as e:
            raise Exception(f"Local API call failed: {str(e)}")
    
    def test_connection(self) -> bool:
        try:
            response = httpx.get(f"{self.config.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class LLMAdapterFactory:
    """Factory for creating LLM adapters."""
    
    _adapters = {
        LLMProvider.OPENAI: OpenAIAdapter,
        LLMProvider.ANTHROPIC: AnthropicAdapter,
        LLMProvider.OLLAMA: OllamaAdapter,
        LLMProvider.HUGGINGFACE: HuggingFaceAdapter,
        LLMProvider.LOCAL_API: LocalAPIAdapter,
    }
    
    @classmethod
    def create_adapter(cls, config: LLMConfig) -> BaseLLMAdapter:
        """Create an adapter for the specified provider."""
        if config.provider not in cls._adapters:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        adapter_class = cls._adapters[config.provider]
        return adapter_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[LLMProvider]:
        """Get list of available providers."""
        return list(cls._adapters.keys())


class MultiLLMManager:
    """Manager for multiple LLM providers with fallback support."""
    
    def __init__(self, configs: List[LLMConfig]):
        self.adapters = []
        self.failed_adapters = []
        
        for config in configs:
            try:
                adapter = LLMAdapterFactory.create_adapter(config)
                if adapter.test_connection():
                    self.adapters.append(adapter)
                else:
                    self.failed_adapters.append((config.provider, "Connection test failed"))
            except Exception as e:
                self.failed_adapters.append((config.provider, str(e)))
        
        if not self.adapters:
            raise Exception("No working LLM adapters available")
    
    async def call_with_fallback(self, prompt: str) -> LLMResponse:
        """Call LLMs with automatic fallback to next provider on failure."""
        last_error = None
        
        for adapter in self.adapters:
            try:
                return await adapter.call_async(prompt)
            except Exception as e:
                last_error = e
                continue
        
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all configured providers."""
        return {
            "working_providers": [a.config.provider.value for a in self.adapters],
            "failed_providers": self.failed_adapters,
            "total_configured": len(self.adapters) + len(self.failed_adapters)
        }


# Configuration helpers
def load_llm_configs_from_env() -> List[LLMConfig]:
    """Load LLM configurations from environment variables."""
    configs = []
    
    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        configs.append(LLMConfig(
            provider=LLMProvider.OPENAI,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY")
        ))
    
    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        configs.append(LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ))
    
    # Ollama
    if os.getenv("OLLAMA_HOST") or os.path.exists("/usr/local/bin/ollama"):
        configs.append(LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=os.getenv("OLLAMA_MODEL", "llama2"),
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ))
    
    # Hugging Face
    if os.getenv("HUGGINGFACE_API_KEY"):
        configs.append(LLMConfig(
            provider=LLMProvider.HUGGINGFACE,
            model=os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium"),
            api_key=os.getenv("HUGGINGFACE_API_KEY")
        ))
    
    # Local API
    if os.getenv("LOCAL_LLM_URL"):
        configs.append(LLMConfig(
            provider=LLMProvider.LOCAL_API,
            model=os.getenv("LOCAL_LLM_MODEL", "local-model"),
            base_url=os.getenv("LOCAL_LLM_URL"),
            api_key=os.getenv("LOCAL_LLM_API_KEY")
        ))
    
    return configs


def load_llm_configs_from_file(config_path: str) -> List[LLMConfig]:
    """Load LLM configurations from a JSON file."""
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    configs = []
    for config_data in data.get("llm_providers", []):
        configs.append(LLMConfig(
            provider=LLMProvider(config_data["provider"]),
            model=config_data["model"],
            api_key=config_data.get("api_key"),
            base_url=config_data.get("base_url"),
            temperature=config_data.get("temperature", 0.2),
            max_tokens=config_data.get("max_tokens", 1200),
            timeout=config_data.get("timeout", 30),
            extra_params=config_data.get("extra_params")
        ))
    
    return configs


# Example usage and testing
async def test_adapters():
    """Test function to verify adapter functionality."""
    configs = load_llm_configs_from_env()
    
    if not configs:
        print("No LLM configurations found in environment")
        return
    
    manager = MultiLLMManager(configs)
    print("LLM Status:", manager.get_status())
    
    try:
        response = await manager.call_with_fallback("Hello, world!")
        print(f"Response from {response.provider.value}: {response.content[:100]}...")
    except Exception as e:
        print(f"All LLM calls failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_adapters())
