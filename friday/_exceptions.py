"""
Система виключень для FridayAI SDK.

Цей модуль визначає всі exception класи, які використовуються в SDK для
обробки помилок API, мережевих проблем та валідації даних.

Приклад використання:
    >>> from friday import Friday
    >>> from friday.exceptions import APIError, RateLimitError
    >>> 
    >>> client = Friday(api_key="sk-...")
    >>> try:
    ...     response = client.chat.completions.create(
    ...         messages=[{"role": "user", "content": "Hello"}]
    ...     )
    ... except RateLimitError as e:
    ...     print(f"Rate limit exceeded. Retry after {e.retry_after}s")
    ... except APIError as e:
    ...     print(f"API error: {e.message} (status: {e.status_code})")
"""

from typing import Optional, Dict, Any, Type
import json


class FridayError(Exception):
    """
    Базовий клас для всіх помилок FridayAI SDK.
    
    Всі кастомні exceptions наслідуються від FridayError для зручної обробки
    всіх помилок SDK одночасно.
    
    Attributes:
        message: Повідомлення про помилку
        
    Example:
        >>> try:
        ...     client.chat.completions.create(...)
        ... except FridayError as e:
        ...     print(f"FridayAI SDK error: {e}")
    """
    
    def __init__(self, message: str) -> None:
        """
        Ініціалізує FridayError.
        
        Args:
            message: Повідомлення про помилку
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Повертає строкове представлення помилки."""
        return self.message
    
    def __repr__(self) -> str:
        """Повертає технічне представлення помилки."""
        return f"{self.__class__.__name__}(message={self.message!r})"


class APIError(FridayError):
    """
    Базовий клас для всіх помилок API.
    
    Містить інформацію про HTTP статус, тіло відповіді та заголовки.
    Автоматично витягує корисну інформацію з response (request_id, error message).
    
    Attributes:
        message: Повідомлення про помилку
        status_code: HTTP статус код (400, 401, 429, etc.)
        response: Повна відповідь від API (для debugging)
        headers: HTTP заголовки відповіді
        request_id: ID запиту з заголовку x-request-id (якщо присутній)
        body: Тіло відповіді (parsed JSON або raw text)
    
    Example:
        >>> try:
        ...     response = client.chat.completions.create(...)
        ... except APIError as e:
        ...     print(f"API error: {e.message}")
        ...     print(f"Status: {e.status_code}")
        ...     print(f"Request ID: {e.request_id}")
        ...     print(f"Full response: {e.body}")
    """
    
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Ініціалізує APIError.
        
        Args:
            message: Повідомлення про помилку
            status_code: HTTP статус код
            response: HTTP response об'єкт
            headers: HTTP заголовки
            body: Тіло відповіді (dict)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.headers = headers or {}
        self.body = body
        
        # Витягуємо request_id з заголовків якщо є
        self.request_id = self.headers.get("x-request-id")
    
    def __repr__(self) -> str:
        """Повертає технічне представлення помилки з деталями."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )
    
    @classmethod
    def from_response(
        cls,
        response: Any,
        *,
        message: Optional[str] = None,
    ) -> "APIError":
        """
        Створює відповідний APIError з HTTP відповіді.
        
        Автоматично визначає правильний підклас помилки на основі статус коду
        та витягує повідомлення про помилку з тіла відповіді.
        
        Args:
            response: HTTP response об'єкт (httpx.Response)
            message: Кастомне повідомлення (якщо None, береться з response body)
        
        Returns:
            Відповідний APIError підклас (AuthenticationError, RateLimitError, etc.)
            
        Example:
            >>> response = httpx.post(...)
            >>> if response.status_code >= 400:
            ...     raise APIError.from_response(response)
        """
        status_code = response.status_code
        headers = dict(response.headers)
        
        # Спробуємо розпарсити JSON body
        try:
            body = response.json()
        except Exception:
            # Якщо не JSON, зберігаємо як text
            body = {"error": response.text}
        
        # Витягуємо повідомлення з body якщо не передано
        if message is None:
            # FridayAI API повертає помилки в полі "error"
            message = body.get("error", f"HTTP {status_code} error")
        
        # Вибираємо правильний клас помилки залежно від статус коду
        error_class = cls._get_error_class(status_code)
        
        return error_class(
            message=message,
            status_code=status_code,
            response=response,
            headers=headers,
            body=body,
        )
    
    @staticmethod
    def _get_error_class(status_code: int) -> Type["APIError"]:
        """
        Повертає правильний клас помилки для статус коду.
        
        Args:
            status_code: HTTP статус код
            
        Returns:
            Клас помилки (підклас APIError)
        """
        error_map = {
            400: BadRequestError,
            401: AuthenticationError,
            403: PermissionDeniedError,
            404: NotFoundError,
            409: ConflictError,
            422: UnprocessableEntityError,
            429: RateLimitError,
            500: InternalServerError,
            503: ServiceUnavailableError,
        }
        return error_map.get(status_code, APIError)


class AuthenticationError(APIError):
    """
    Помилка автентифікації (401).
    
    Викидається коли:
    - API ключ невалідний або відсутній
    - API ключ прострочений
    - Токен не має необхідних прав доступу
    
    Example:
        >>> client = Friday(api_key="invalid-key")
        >>> try:
        ...     client.chat.completions.create(
        ...         messages=[{"role": "user", "content": "Hello"}]
        ...     )
        ... except AuthenticationError as e:
        ...     print(f"Invalid API key: {e}")
        ...     print("Please check your API key at https://fridayai.online")
    """
    
    def __init__(self, message: str = "Authentication failed", **kwargs) -> None:
        """
        Ініціалізує AuthenticationError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри (status_code, headers, etc.)
        """
        super().__init__(message, **kwargs)


class PermissionDeniedError(APIError):
    """
    Помилка доступу (403).
    
    Викидається коли:
    - У користувача немає прав на цей ресурс
    - Токен валідний, але operation заборонена для цього користувача
    - Доступ до ресурсу обмежений
    
    Example:
        >>> try:
        ...     client.collections.delete("protected_collection")
        ... except PermissionDeniedError as e:
        ...     print(f"Access denied: {e}")
        ...     print("You don't have permission to delete this collection")
    """
    
    def __init__(self, message: str = "Permission denied", **kwargs) -> None:
        """
        Ініціалізує PermissionDeniedError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)


