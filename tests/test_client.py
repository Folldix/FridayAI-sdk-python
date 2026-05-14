"""
Unit тести для модуля _client.py

Тестує BaseClient та AsyncClient.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "friday"))
from _client import BaseClient, AsyncClient
from _exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
    InternalServerError,
    APIConnectionError,
    APITimeoutError,
)


class TestBaseClientInit:
    """Тести для ініціалізації BaseClient"""
    
    def test_init_with_api_key(self):
        """Тест успішної ініціалізації з API ключем"""
        client = BaseClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://www.fridayai.online/api"
        assert client.timeout == 300.0
        assert client.max_retries == 2
    
    def test_init_without_api_key(self):
        """Тест що помилка викидається без API ключа"""
        with pytest.raises(ValueError, match="API key is required"):
            BaseClient(api_key="")
    
    def test_init_with_custom_params(self):
        """Тест ініціалізації з кастомними параметрами"""
        client = BaseClient(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            timeout=60.0,
            max_retries=5
        )
        
        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.api.com/v1"
        assert client.timeout == 60.0
        assert client.max_retries == 5
    
    def test_init_strips_trailing_slash(self):
        """Тест що trailing slash видаляється з base_url"""
        client = BaseClient(
            api_key="test-key",
            base_url="https://api.com/v1/"
        )
        assert client.base_url == "https://api.com/v1"
    
    def test_init_with_default_headers(self):
        """Тест з кастомними default headers"""
        custom_headers = {"X-Custom": "value"}
        client = BaseClient(
            api_key="test-key",
            default_headers=custom_headers
        )
        assert client.default_headers == custom_headers


class TestPrepareHeaders:
    """Тести для _prepare_headers методу"""
    
    def test_prepare_headers_default(self):
        """Тест дефолтних заголовків"""
        client = BaseClient(api_key="test-key")
        headers = client._prepare_headers()
        
        assert headers["X-User-Token"] == "test-key"
        assert headers["Content-Type"] == "application/json"
        assert "User-Agent" in headers
        assert "friday-python" in headers["User-Agent"]
    
    def test_prepare_headers_with_custom(self):
        """Тест з додатковими заголовками"""
        client = BaseClient(api_key="test-key")
        headers = client._prepare_headers(
            headers={"X-Custom": "value"}
        )
        
        assert headers["X-User-Token"] == "test-key"
        assert headers["X-Custom"] == "value"
    
    def test_prepare_headers_override(self):
        """Тест що кастомні заголовки перезаписують дефолтні"""
        client = BaseClient(api_key="test-key")
        headers = client._prepare_headers(
            headers={"Content-Type": "text/plain"}
        )
        
        assert headers["Content-Type"] == "text/plain"
    
    def test_prepare_headers_with_defaults(self):
        """Тест з default_headers"""
        client = BaseClient(
            api_key="test-key",
            default_headers={"X-Default": "default-value"}
        )
        headers = client._prepare_headers()
        
        assert headers["X-Default"] == "default-value"


class TestHandleResponse:
    """Тести для _handle_response методу"""
    
    def test_handle_response_success(self):
        """Тест успішної відповіді"""
        client = BaseClient(api_key="test-key")
        
        # Mock response
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"result": "success"}
        
        result = client._handle_response(response)
        
        assert result == {"result": "success"}
    
    def test_handle_response_201(self):
        """Тест 201 Created відповіді"""
        client = BaseClient(api_key="test-key")
        
        response = Mock()
        response.status_code = 201
        response.json.return_value = {"created": True}
        
        result = client._handle_response(response)
        assert result == {"created": True}
    
    def test_handle_response_400(self):
        """Тест 400 Bad Request"""
        client = BaseClient(api_key="test-key")
        
        response = Mock()
        response.status_code = 400
        response.headers = {}
        response.json.return_value = {"error": "Bad request"}
        
        with pytest.raises(APIError):
            client._handle_response(response)
    
    def test_handle_response_401(self):
        """Тест 401 Unauthorized"""
        client = BaseClient(api_key="test-key")
        
        response = Mock()
        response.status_code = 401
        response.headers = {}
        response.json.return_value = {"error": "Unauthorized"}
        
        with pytest.raises(AuthenticationError):
            client._handle_response(response)
    
    def test_handle_response_429(self):
        """Тест 429 Rate Limit"""
        client = BaseClient(api_key="test-key")
        
        response = Mock()
        response.status_code = 429
        response.headers = {"retry-after": "60"}
        response.json.return_value = {"error": "Rate limit"}
        
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(response)
        
        assert exc_info.value.retry_after == 60
    
    def test_handle_response_invalid_json(self):
        """Тест коли response не JSON"""
        client = BaseClient(api_key="test-key")
        
        response = Mock()
        response.status_code = 200
        response.json.side_effect = ValueError("Not JSON")
        response.text = "Plain text response"
        
        with pytest.raises(APIError, match="Failed to parse JSON"):
            client._handle_response(response)


class TestShouldRetry:
    """Тести для _should_retry методу"""
    
    def test_should_retry_503(self):
        """Тест що retry для 503"""
        client = BaseClient(api_key="test-key", max_retries=3)
        
        error = ServiceUnavailableError("Service down")
        assert client._should_retry(error, 0) is True
        assert client._should_retry(error, 1) is True
        assert client._should_retry(error, 2) is True
        assert client._should_retry(error, 3) is False
    
    def test_should_retry_timeout(self):
        """Тест що retry для timeout"""
        client = BaseClient(api_key="test-key")
        
        error = APITimeoutError("Timeout")
        assert client._should_retry(error, 0) is True
    
    def test_should_retry_connection_error(self):
        """Тест що retry для connection error"""
        client = BaseClient(api_key="test-key")
        
        error = APIConnectionError("Connection failed")
        assert client._should_retry(error, 0) is True
    
    def test_should_retry_internal_server_error(self):
        """Тест що retry для 500 тільки 1 раз"""
        client = BaseClient(api_key="test-key")
        
        error = InternalServerError("Internal error")
        assert client._should_retry(error, 0) is True
        assert client._should_retry(error, 1) is False
    
    def test_should_not_retry_auth_error(self):
        """Тест що НЕ retry для auth помилок"""
        client = BaseClient(api_key="test-key")
        
        error = AuthenticationError("Unauthorized")
        assert client._should_retry(error, 0) is False
    
    def test_should_not_retry_rate_limit(self):
        """Тест що НЕ retry для rate limit (це робить користувач)"""
        client = BaseClient(api_key="test-key")
        
        error = RateLimitError("Rate limit")
        assert client._should_retry(error, 0) is False
    
    def test_max_retries_exceeded(self):
        """Тест що retry припиняється після max_retries"""
        client = BaseClient(api_key="test-key", max_retries=2)
        
        error = ServiceUnavailableError("Down")
        assert client._should_retry(error, 2) is False


class TestMakeRequest:
    """Тести для _make_request методу"""
    
    @patch("httpx.Client")
    def test_make_request_success(self, mock_client_class):
        """Тест успішного запиту"""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        # Створюємо клієнт (httpx.Client буде mock)
        client = BaseClient(api_key="test-key")
        client._client = mock_instance
        
        # Виконуємо запит
        result = client._make_request("POST", "/test", json={"data": "test"})
        
        # Перевірки
        assert result == {"result": "success"}
        mock_instance.request.assert_called_once()
    
    @patch("httpx.Client")
    def test_make_request_with_params(self, mock_client_class):
        """Тест запиту з query параметрами"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key")
        client._client = mock_instance
        
        result = client._make_request(
            "GET",
            "/test",
            params={"limit": 10}
        )
        
        # Перевірка що params передано
        call_kwargs = mock_instance.request.call_args[1]
        assert call_kwargs["params"] == {"limit": 10}
    
    @patch("httpx.Client")
    def test_make_request_forms_correct_url(self, mock_client_class):
        """Тест що URL формується правильно"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key")
        client._client = mock_instance
        
        client._make_request("GET", "/test/path")
        
        # Перевірка URL
        call_kwargs = mock_instance.request.call_args[1]
        assert call_kwargs["url"] == "https://www.fridayai.online/api/test/path"
    
    @patch("httpx.Client")
    def test_make_request_adds_auth_header(self, mock_client_class):
        """Тест що додається X-User-Token header"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="secret-key-123")
        client._client = mock_instance
        
        client._make_request("GET", "/test")
        
        # Перевірка headers
        call_kwargs = mock_instance.request.call_args[1]
        assert call_kwargs["headers"]["X-User-Token"] == "secret-key-123"


