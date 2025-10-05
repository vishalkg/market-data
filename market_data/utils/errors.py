#!/usr/bin/env python3
"""
Standardized error handling for market data services.
Defines error types, error response formats, and error handling utilities.
"""

from enum import Enum
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Standard error types across the application"""
    
    # Authentication errors
    AUTH_FAILED = "authentication_failed"
    AUTH_EXPIRED = "authentication_expired"
    INVALID_CREDENTIALS = "invalid_credentials"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_TIMEOUT = "rate_limit_timeout"
    
    # Provider errors
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_TIMEOUT = "provider_timeout"
    ALL_PROVIDERS_FAILED = "all_providers_failed"
    
    # Data errors
    INVALID_SYMBOL = "invalid_symbol"
    NO_DATA_AVAILABLE = "no_data_available"
    INVALID_PARAMETERS = "invalid_parameters"
    
    # Network errors
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    
    # API errors
    API_ERROR = "api_error"
    INVALID_API_KEY = "invalid_api_key"
    QUOTA_EXCEEDED = "quota_exceeded"
    
    # Internal errors
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"


class MarketDataError(Exception):
    """Base exception for market data errors"""
    
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.provider = provider
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for API responses"""
        error_dict = {
            "error": True,
            "error_type": self.error_type.value,
            "message": self.message
        }
        
        if self.provider:
            error_dict["provider"] = self.provider
        
        if self.details:
            error_dict["details"] = self.details
        
        return error_dict


class AuthenticationError(MarketDataError):
    """Authentication-related errors"""
    
    def __init__(self, message: str, provider: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            error_type=ErrorType.AUTH_FAILED,
            message=message,
            details=details,
            provider=provider
        )


class RateLimitError(MarketDataError):
    """Rate limiting errors"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        wait_time: Optional[float] = None,
        details: Optional[Dict] = None
    ):
        error_details = details or {}
        if wait_time:
            error_details["wait_time_seconds"] = wait_time
        
        super().__init__(
            error_type=ErrorType.RATE_LIMIT_EXCEEDED,
            message=message,
            details=error_details,
            provider=provider
        )


class ProviderError(MarketDataError):
    """Provider-related errors"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        error_type: ErrorType = ErrorType.PROVIDER_UNAVAILABLE,
        details: Optional[Dict] = None
    ):
        super().__init__(
            error_type=error_type,
            message=message,
            details=details,
            provider=provider
        )


class DataError(MarketDataError):
    """Data-related errors"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.NO_DATA_AVAILABLE,
        details: Optional[Dict] = None
    ):
        super().__init__(
            error_type=error_type,
            message=message,
            details=details
        )


def create_error_response(
    error_type: ErrorType,
    message: str,
    provider: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    Use this for MCP tool responses (user-facing).
    """
    response = {
        "error": True,
        "error_type": error_type.value,
        "message": message
    }
    
    if provider:
        response["provider"] = provider
    
    if details:
        response["details"] = details
    
    return response


def create_success_response(data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.
    Use this for MCP tool responses (user-facing).
    """
    response = {
        "error": False,
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def handle_provider_error(e: Exception, provider_name: str, operation: str) -> Dict[str, Any]:
    """
    Handle provider errors and convert to standardized error response.
    Use this in service layer to convert exceptions to error dictionaries.
    """
    logger.error(f"Provider {provider_name} failed during {operation}: {e}")
    
    error_str = str(e).lower()
    
    # Detect error type from exception message
    if "authentication" in error_str or "unauthorized" in error_str or "401" in error_str:
        return create_error_response(
            ErrorType.AUTH_FAILED,
            f"Authentication failed for {provider_name}",
            provider=provider_name,
            details={"operation": operation, "original_error": str(e)}
        )
    
    elif "rate limit" in error_str or "429" in error_str or "quota" in error_str:
        return create_error_response(
            ErrorType.RATE_LIMIT_EXCEEDED,
            f"Rate limit exceeded for {provider_name}",
            provider=provider_name,
            details={"operation": operation, "original_error": str(e)}
        )
    
    elif "timeout" in error_str:
        return create_error_response(
            ErrorType.TIMEOUT_ERROR,
            f"Request timeout for {provider_name}",
            provider=provider_name,
            details={"operation": operation, "original_error": str(e)}
        )
    
    elif "network" in error_str or "connection" in error_str:
        return create_error_response(
            ErrorType.NETWORK_ERROR,
            f"Network error for {provider_name}",
            provider=provider_name,
            details={"operation": operation, "original_error": str(e)}
        )
    
    elif "not found" in error_str or "invalid symbol" in error_str:
        return create_error_response(
            ErrorType.INVALID_SYMBOL,
            f"Invalid symbol or data not found",
            provider=provider_name,
            details={"operation": operation, "original_error": str(e)}
        )
    
    else:
        # Generic provider error
        return create_error_response(
            ErrorType.PROVIDER_UNAVAILABLE,
            f"Provider {provider_name} failed: {str(e)}",
            provider=provider_name,
            details={"operation": operation}
        )


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable (should try next provider in chain).
    """
    error_str = str(error).lower()
    
    # Retryable errors
    retryable_keywords = [
        "timeout",
        "network",
        "connection",
        "temporary",
        "unavailable",
        "503",
        "502",
        "504"
    ]
    
    # Non-retryable errors
    non_retryable_keywords = [
        "invalid symbol",
        "not found",
        "invalid parameter",
        "400",
        "404"
    ]
    
    # Check non-retryable first
    if any(keyword in error_str for keyword in non_retryable_keywords):
        return False
    
    # Check retryable
    if any(keyword in error_str for keyword in retryable_keywords):
        return True
    
    # Default: retry on unknown errors
    return True