class NotFoundError(APIError):
    """
    Ресурс не знайдено (404).
    
    Викидається коли:
    - Запитуваний endpoint не існує
    - Ресурс (колекція, лог, файл) не знайдено
    - Невірний URL або ID ресурсу
    
    Example:
        >>> try:
        ...     client.collections.retrieve("nonexistent_collection")
        ... except NotFoundError as e:
        ...     print(f"Collection not found: {e}")
        ...     # Можна створити нову колекцію
        ...     client.collections.create("nonexistent_collection")
    """
    
    def __init__(self, message: str = "Resource not found", **kwargs) -> None:
        """
        Ініціалізує NotFoundError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)


class BadRequestError(APIError):
    """
    Невалідний запит (400).
    
    Викидається коли:
    - Невалідні параметри запиту
    - Відсутні обов'язкові поля
    - Некоректний формат даних
    - Синтаксична помилка в JSON
    
    Attributes:
        validation_errors: Список помилок валідації (якщо доступно)
    
    Example:
        >>> try:
        ...     # messages має бути список, не рядок
        ...     client.chat.completions.create(messages="invalid")
        ... except BadRequestError as e:
        ...     print(f"Invalid request: {e}")
        ...     if e.validation_errors:
        ...         print("Validation errors:")
        ...         for error in e.validation_errors:
        ...             print(f"  - {error}")
    """
    
    def __init__(self, message: str = "Bad request", **kwargs) -> None:
        """
        Ініціалізує BadRequestError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)
        
        # Витягуємо validation errors якщо є
        self.validation_errors = []
        if self.body and isinstance(self.body, dict):
            # API може повертати помилки в різних форматах
            if "validation_errors" in self.body:
                self.validation_errors = self.body["validation_errors"]
            elif "errors" in self.body:
                self.validation_errors = self.body["errors"]
            elif "details" in self.body:
                self.validation_errors = self.body["details"]


