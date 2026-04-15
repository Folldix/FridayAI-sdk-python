"""
Базовий HTTP клієнт для FridayAI SDK.

Цей модуль забезпечує низькорівневу взаємодію з FridayAI API:
- HTTP запити через httpx
- Автентифікація через X-User-Token header
- Обробка помилок та retry логіка
- Підтримка синхронного та асинхронного режимів
- Logging для debugging

Приклад використання:
    >>> from friday._client import BaseClient
    >>> client = BaseClient(api_key="sk-...")
    >>> response = client._make_request("POST", "/chat/completions", json={...})
"""

import time
import logging
from typing import Dict, Any, Optional, Union, Iterator
from contextlib import contextmanager

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for FridayAI SDK. "
        "Install it with: pip install httpx"
    )

from _exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    ServiceUnavailableError,
    make_error_from_response,
    handle_httpx_error,
)

# Версія SDK (буде імпортуватись з _version.py)
__version__ = "0.1.0"

# Налаштування logging
logger = logging.getLogger("friday.client")


class BaseClient:
    """
    Базовий синхронний HTTP клієнт для FridayAI API.
    
    Забезпечує низькорівневі HTTP запити з автоматичною автентифікацією,
    обробкою помилок та retry логікою.
    
    Attributes:
        api_key: API ключ для автентифікації
        base_url: Базовий URL API
        timeout: Таймаут запитів в секундах
        max_retries: Максимальна кількість повторів при помилках
        
    Example:
        >>> client = BaseClient(api_key="sk-...")
        >>> response = client._make_request(
        ...     "POST",
        ...     "/chat/completions",
        ...     json={"conversation": [...], "model": "friday_big"}
        ... )
        >>> print(response)
    """
    
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.fridayai.online/api",
        timeout: float = 300.0,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Ініціалізує базовий HTTP клієнт.
        
        Args:
            api_key: API ключ для автентифікації (обов'язковий)
            base_url: Базовий URL API (за замовчуванням FridayAI API)
            timeout: Таймаут запитів в секундах (300s = 5 хвилин)
            max_retries: Максимальна кількість повторів при тимчасових помилках
            default_headers: Додаткові HTTP заголовки для всіх запитів
            
        Raises:
            ValueError: Якщо API ключ не вказано
            
        Example:
            >>> client = BaseClient(
            ...     api_key="sk-abc123",
            ...     timeout=60.0,
            ...     max_retries=3
            ... )
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        
        # Створюємо httpx клієнт
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
        
        logger.debug(
            "BaseClient initialized",
            extra={
                "base_url": self.base_url,
                "timeout": self.timeout,
                "max_retries": self.max_retries,
            }
        )
    
    def _prepare_headers(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Підготовка HTTP заголовків для запиту.
        
        Автоматично додає:
        - X-User-Token для автентифікації
        - Content-Type: application/json
        - User-Agent з версією SDK
        
        Args:
            headers: Додаткові заголовки для цього запиту
            
        Returns:
            Об'єднані заголовки
            
        Example:
            >>> headers = client._prepare_headers({"X-Custom": "value"})
            >>> assert "X-User-Token" in headers
        """
        # Базові заголовки
        prepared = {
            "X-User-Token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"friday-python/{__version__}",
        }
        
        # Додаємо default headers
        prepared.update(self.default_headers)
        
        # Додаємо headers для цього запиту
        if headers:
            prepared.update(headers)
        
        return prepared
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Обробка HTTP відповіді.
        
        Перевіряє статус код та парсить JSON. При помилках створює
        відповідні exception класи.
        
        Args:
            response: HTTP відповідь від httpx
            
        Returns:
            Розпарсений JSON як dict
            
        Raises:
            APIError: При будь-якій помилці API (400+)
            
        Example:
            >>> response = httpx.get(...)
            >>> data = client._handle_response(response)
        """
        # Успішна відповідь (200-299)
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except Exception as e:
                logger.error(
                    "Failed to parse JSON response",
                    extra={
                        "status_code": response.status_code,
                        "content": response.text[:200],
                    }
                )
                raise APIError(
                    f"Failed to parse JSON response: {str(e)}",
                    status_code=response.status_code,
                    response=response,
                )
        
        # Помилка (400+)
        raise make_error_from_response(response)
    
    def _should_retry(
        self,
        error: Exception,
        attempt: int
    ) -> bool:
        """
        Визначає чи потрібно повторити запит при помилці.
        
        Retry виконується для тимчасових помилок:
        - ServiceUnavailableError (503)
        - InternalServerError (500) - обмежено
        - APITimeoutError
        - APIConnectionError
        
        Args:
            error: Exception що виникла
            attempt: Номер поточної спроби (0-based)
            
        Returns:
            True якщо потрібно retry, False якщо ні
            
        Example:
            >>> error = ServiceUnavailableError("Down")
            >>> should_retry = client._should_retry(error, 0)
            >>> assert should_retry is True
        """
        # Перевищено максимальну кількість спроб
        if attempt >= self.max_retries:
            return False
        
        # Retry для тимчасових помилок
        retryable_errors = (
            ServiceUnavailableError,
            APITimeoutError,
            APIConnectionError,
        )
        
        # InternalServerError - retry тільки 1 раз
        if isinstance(error, InternalServerError):
            return attempt == 0
        
        return isinstance(error, retryable_errors)
    
    def _make_request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Виконання HTTP запиту до API.
        
        Основний метод для всіх HTTP операцій. Автоматично:
        - Додає автентифікацію
        - Обробляє помилки
        - Виконує retry при необхідності
        - Логує запити/відповіді
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, etc.)
            path: URL path (без base_url)
            json: JSON body для запиту
            params: Query параметри
            headers: Додаткові HTTP заголовки
            files: Файли для завантаження
            stream: Повернути streaming response (для SSE)
            **kwargs: Додаткові параметри для httpx
            
        Returns:
            JSON response як dict (або httpx.Response якщо stream=True)
            
        Raises:
            APIError: При помилках API
            APIConnectionError: При мережевих помилках
            APITimeoutError: При таймаутах
            
        Example:
            >>> response = client._make_request(
            ...     "POST",
            ...     "/chat/completions",
            ...     json={"conversation": [...]}
            ... )
            >>> print(response["response"])
        """
        # Формуємо повний URL
        url = f"{self.base_url}{path}"
        
        # Підготовка заголовків
        prepared_headers = self._prepare_headers(headers)
        
        # Логування запиту (без sensitive даних)
        safe_headers = {
            k: ("***" if k == "X-User-Token" else v)
            for k, v in prepared_headers.items()
        }
        logger.debug(
            "Making request",
            extra={
                "method": method,
                "url": url,
                "headers": safe_headers,
                "has_json": json is not None,
                "has_params": params is not None,
            }
        )
        
        # Retry логіка
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                # Виконання запиту
                start_time = time.time()
                
                response = self._client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=prepared_headers,
                    files=files,
                    **kwargs
                )
                
                elapsed = time.time() - start_time
                
                # Логування успішного запиту
                logger.info(
                    "Request completed",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "elapsed": f"{elapsed:.2f}s",
                    }
                )
                
                # Якщо streaming - повертаємо response
                if stream:
                    return response
                
                # Обробка відповіді
                return self._handle_response(response)
            
            except httpx.HTTPError as e:
                # Конвертуємо httpx помилки у FridayAI помилки
                friday_error = handle_httpx_error(e, timeout=self.timeout)
                last_error = friday_error
                
                # Перевіряємо чи потрібно retry
                if not self._should_retry(friday_error, attempt):
                    logger.error(
                        "Request failed (no retry)",
                        extra={
                            "method": method,
                            "url": url,
                            "error": str(friday_error),
                            "attempt": attempt + 1,
                        }
                    )
                    raise friday_error
                
                # Exponential backoff
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "Request failed, retrying",
                        extra={
                            "method": method,
                            "url": url,
                            "error": str(friday_error),
                            "attempt": attempt + 1,
                            "wait_time": wait_time,
                        }
                    )
                    time.sleep(wait_time)
            
            except APIError as e:
                # API помилки (400, 401, 429, etc.)
                last_error = e
                
                # Перевіряємо чи потрібно retry
                if not self._should_retry(e, attempt):
                    logger.error(
                        "API error (no retry)",
                        extra={
                            "method": method,
                            "url": url,
                            "status_code": e.status_code,
                            "error": e.message,
                            "request_id": e.request_id,
                        }
                    )
                    raise
                
                # Retry з backoff
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "API error, retrying",
                        extra={
                            "method": method,
                            "url": url,
                            "error": e.message,
                            "attempt": attempt + 1,
                            "wait_time": wait_time,
                        }
                    )
                    time.sleep(wait_time)
        
        # Якщо всі retry вичерпано
        logger.error(
            "Request failed after all retries",
            extra={
                "method": method,
                "url": url,
                "max_retries": self.max_retries,
            }
        )
        raise last_error
    
    def close(self) -> None:
        """
        Закриває HTTP клієнт та звільняє ресурси.
        
        Рекомендується викликати після завершення роботи з клієнтом
        або використовувати context manager.
        
        Example:
            >>> client = BaseClient(api_key="...")
            >>> try:
            ...     response = client._make_request(...)
            ... finally:
            ...     client.close()
        """
        self._client.close()
        logger.debug("BaseClient closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - автоматично закриває клієнт."""
        self.close()
        return False
    
    def __del__(self):
        """Destructor - закриває клієнт при видаленні об'єкта."""
        try:
            self.close()
        except Exception:
            pass


class AsyncClient:
    """
    Асинхронний HTTP клієнт для FridayAI API.
    
    Забезпечує ті самі можливості що й BaseClient, але з async/await.
    
    Attributes:
        api_key: API ключ для автентифікації
        base_url: Базовий URL API
        timeout: Таймаут запитів в секундах
        max_retries: Максимальна кількість повторів
        
    Example:
        >>> import asyncio
        >>> async def main():
        ...     client = AsyncClient(api_key="sk-...")
        ...     response = await client._make_request(
        ...         "POST",
        ...         "/chat/completions",
        ...         json={...}
        ...     )
        ...     print(response)
        >>> asyncio.run(main())
    """
    
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.fridayai.online/api",
        timeout: float = 300.0,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Ініціалізує асинхронний HTTP клієнт.
        
        Args:
            api_key: API ключ для автентифікації
            base_url: Базовий URL API
            timeout: Таймаут запитів в секундах
            max_retries: Максимальна кількість повторів
            default_headers: Додаткові HTTP заголовки
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        
        # AsyncClient створюється при першому запиті
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.debug(
            "AsyncClient initialized",
            extra={
                "base_url": self.base_url,
                "timeout": self.timeout,
            }
        )
    
    def _get_client(self) -> httpx.AsyncClient:
        """Отримує або створює httpx.AsyncClient."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
            )
        return self._client
    
    def _prepare_headers(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Підготовка HTTP заголовків (аналогічно BaseClient)."""
        prepared = {
            "X-User-Token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"friday-python/{__version__}",
        }
        
        prepared.update(self.default_headers)
        
        if headers:
            prepared.update(headers)
        
        return prepared
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Обробка HTTP відповіді (аналогічно BaseClient)."""
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except Exception as e:
                logger.error("Failed to parse JSON response")
                raise APIError(
                    f"Failed to parse JSON response: {str(e)}",
                    status_code=response.status_code,
                    response=response,
                )
        
        raise make_error_from_response(response)
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Визначає чи потрібно retry (аналогічно BaseClient)."""
        if attempt >= self.max_retries:
            return False
        
        retryable_errors = (
            ServiceUnavailableError,
            APITimeoutError,
            APIConnectionError,
        )
        
        if isinstance(error, InternalServerError):
            return attempt == 0
        
        return isinstance(error, retryable_errors)
    
    async def _make_request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Асинхронне виконання HTTP запиту.
        
        Args:
            method: HTTP метод
            path: URL path
            json: JSON body
            params: Query параметри
            headers: HTTP заголовки
            files: Файли
            stream: Streaming response
            **kwargs: Додаткові параметри
            
        Returns:
            JSON response або httpx.Response
            
        Example:
            >>> response = await client._make_request("GET", "/health")
        """
        client = self._get_client()
        url = f"{self.base_url}{path}"
        prepared_headers = self._prepare_headers(headers)
        
        # Логування
        safe_headers = {
            k: ("***" if k == "X-User-Token" else v)
            for k, v in prepared_headers.items()
        }
        logger.debug(
            "Making async request",
            extra={
                "method": method,
                "url": url,
                "headers": safe_headers,
            }
        )
        
        # Retry логіка
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                response = await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=prepared_headers,
                    files=files,
                    **kwargs
                )
                
                elapsed = time.time() - start_time
                
                logger.info(
                    "Async request completed",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "elapsed": f"{elapsed:.2f}s",
                    }
                )
                
                if stream:
                    return response
                
                return self._handle_response(response)
            
            except httpx.HTTPError as e:
                friday_error = handle_httpx_error(e, timeout=self.timeout)
                last_error = friday_error
                
                if not self._should_retry(friday_error, attempt):
                    logger.error("Async request failed (no retry)")
                    raise friday_error
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(
                        "Async request failed, retrying",
                        extra={"wait_time": wait_time}
                    )
                    import asyncio
                    await asyncio.sleep(wait_time)
            
            except APIError as e:
                last_error = e
                
                if not self._should_retry(e, attempt):
                    logger.error("API error (no retry)")
                    raise
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning("API error, retrying")
                    import asyncio
                    await asyncio.sleep(wait_time)
        
        logger.error("Async request failed after all retries")
        raise last_error
    
    async def aclose(self) -> None:
        """
        Закриває асинхронний HTTP клієнт.
        
        Example:
            >>> await client.aclose()
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        logger.debug("AsyncClient closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
        return False


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "BaseClient",
    "AsyncClient",
]