class TestMakeRequestRetry:
    """Тести для retry логіки в _make_request"""
    
    @patch("httpx.Client")
    @patch("time.sleep")  # Mock sleep щоб тести були швидкі
    def test_retry_on_503(self, mock_sleep, mock_client_class):
        """Тест retry при 503"""
        # Перші 2 спроби - 503, 3-я - успіх
        mock_responses = [
            Mock(status_code=503, headers={}, json=lambda: {"error": "Down"}),
            Mock(status_code=503, headers={}, json=lambda: {"error": "Down"}),
            Mock(status_code=200, json=lambda: {"result": "success"}),
        ]
        
        mock_instance = Mock()
        mock_instance.request.side_effect = mock_responses
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key", max_retries=3)
        client._client = mock_instance
        
        result = client._make_request("GET", "/test")
        
        # Перевірки
        assert result == {"result": "success"}
        assert mock_instance.request.call_count == 3
        assert mock_sleep.call_count == 2  # 2 sleeps між 3 спробами
    
    @patch("httpx.Client")
    @patch("time.sleep")
    def test_no_retry_on_401(self, mock_sleep, mock_client_class):
        """Тест що НЕ retry при 401"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_response.json.return_value = {"error": "Unauthorized"}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key")
        client._client = mock_instance
        
        with pytest.raises(AuthenticationError):
            client._make_request("GET", "/test")
        
        # Тільки 1 спроба
        assert mock_instance.request.call_count == 1
        mock_sleep.assert_not_called()
    
    @patch("httpx.Client")
    @patch("time.sleep")
    def test_exponential_backoff(self, mock_sleep, mock_client_class):
        """Тест exponential backoff"""
        # Всі спроби - 503
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.headers = {}
        mock_response.json.return_value = {"error": "Down"}
        
        mock_instance = Mock()
        mock_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key", max_retries=3)
        client._client = mock_instance
        
        with pytest.raises(ServiceUnavailableError):
            client._make_request("GET", "/test")
        
        # Перевірка exponential backoff: 1s, 2s, 4s
        assert mock_sleep.call_count == 3
        sleep_times = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_times == [1, 2, 4]


class TestContextManager:
    """Тести для context manager"""
    
    @patch("httpx.Client")
    def test_context_manager(self, mock_client_class):
        """Тест що context manager працює"""
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        with BaseClient(api_key="test-key") as client:
            assert client.api_key == "test-key"
        
        # Перевірка що close() викликано
        mock_instance.close.assert_called_once()
    
    @patch("httpx.Client")
    def test_close_method(self, mock_client_class):
        """Тест close() методу"""
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        client = BaseClient(api_key="test-key")
        client.close()
        
        mock_instance.close.assert_called_once()


class TestAsyncClient:
    """Тести для AsyncClient"""
    
    def test_async_client_init(self):
        """Тест ініціалізації AsyncClient"""
        client = AsyncClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://www.fridayai.online/api"
        assert client._client is None  # Створюється при першому запиті
    
    @pytest.mark.asyncio
    async def test_async_client_aclose(self):
        """Тест aclose() методу"""
        client = AsyncClient(api_key="test-key")
        
        # Mock async client
        mock_async_client = Mock()
        mock_async_client.aclose = AsyncMock(return_value=None)
        client._client = mock_async_client
        
        await client.aclose()
        
        assert client._client is None


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])