class ConflictError(APIError):
    """
    Конфлікт ресурсів (409).
    
    Викидається коли:
    - Спроба створити ресурс що вже існує
    - Конфлікт версій/станів ресурсу
    - Одночасна модифікація ресурсу
    
    Example:
        >>> try:
        ...     client.collections.create("existing_collection")
        ... except ConflictError as e:
        ...     print(f"Collection already exists: {e}")
        ...     # Можна використати існуючу або видалити і створити нову
    """
    
    def __init__(self, message: str = "Resource conflict", **kwargs) -> None:
        """
        Ініціалізує ConflictError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)


class UnprocessableEntityError(APIError):
    """
    Неможливо обробити сутність (422).
    
    Викидається коли:
    - Запит синтаксично правильний, але семантично некоректний
    - Validation пройшов, але бізнес-логіка відхилила запит
    - Параметри валідні, але комбінація невірна
    
    Example:
        >>> try:
        ...     # Порожній prompt не дозволений
        ...     client.images.generate(prompt="")
        ... except UnprocessableEntityError as e:
        ...     print(f"Invalid input: {e}")
        ...     print("Prompt cannot be empty")
    """
    
    def __init__(self, message: str = "Unprocessable entity", **kwargs) -> None:
        """
        Ініціалізує UnprocessableEntityError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)


class RateLimitError(APIError):
    """
    Перевищено ліміт запитів (429).
    
    Викидається коли:
    - Досягнуто денний ліміт для токену
    - Занадто багато запитів за короткий час
    - Вичерпано квоту на конкретну операцію
    
    Attributes:
        retry_after: Скільки секунд чекати перед наступним запитом (якщо доступно)
        limit_type: Тип ліміту ('chat', 'image', 'voice')
        current_usage: Поточне використання
        limit: Максимальний ліміт
    
    Example:
        >>> import time
        >>> try:
        ...     client.chat.completions.create(...)
        ... except RateLimitError as e:
        ...     print(f"Rate limit exceeded: {e}")
        ...     print(f"Usage: {e.current_usage}/{e.limit}")
        ...     if e.retry_after:
        ...         print(f"Please wait {e.retry_after} seconds")
        ...         time.sleep(e.retry_after)
        ...         # Повторити запит
    """
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs) -> None:
        """
        Ініціалізує RateLimitError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)
        
        # Спробуємо витягнути retry_after з headers
        self.retry_after = None
        if self.headers:
            retry_after_header = self.headers.get("retry-after")
            if retry_after_header:
                try:
                    self.retry_after = int(retry_after_header)
                except (ValueError, TypeError):
                    pass
        
        # Витягуємо додаткову інформацію з body
        self.limit_type = None
        self.current_usage = None
        self.limit = None
        
        if self.body and isinstance(self.body, dict):
            self.limit_type = self.body.get("limit_type")
            self.current_usage = self.body.get("current_usage")
            self.limit = self.body.get("limit")
            
            # Якщо retry_after не в headers, можливо в body
            if self.retry_after is None and "retry_after" in self.body:
                try:
                    self.retry_after = int(self.body["retry_after"])
                except (ValueError, TypeError):
                    pass


class InternalServerError(APIError):
    """
    Внутрішня помилка сервера (500).
    
    Викидається коли:
    - Помилка на стороні сервера FridayAI
    - Неочікувана помилка при обробці запиту
    - Backend service недоступний
    
    Ця помилка зазвичай тимчасова і запит можна повторити.
    
    Example:
        >>> import time
        >>> max_retries = 3
        >>> for attempt in range(max_retries):
        ...     try:
        ...         response = client.chat.completions.create(...)
        ...         break
        ...     except InternalServerError as e:
        ...         if attempt == max_retries - 1:
        ...             raise
        ...         print(f"Server error, retrying... ({attempt + 1}/{max_retries})")
        ...         time.sleep(2 ** attempt)  # Exponential backoff
    """
    
    def __init__(
        self, 
        message: str = "Internal server error. Please try again later.", 
        **kwargs
    ) -> None:
        """
        Ініціалізує InternalServerError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)


