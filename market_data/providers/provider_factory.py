#!/usr/bin/env python3

import logging
from typing import Any, Dict, List, Type, Optional
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating and managing provider instances"""
    
    _providers: Dict[str, Type[BaseProvider]] = {}
    _instances: Dict[str, BaseProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseProvider]) -> None:
        """Register a provider class"""
        if not issubclass(provider_class, BaseProvider):
            raise ValueError(f"Provider class must inherit from BaseProvider")
        
        cls._providers[name] = provider_class
        logger.info(f"Registered provider: {name}")
    
    @classmethod
    def create_provider(cls, name: str, **kwargs) -> BaseProvider:
        """Create a provider instance"""
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._providers.keys())}")
        
        provider_class = cls._providers[name]
        instance = provider_class(**kwargs)
        
        # Cache instance for reuse
        cls._instances[name] = instance
        logger.info(f"Created provider instance: {name}")
        return instance
    
    @classmethod
    def get_provider(cls, name: str, **kwargs) -> BaseProvider:
        """Get existing provider instance or create new one"""
        if name in cls._instances:
            return cls._instances[name]
        return cls.create_provider(name, **kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_capabilities(cls, name: str) -> List[str]:
        """Get capabilities of a provider without instantiating it"""
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        
        # Create temporary instance to get capabilities
        temp_instance = cls._providers[name]()
        return [cap.value for cap in temp_instance.get_capabilities()]
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached provider instances"""
        cls._instances.clear()
        logger.info("Cleared provider instance cache")
    
    @classmethod
    def reset(cls) -> None:
        """Reset factory (for testing)"""
        cls._providers.clear()
        cls._instances.clear()
        logger.info("Reset provider factory")
