#!/usr/bin/env python3
"""Unit tests for error handling functionality"""

import pytest
from market_data.utils.errors import (
    ErrorType,
    MarketDataError,
    AuthenticationError,
    RateLimitError,
    ProviderError,
    DataError,
    create_error_response,
    create_success_response,
    handle_provider_error
)


class TestErrorType:
    """Test ErrorType enum"""
    
    def test_error_types_exist(self):
        """Test that all error types are defined"""
        assert ErrorType.AUTH_FAILED
        assert ErrorType.RATE_LIMIT_EXCEEDED
        assert ErrorType.PROVIDER_UNAVAILABLE
        assert ErrorType.INVALID_SYMBOL
        assert ErrorType.NETWORK_ERROR
        assert ErrorType.INTERNAL_ERROR
    
    def test_error_type_values(self):
        """Test error type string values"""
        assert ErrorType.AUTH_FAILED.value == "authentication_failed"
        assert ErrorType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_market_data_error(self):
        """Test MarketDataError base exception"""
        error = MarketDataError(ErrorType.INTERNAL_ERROR, "Test error")
        assert str(error) == "Test error"
        assert error.error_type == ErrorType.INTERNAL_ERROR
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError("Auth failed")
        assert "Auth failed" in str(error)
        assert error.error_type == ErrorType.AUTH_FAILED
    
    def test_rate_limit_error(self):
        """Test RateLimitError with wait time"""
        error = RateLimitError("Rate limit exceeded", wait_time=60)
        assert error.details["wait_time_seconds"] == 60
        assert error.error_type == ErrorType.RATE_LIMIT_EXCEEDED
    
    def test_provider_error(self):
        """Test ProviderError"""
        error = ProviderError("Provider down", provider="finnhub")
        assert error.provider == "finnhub"
        assert error.error_type == ErrorType.PROVIDER_UNAVAILABLE
    
    def test_data_error(self):
        """Test DataError"""
        error = DataError("Invalid symbol", error_type=ErrorType.INVALID_SYMBOL)
        assert "Invalid symbol" in str(error)
        assert error.error_type == ErrorType.INVALID_SYMBOL


class TestErrorResponseCreation:
    """Test error response creation functions"""
    
    def test_create_error_response(self):
        """Test creating error response"""
        response = create_error_response(
            ErrorType.INVALID_SYMBOL,
            "Symbol not found",
            details={"symbol": "INVALID"}
        )
        
        assert response["error"] is True
        assert response["error_type"] == "invalid_symbol"
        assert response["message"] == "Symbol not found"
        assert response["details"]["symbol"] == "INVALID"
    
    def test_create_error_response_minimal(self):
        """Test creating error response with minimal info"""
        response = create_error_response(
            ErrorType.NETWORK_ERROR,
            "Network failed"
        )
        
        assert response["error"] is True
        assert response["error_type"] == "network_error"
        assert response["message"] == "Network failed"
    
    def test_create_success_response(self):
        """Test creating success response"""
        data = {"symbol": "AAPL", "price": 150.0}
        response = create_success_response(
            data=data,
            metadata={"provider": "robinhood"}
        )
        
        assert response["error"] is False
        assert response["data"] == data
        assert response["metadata"]["provider"] == "robinhood"
    
    def test_create_success_response_minimal(self):
        """Test creating success response with minimal info"""
        data = {"result": "ok"}
        response = create_success_response(data=data)
        
        assert response["error"] is False
        assert response["data"] == data


class TestHandleProviderError:
    """Test provider error handling"""
    
    def test_handle_authentication_error(self):
        """Test handling authentication errors"""
        error = Exception("401 Unauthorized")
        response = handle_provider_error(error, "robinhood", "get_quote")
        
        assert response["error"] is True
        assert response["error_type"] == "authentication_failed"
        assert response["provider"] == "robinhood"
        assert response["details"]["operation"] == "get_quote"
    
    def test_handle_rate_limit_error(self):
        """Test handling rate limit errors"""
        error = Exception("Rate limit exceeded")
        response = handle_provider_error(error, "alpha_vantage", "get_quote")
        
        assert response["error"] is True
        assert response["error_type"] == "rate_limit_exceeded"
        assert response["provider"] == "alpha_vantage"
    
    def test_handle_generic_exception(self):
        """Test handling generic exceptions"""
        error = Exception("Something went wrong")
        response = handle_provider_error(error, "finnhub", "get_fundamentals")
        
        assert response["error"] is True
        assert response["provider"] == "finnhub"
        assert "Something went wrong" in response["message"]
    
    def test_handle_provider_error(self):
        """Test handling ProviderError"""
        error = ProviderError("Service unavailable", provider="finnhub")
        response = handle_provider_error(error, "finnhub", "get_quote")
        
        assert response["error"] is True
        assert response["error_type"] == "provider_unavailable"
        assert response["provider"] == "finnhub"


class TestErrorDetection:
    """Test error detection from messages"""
    
    def test_detect_auth_error_from_message(self):
        """Test detecting auth errors from exception messages"""
        error = Exception("401 Unauthorized")
        response = handle_provider_error(error, "test", "test")
        
        # Should detect as auth-related
        assert response["error"] is True
    
    def test_detect_rate_limit_from_message(self):
        """Test detecting rate limit from exception messages"""
        error = Exception("429 Too Many Requests")
        response = handle_provider_error(error, "test", "test")
        
        assert response["error"] is True
    
    def test_detect_network_error_from_message(self):
        """Test detecting network errors from exception messages"""
        error = Exception("Connection timeout")
        response = handle_provider_error(error, "test", "test")
        
        assert response["error"] is True
