"""LLM client for interacting with various language models."""

import os
import json
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate a structured response following a schema."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a response using OpenAI API."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate a structured response with JSON schema."""
        try:
            system_prompt = f"""You must respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Ensure your response is valid JSON and follows the schema exactly."""
            
            response = self.generate_response(prompt, system_prompt, **kwargs)
            
            # Try to parse JSON from response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No valid JSON found in response")
                    
        except Exception as e:
            logger.error(f"OpenAI structured response error: {e}")
            raise


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = model
        except ImportError:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a response using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7),
                system=system_prompt or "You are a helpful AI coding assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate a structured response with JSON schema."""
        try:
            system_prompt = f"""You must respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Ensure your response is valid JSON and follows the schema exactly."""
            
            response = self.generate_response(prompt, system_prompt, **kwargs)
            
            # Try to parse JSON from response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No valid JSON found in response")
                    
        except Exception as e:
            logger.error(f"Anthropic structured response error: {e}")
            raise


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(provider: str = "openai", **kwargs) -> LLMClient:
        """
        Create an LLM client based on provider.
        
        Args:
            provider: Provider name (openai, anthropic)
            **kwargs: Additional arguments for client initialization
            
        Returns:
            Configured LLM client
        """
        provider = provider.lower()
        
        if provider == "openai":
            return OpenAIClient(**kwargs)
        elif provider == "anthropic":
            return AnthropicClient(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def create_default_client() -> LLMClient:
        """Create default client based on environment configuration."""
        provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        model = os.getenv("DEFAULT_MODEL", "gpt-4" if provider == "openai" else "claude-3-sonnet-20240229")
        
        return LLMClientFactory.create_client(provider, model=model)


class LLMManager:
    """Manager for handling multiple LLM clients and fallbacks."""
    
    def __init__(self, primary_client: LLMClient, fallback_clients: Optional[List[LLMClient]] = None):
        self.primary_client = primary_client
        self.fallback_clients = fallback_clients or []
        self.all_clients = [primary_client] + self.fallback_clients
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response with fallback support."""
        for i, client in enumerate(self.all_clients):
            try:
                logger.info(f"Attempting to generate response with client {i+1}")
                return client.generate_response(prompt, system_prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Client {i+1} failed: {e}")
                if i == len(self.all_clients) - 1:
                    raise
                continue
        
        raise RuntimeError("All LLM clients failed")
    
    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured response with fallback support."""
        for i, client in enumerate(self.all_clients):
            try:
                logger.info(f"Attempting to generate structured response with client {i+1}")
                return client.generate_structured_response(prompt, schema, **kwargs)
            except Exception as e:
                logger.warning(f"Client {i+1} failed: {e}")
                if i == len(self.all_clients) - 1:
                    raise
                continue
        
        raise RuntimeError("All LLM clients failed")