class ServiceUnavailableError(APIError):
    """
    Сервіс недоступний (503).
    
    Викидається коли:
    - API тимчасово недоступний
    - Проводиться технічне обслуговування
    - Проблеми з підключенням до backend сервісів
    - Сервер перевантажений
    
    Attributes:
        retry_after: Скільки секунд чекати перед повтором (якщо доступно)
    
    Example:
        >>> import time
        >>> try:
        ...     client.chat.completions.create(...)
        ... except ServiceUnavailableError as e:
        ...     print(f"Service unavailable: {e}")
        ...     if e.retry_after:
        ...         print(f"Retrying after {e.retry_after} seconds...")
        ...         time.sleep(e.retry_after)
        ...         # Повторити запит
        ...     else:
        ...         print("Please try again later")
    """
    
    def __init__(
        self, 
        message: str = "Service temporarily unavailable", 
        **kwargs
    ) -> None:
        """
        Ініціалізує ServiceUnavailableError.
        
        Args:
            message: Повідомлення про помилку
            **kwargs: Додаткові параметри
        """
        super().__init__(message, **kwargs)
        
        # Витягуємо Retry-After header
        self.retry_after = None
        if self.headers:
            retry_after_header = self.headers.get("retry-after")
            if retry_after_header:
                try:
                    self.retry_after = int(retry_after_header)
                except (ValueError, TypeError):
                    pass


class APIConnectionError(FridayError):
    """
    Помилка підключення до API.
    
    Викидається коли:
    - Немає інтернет з'єднання
    - Неможливо підключитися до API сервера
    - DNS resolution failed
    - SSL/TLS помилки
    - Proxy помилки
    
    Attributes:
        original_error: Оригінальна помилка (наприклад httpx.ConnectError)
    
    Example:
        >>> try:
        ...     client.chat.completions.create(...)
        ... except APIConnectionError as e:
        ...     print(f"Connection failed: {e}")
        ...     print("Please check your internet connection")
        ...     if e.original_error:
        ...         print(f"Details: {e.original_error}")
    """
    
    def __init__(
        self, 
        message: str = "Connection error occurred",
        *,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Ініціалізує APIConnectionError.
        
        Args:
            message: Повідомлення про помилку
            original_error: Оригінальна exception (httpx.ConnectError, etc.)
        """
        super().__init__(message)
        self.original_error = original_error
    
    def __repr__(self) -> str:
        """Повертає технічне представлення з оригінальною помилкою."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"original_error={self.original_error!r})"
        )


class APITimeoutError(FridayError):
    """
    Таймаут запиту.
    
    Викидається коли:
    - Запит перевищив встановлений timeout
    - Відповідь від сервера надходить занадто довго
    - Read timeout (сервер не встиг відповісти)
    - Connection timeout (не вдалося встановити з'єднання)
    
    Attributes:
        timeout: Встановлений timeout в секундах
        original_error: Оригінальна помилка
    
    Example:
        >>> client = Friday(api_key="...", timeout=5.0)
        >>> try:
        ...     # Довгий запит може перевищити timeout
        ...     client.chat.completions.create(...)
        ... except APITimeoutError as e:
        ...     print(f"Request timed out after {e.timeout} seconds")
        ...     # Можна повторити з більшим timeout
        ...     client_with_longer_timeout = Friday(api_key="...", timeout=30.0)
    """
    
    def __init__(
        self,
        message: str = "Request timed out",
        *,
        timeout: Optional[float] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Ініціалізує APITimeoutError.
        
        Args:
            message: Повідомлення про помилку
            timeout: Встановлений timeout в секундах
            original_error: Оригінальна exception
        """
        super().__init__(message)
        self.timeout = timeout
        self.original_error = original_error
    
    def __repr__(self) -> str:
        """Повертає технічне представлення з timeout."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"timeout={self.timeout})"
        )


