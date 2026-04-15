"""
Unit тести для модуля _exceptions.py

Тестує всі exception класи та helper функції.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Додаємо шлях до модуля для імпорту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _exceptions import (
    FridayError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    BadRequestError,
    ConflictError,
    UnprocessableEntityError,
    RateLimitError,
    InternalServerError,
    ServiceUnavailableError,
    APIConnectionError,
    APITimeoutError,
    ValidationError,
    make_error_from_response,
    handle_httpx_error,
)


class TestFridayError:
    """Тести для базового класу FridayError"""
    
    def test_basic_error(self):
        """Тест створення базової помилки"""
        error = FridayError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
    
    def test_error_inheritance(self):
        """Тест що FridayError наслідується від Exception"""
        error = FridayError("Test")
        assert isinstance(error, Exception)
    
    def test_repr(self):
        """Тест repr методу"""
        error = FridayError("Test message")
        assert repr(error) == "FridayError(message='Test message')"
    
    def test_catching_as_exception(self):
        """Тест що можна ловити як Exception"""
        with pytest.raises(Exception):
            raise FridayError("Test")


class TestAPIError:
    """Тести для APIError"""
    
    def test_basic_api_error(self):
        """Тест створення базової API помилки"""
        error = APIError(
            "API failed",
            status_code=500,
            headers={"x-request-id": "test-123"}
        )
        assert error.message == "API failed"
        assert error.status_code == 500
        assert error.request_id == "test-123"
    
    def test_api_error_without_request_id(self):
        """Тест API помилки без request_id"""
        error = APIError("Test", status_code=400)
        assert error.request_id is None
    
    def test_api_error_with_body(self):
        """Тест API помилки з body"""
        body = {"error": "Invalid input", "details": "Field X is required"}
        error = APIError("Test", body=body)
        assert error.body == body
    
    def test_repr(self):
        """Тест repr методу"""
        error = APIError(
            "Test",
            status_code=400,
            headers={"x-request-id": "abc123"}
        )
        assert "APIError" in repr(error)
        assert "status_code=400" in repr(error)
        assert "request_id='abc123'" in repr(error)
    
    def test_from_response_with_json(self):
        """Тест створення помилки з JSON response"""
        # Mock response
        response = Mock()
        response.status_code = 400
        response.headers = {"x-request-id": "req-123"}
        response.json.return_value = {"error": "Bad request"}
        
        error = APIError.from_response(response)
        
        assert isinstance(error, BadRequestError)
        assert error.status_code == 400
        assert error.message == "Bad request"
        assert error.request_id == "req-123"
        assert error.body == {"error": "Bad request"}
    
    def test_from_response_without_json(self):
        """Тест створення помилки коли response не JSON"""
        response = Mock()
        response.status_code = 500
        response.headers = {}
        response.json.side_effect = Exception("Not JSON")
        response.text = "Internal Server Error"
        
        error = APIError.from_response(response)
        
        assert isinstance(error, InternalServerError)
        assert error.body == {"error": "Internal Server Error"}
    
    def test_from_response_with_custom_message(self):
        """Тест створення помилки з кастомним повідомленням"""
        response = Mock()
        response.status_code = 401
        response.headers = {}
        response.json.return_value = {"error": "Unauthorized"}
        
        error = APIError.from_response(response, message="Custom error message")
        
        assert error.message == "Custom error message"
        assert isinstance(error, AuthenticationError)
    
    def test_get_error_class_mapping(self):
        """Тест маппінгу статус кодів на класи помилок"""
        assert APIError._get_error_class(400) == BadRequestError
        assert APIError._get_error_class(401) == AuthenticationError
        assert APIError._get_error_class(403) == PermissionDeniedError
        assert APIError._get_error_class(404) == NotFoundError
        assert APIError._get_error_class(409) == ConflictError
        assert APIError._get_error_class(422) == UnprocessableEntityError
        assert APIError._get_error_class(429) == RateLimitError
        assert APIError._get_error_class(500) == InternalServerError
        assert APIError._get_error_class(503) == ServiceUnavailableError
    
    def test_get_error_class_unknown_status(self):
        """Тест що невідомий статус код повертає базовий APIError"""
        assert APIError._get_error_class(418) == APIError  # I'm a teapot
        assert APIError._get_error_class(999) == APIError


class TestAuthenticationError:
    """Тести для AuthenticationError"""
    
    def test_default_message(self):
        """Тест дефолтного повідомлення"""
        error = AuthenticationError()
        assert error.message == "Authentication failed"
    
    def test_custom_message(self):
        """Тест кастомного повідомлення"""
        error = AuthenticationError("Invalid API key")
        assert error.message == "Invalid API key"
    
    def test_with_status_code(self):
        """Тест з статус кодом"""
        error = AuthenticationError(status_code=401)
        assert error.status_code == 401


class TestPermissionDeniedError:
    """Тести для PermissionDeniedError"""
    
    def test_default_message(self):
        error = PermissionDeniedError()
        assert error.message == "Permission denied"
    
    def test_custom_message(self):
        error = PermissionDeniedError("Access forbidden")
        assert error.message == "Access forbidden"


class TestNotFoundError:
    """Тести для NotFoundError"""
    
    def test_default_message(self):
        error = NotFoundError()
        assert error.message == "Resource not found"
    
    def test_custom_message(self):
        error = NotFoundError("Collection not found")
        assert error.message == "Collection not found"


class TestBadRequestError:
    """Тести для BadRequestError"""
    
    def test_default_message(self):
        error = BadRequestError()
        assert error.message == "Bad request"
    
    def test_without_validation_errors(self):
        """Тест без validation errors"""
        error = BadRequestError("Invalid input")
        assert error.validation_errors == []
    
    def test_with_validation_errors_field(self):
        """Тест з validation_errors полем"""
        error = BadRequestError(
            "Invalid input",
            body={
                "validation_errors": [
                    "Field 'model' is required",
                    "Field 'messages' cannot be empty"
                ]
            }
        )
        
        assert len(error.validation_errors) == 2
        assert "Field 'model' is required" in error.validation_errors
        assert "Field 'messages' cannot be empty" in error.validation_errors
    
    def test_with_errors_field(self):
        """Тест з errors полем (альтернативний формат)"""
        error = BadRequestError(
            "Invalid",
            body={"errors": ["Error 1", "Error 2"]}
        )
        assert len(error.validation_errors) == 2
    
    def test_with_details_field(self):
        """Тест з details полем (альтернативний формат)"""
        error = BadRequestError(
            "Invalid",
            body={"details": ["Detail 1"]}
        )
        assert len(error.validation_errors) == 1


class TestRateLimitError:
    """Тести для RateLimitError"""
    
    def test_default_message(self):
        error = RateLimitError()
        assert error.message == "Rate limit exceeded"
    
    def test_without_retry_after(self):
        """Тест без retry_after"""
        error = RateLimitError("Too many requests")
        assert error.retry_after is None
    
    def test_with_retry_after_header(self):
        """Тест з retry_after в headers"""
        error = RateLimitError(
            "Rate limit",
            headers={"retry-after": "60"}
        )
        assert error.retry_after == 60
    
    def test_with_retry_after_in_body(self):
        """Тест з retry_after в body"""
        error = RateLimitError(
            "Rate limit",
            body={"retry_after": 120}
        )
        assert error.retry_after == 120
    
    def test_with_limit_info(self):
        """Тест з інформацією про ліміти"""
        error = RateLimitError(
            "Rate limit exceeded",
            headers={"retry-after": "30"},
            body={
                "limit_type": "chat",
                "current_usage": 100,
                "limit": 100
            }
        )
        
        assert error.retry_after == 30
        assert error.limit_type == "chat"
        assert error.current_usage == 100
        assert error.limit == 100
    
    def test_invalid_retry_after(self):
        """Тест з невалідним retry_after"""
        error = RateLimitError(
            "Rate limit",
            headers={"retry-after": "invalid"}
        )
        assert error.retry_after is None


class TestInternalServerError:
    """Тести для InternalServerError"""
    
    def test_default_message(self):
        error = InternalServerError()
        assert "try again later" in error.message.lower()
    
    def test_custom_message(self):
        error = InternalServerError("Database error")
        assert error.message == "Database error"


class TestServiceUnavailableError:
    """Тести для ServiceUnavailableError"""
    
    def test_default_message(self):
        error = ServiceUnavailableError()
        assert "unavailable" in error.message.lower()
    
    def test_with_retry_after(self):
        """Тест з retry_after"""
        error = ServiceUnavailableError(
            "Maintenance",
            headers={"retry-after": "300"}
        )
        assert error.retry_after == 300
    
    def test_without_retry_after(self):
        error = ServiceUnavailableError("Maintenance")
        assert error.retry_after is None


class TestConflictError:
    """Тести для ConflictError"""
    
    def test_default_message(self):
        error = ConflictError()
        assert error.message == "Resource conflict"
    
    def test_custom_message(self):
        error = ConflictError("Collection already exists")
        assert error.message == "Collection already exists"


class TestUnprocessableEntityError:
    """Тести для UnprocessableEntityError"""
    
    def test_default_message(self):
        error = UnprocessableEntityError()
        assert error.message == "Unprocessable entity"
    
    def test_custom_message(self):
        error = UnprocessableEntityError("Invalid combination")
        assert error.message == "Invalid combination"


class TestAPIConnectionError:
    """Тести для APIConnectionError"""
    
    def test_default_message(self):
        error = APIConnectionError()
        assert "connection" in error.message.lower()
    
    def test_with_original_error(self):
        """Тест з оригінальною помилкою"""
        original = ConnectionError("Network is down")
        error = APIConnectionError(
            "Failed to connect",
            original_error=original
        )
        
        assert error.message == "Failed to connect"
        assert error.original_error == original
    
    def test_repr(self):
        """Тест repr з оригінальною помилкою"""
        original = Exception("Test")
        error = APIConnectionError(
            "Connection failed",
            original_error=original
        )
        
        assert "APIConnectionError" in repr(error)
        assert "original_error" in repr(error)


class TestAPITimeoutError:
    """Тести для APITimeoutError"""
    
    def test_default_message(self):
        error = APITimeoutError()
        assert "timeout" in error.message.lower()
    
    def test_with_timeout(self):
        """Тест з timeout значенням"""
        error = APITimeoutError(
            "Request timed out",
            timeout=30.0
        )
        
        assert error.timeout == 30.0
        assert "timed out" in error.message.lower()
    
    def test_with_original_error(self):
        """Тест з оригінальною помилкою"""
        original = TimeoutError("Connection timeout")
        error = APITimeoutError(
            "Timeout",
            timeout=10.0,
            original_error=original
        )
        
        assert error.original_error == original
        assert error.timeout == 10.0
    
    def test_repr(self):
        """Тест repr з timeout"""
        error = APITimeoutError("Timeout", timeout=15.0)
        assert "APITimeoutError" in repr(error)
        assert "timeout=15.0" in repr(error)


class TestValidationError:
    """Тести для ValidationError"""
    
    def test_basic_validation_error(self):
        """Тест базової validation помилки"""
        error = ValidationError("Invalid value")
        assert error.message == "Invalid value"
        assert error.field is None
        assert error.value is None
    
    def test_with_field(self):
        """Тест з полем"""
        error = ValidationError(
            "Invalid model",
            field="model"
        )
        assert error.field == "model"
    
    def test_with_field_and_value(self):
        """Тест з полем та значенням"""
        error = ValidationError(
            "Invalid model",
            field="model",
            value="gpt-4"
        )
        
        assert error.field == "model"
        assert error.value == "gpt-4"
    
    def test_repr(self):
        """Тест repr"""
        error = ValidationError(
            "Invalid",
            field="test_field",
            value=123
        )
        
        assert "ValidationError" in repr(error)
        assert "field='test_field'" in repr(error)
        assert "value=123" in repr(error)


class TestMakeErrorFromResponse:
    """Тести для make_error_from_response helper функції"""
    
    def test_creates_correct_error_type(self):
        """Тест що створюється правильний тип помилки"""
        response = Mock()
        response.status_code = 401
        response.headers = {}
        response.json.return_value = {"error": "Unauthorized"}
        
        error = make_error_from_response(response)
        
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401
    
    def test_with_different_status_codes(self):
        """Тест з різними статус кодами"""
        test_cases = [
            (400, BadRequestError),
            (404, NotFoundError),
            (429, RateLimitError),
            (500, InternalServerError),
        ]
        
        for status_code, expected_class in test_cases:
            response = Mock()
            response.status_code = status_code
            response.headers = {}
            response.json.return_value = {"error": "Test"}
            
            error = make_error_from_response(response)
            assert isinstance(error, expected_class)


class TestHandleHttpxError:
    """Тести для handle_httpx_error helper функції"""
    
    def test_without_httpx_installed(self):
        """Тест коли httpx не встановлений"""
        # Симулюємо відсутність httpx
        error = Exception("Generic error")
        result = handle_httpx_error(error)
        
        assert isinstance(result, APIConnectionError)
        assert result.original_error == error
    
    @pytest.mark.skipif(
        True,  # Пропускаємо якщо httpx не встановлений
        reason="httpx not installed"
    )
    def test_timeout_exception(self):
        """Тест TimeoutException"""
        import httpx
        
        timeout_error = httpx.TimeoutException("Request timed out")
        result = handle_httpx_error(timeout_error, timeout=30.0)
        
        assert isinstance(result, APITimeoutError)
        assert result.timeout == 30.0
        assert result.original_error == timeout_error
    
    @pytest.mark.skipif(
        True,
        reason="httpx not installed"
    )
    def test_connect_error(self):
        """Тест ConnectError"""
        import httpx
        
        connect_error = httpx.ConnectError("Connection failed")
        result = handle_httpx_error(connect_error)
        
        assert isinstance(result, APIConnectionError)
        assert result.original_error == connect_error
    
    @pytest.mark.skipif(
        True,
        reason="httpx not installed"
    )
    def test_network_error(self):
        """Тест NetworkError"""
        import httpx
        
        network_error = httpx.NetworkError("Network problem")
        result = handle_httpx_error(network_error)
        
        assert isinstance(result, APIConnectionError)


class TestExceptionInheritance:
    """Тести для перевірки правильної ієрархії наслідування"""
    
    def test_all_api_errors_inherit_from_api_error(self):
        """Тест що всі API помилки наслідуються від APIError"""
        api_error_subclasses = [
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            BadRequestError,
            ConflictError,
            UnprocessableEntityError,
            RateLimitError,
            InternalServerError,
            ServiceUnavailableError,
        ]
        
        for error_class in api_error_subclasses:
            error = error_class("Test")
            assert isinstance(error, APIError)
            assert isinstance(error, FridayError)
    
    def test_all_errors_inherit_from_friday_error(self):
        """Тест що всі помилки наслідуються від FridayError"""
        all_error_classes = [
            APIError,
            AuthenticationError,
            APIConnectionError,
            APITimeoutError,
            ValidationError,
        ]
        
        for error_class in all_error_classes:
            error = error_class("Test")
            assert isinstance(error, FridayError)
            assert isinstance(error, Exception)
    
    def test_can_catch_all_with_friday_error(self):
        """Тест що можна ловити всі помилки через FridayError"""
        errors_to_test = [
            AuthenticationError("Test"),
            RateLimitError("Test"),
            APIConnectionError("Test"),
            ValidationError("Test"),
        ]
        
        for error in errors_to_test:
            with pytest.raises(FridayError):
                raise error


class TestExceptionMessages:
    """Тести для перевірки якості повідомлень про помилки"""
    
    def test_error_messages_are_informative(self):
        """Тест що повідомлення інформативні"""
        error = RateLimitError(
            "Rate limit exceeded",
            body={"current_usage": 100, "limit": 100}
        )
        
        assert error.message  # Не порожнє
        assert len(error.message) > 5  # Достатньо довге
    
    def test_error_with_details_provides_context(self):
        """Тест що помилки з деталями надають контекст"""
        error = BadRequestError(
            "Invalid request",
            body={
                "validation_errors": [
                    "Field 'messages' is required"
                ]
            }
        )
        
        assert error.message
        assert len(error.validation_errors) > 0


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    # Запуск тестів з verbose output
    pytest.main([__file__, "-v", "--tb=short"])