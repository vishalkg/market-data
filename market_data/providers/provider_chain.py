#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from .base_provider import BaseProvider, ProviderCapability

logger = logging.getLogger(__name__)


class ProviderChain:
    """Manages fallback chain execution across multiple providers"""
    
    def __init__(self, providers: List[BaseProvider]):
        self.providers = providers
        self.errors: Dict[str, str] = {}
    
    async def execute(self, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute method across provider chain with fallback"""
        self.errors.clear()
        
        for i, provider in enumerate(self.providers):
            try:
                # Check if provider supports the method
                if not hasattr(provider, method_name):
                    self.errors[provider.name] = f"Method {method_name} not supported"
                    continue
                
                # Check provider health
                if not await provider.health_check():
                    self.errors[provider.name] = "Provider health check failed"
                    continue
                
                logger.info(f"Executing {method_name} on {provider.name} (attempt {i+1})")
                
                method = getattr(provider, method_name)
                result = await method(*args, **kwargs)
                
                # Add provider metadata to successful result
                if isinstance(result, dict):
                    result["provider"] = provider.name
                    result["fallback_used"] = i > 0
                    if i > 0:
                        result["failed_providers"] = list(self.errors.keys())
                
                logger.info(f"Success: {method_name} completed by {provider.name}")
                return result
                
            except Exception as e:
                error_msg = str(e)
                self.errors[provider.name] = error_msg
                logger.warning(f"Provider {provider.name} failed for {method_name}: {error_msg}")
                
                # If this is the last provider, don't continue
                if i == len(self.providers) - 1:
                    break
                
                # Add small delay before trying next provider
                await asyncio.sleep(0.1)
        
        # All providers failed
        return {
            "error": "All providers in chain failed",
            "method": method_name,
            "provider_errors": self.errors,
            "total_providers": len(self.providers)
        }
    
    async def execute_with_capability_filter(
        self, 
        method_name: str, 
        required_capability: ProviderCapability,
        *args, 
        **kwargs
    ) -> Dict[str, Any]:
        """Execute method only on providers that support the required capability"""
        capable_providers = [
            p for p in self.providers 
            if p.supports_capability(required_capability)
        ]
        
        if not capable_providers:
            return {
                "error": f"No providers support capability: {required_capability.value}",
                "method": method_name,
                "available_providers": [p.name for p in self.providers]
            }
        
        # Create temporary chain with only capable providers
        temp_chain = ProviderChain(capable_providers)
        return await temp_chain.execute(method_name, *args, **kwargs)
    
    async def get_chain_status(self) -> Dict[str, Any]:
        """Get health status of all providers in chain"""
        status = {}
        
        for provider in self.providers:
            try:
                is_healthy = await provider.health_check()
                status[provider.name] = {
                    "healthy": is_healthy,
                    "capabilities": [cap.value for cap in provider.get_capabilities()],
                    "metadata": provider.get_metadata()
                }
            except Exception as e:
                status[provider.name] = {
                    "healthy": False,
                    "error": str(e),
                    "capabilities": [],
                    "metadata": {}
                }
        
        return {
            "chain_status": status,
            "total_providers": len(self.providers),
            "healthy_providers": sum(1 for s in status.values() if s.get("healthy", False))
        }
    
    def get_providers_by_capability(self, capability: ProviderCapability) -> List[BaseProvider]:
        """Get all providers that support a specific capability"""
        return [p for p in self.providers if p.supports_capability(capability)]
    
    def reorder_by_priority(self, priority_order: List[str]) -> None:
        """Reorder providers based on priority list"""
        provider_map = {p.name: p for p in self.providers}
        reordered = []
        
        # Add providers in priority order
        for name in priority_order:
            if name in provider_map:
                reordered.append(provider_map[name])
                del provider_map[name]
        
        # Add remaining providers at the end
        reordered.extend(provider_map.values())
        
        self.providers = reordered
        logger.info(f"Reordered provider chain: {[p.name for p in self.providers]}")