class ValidationError(FridayError):
    """
    Помилка валідації на стороні клієнта.
    
    Викидається коли:
    - Невалідні типи параметрів (перед відправкою запиту)
    - Відсутні обов'язкові параметри
    - Параметри поза допустимими межами
    - Некоректний формат даних
    
    Attributes:
        field: Ім'я поля що викликало помилку
        value: Невалідне значення
    
    Example:
        >>> from friday.exceptions import ValidationError
        >>> 
        >>> def validate_model(model):
        ...     valid_models = ["friday_medium", "friday_big"]
        ...     if model not in valid_models:
        ...         raise ValidationError(
        ...             f"Invalid model: {model}. Must be one of {valid_models}",
        ...             field="model",
        ...             value=model
        ...         )
        >>> 
        >>> try:
        ...     validate_model("gpt-4")
        ... except ValidationError as e:
        ...     print(f"Validation error: {e}")
        ...     print(f"Field: {e.field}")
        ...     print(f"Invalid value: {e.value}")
    """
    
    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> None:
        """
        Ініціалізує ValidationError.
        
        Args:
            message: Повідомлення про помилку
            field: Ім'я поля що викликало помилку
            value: Невалідне значення
        """
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __repr__(self) -> str:
        """Повертає технічне представлення з полем та значенням."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"field={self.field!r}, "
            f"value={self.value!r})"
        )


# ============================================================================
# Helper функції
# ============================================================================


def make_error_from_response(response: Any) -> APIError:
    """
    Створює відповідну помилку з HTTP response.
    
    Це головна функція для конвертації HTTP відповідей у типізовані помилки.
    Автоматично визначає правильний клас помилки на основі статус коду.
    
    Args:
        response: HTTP response об'єкт (httpx.Response)
    
    Returns:
        Відповідний підклас APIError
    
    Example:
        >>> import httpx
        >>> response = httpx.post("https://api.fridayai.online/chat/completions", ...)
        >>> if response.status_code >= 400:
        ...     raise make_error_from_response(response)
    """
    return APIError.from_response(response)


def handle_httpx_error(error: Exception, timeout: Optional[float] = None) -> FridayError:
    """
    Конвертує httpx помилки у FridayAI помилки.
    
    Допоміжна функція для обробки мережевих помилок та таймаутів.
    Трансформує низькорівневі httpx exceptions у зрозумілі FridayError.
    
    Args:
        error: httpx exception
        timeout: Встановлений timeout (опціонально)
    
    Returns:
        Відповідний FridayError
        
    Example:
        >>> import httpx
        >>> try:
        ...     response = httpx.post(...)
        ... except httpx.TimeoutException as e:
        ...     raise handle_httpx_error(e, timeout=30.0)
        ... except httpx.ConnectError as e:
        ...     raise handle_httpx_error(e)
    """
    try:
        import httpx
    except ImportError:
        # Якщо httpx не встановлений, повертаємо generic помилку
        return APIConnectionError(
            message=f"Connection error: {str(error)}",
            original_error=error,
        )
    
    # Обробка різних типів httpx помилок
    if isinstance(error, httpx.TimeoutException):
        return APITimeoutError(
            message=f"Request timed out: {str(error)}",
            timeout=timeout,
            original_error=error,
        )
    
    elif isinstance(error, httpx.ConnectError):
        return APIConnectionError(
            message=f"Failed to connect to API: {str(error)}",
            original_error=error,
        )
    
    elif isinstance(error, httpx.ConnectTimeout):
        return APITimeoutError(
            message=f"Connection timeout: {str(error)}",
            timeout=timeout,
            original_error=error,
        )
    
    elif isinstance(error, httpx.ReadTimeout):
        return APITimeoutError(
            message=f"Read timeout: {str(error)}",
            timeout=timeout,
            original_error=error,
        )
    
    elif isinstance(error, httpx.WriteTimeout):
        return APITimeoutError(
            message=f"Write timeout: {str(error)}",
            timeout=timeout,
            original_error=error,
        )
    
    elif isinstance(error, httpx.PoolTimeout):
        return APITimeoutError(
            message=f"Connection pool timeout: {str(error)}",
            timeout=timeout,
            original_error=error,
        )
    
    elif isinstance(error, httpx.NetworkError):
        return APIConnectionError(
            message=f"Network error occurred: {str(error)}",
            original_error=error,
        )
    
    elif isinstance(error, httpx.ProxyError):
        return APIConnectionError(
            message=f"Proxy error: {str(error)}",
            original_error=error,
        )
    
    elif isinstance(error, httpx.TooManyRedirects):
        return APIConnectionError(
            message=f"Too many redirects: {str(error)}",
            original_error=error,
        )
    
    elif isinstance(error, httpx.HTTPStatusError):
        # HTTPStatusError має response, використаємо from_response
        return make_error_from_response(error.response)
    
    else:
        # Інші httpx помилки
        return APIConnectionError(
            message=f"HTTP error: {str(error)}",
            original_error=error,
        )


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    # Базові класи
    "FridayError",
    "APIError",
    
    # HTTP помилки
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "BadRequestError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    
    # Мережеві помилки
    "APIConnectionError",
    "APITimeoutError",
    
    # Валідація
    "ValidationError",
    
    # Helper функції
    "make_error_from_response",
    "handle_httpx_error",
]