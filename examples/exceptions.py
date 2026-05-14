"""
Приклади використання системи виключень FridayAI SDK

Цей файл демонструє різні сценарії обробки помилок.
"""

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time
import logging
from typing import Optional, Callable, Any

# Імпортуємо наші exception класи
# В реальному використанні: from friday.exceptions import ...
from friday._exceptions import (
    FridayError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    BadRequestError,
    RateLimitError,
    InternalServerError,
    ServiceUnavailableError,
    APIConnectionError,
    APITimeoutError,
    ValidationError,
)


# ============================================================================
# Приклад 1: Базова обробка помилок
# ============================================================================

def example_basic_error_handling():
    """
    Демонструє базову обробку помилок при роботі з SDK.
    """
    print("=" * 60)
    print("Приклад 1: Базова обробка помилок")
    print("=" * 60)
    
    # Симуляція виклику API (в реальності це буде client.chat.completions.create())
    def simulate_api_call():
        # Для прикладу створимо помилку автентифікації
        raise AuthenticationError(
            "Invalid API key provided",
            status_code=401,
            headers={"x-request-id": "req-12345"}
        )
    
    try:
        response = simulate_api_call()
        print(f"Response: {response}")
    
    except AuthenticationError as e:
        print(f"ERROR: Authentication failed: {e.message}")
        print(f"   Status code: {e.status_code}")
        print(f"   Request ID: {e.request_id}")
        print(f"   Tip: Check your API key at https://fridayai.online/settings")
    
    except APIError as e:
        print(f"ERROR: API error: {e.message}")
        print(f"   Status: {e.status_code}")
    
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
    
    print()


# ============================================================================
# Приклад 2: Обробка Rate Limit з retry логікою
# ============================================================================

def example_rate_limit_with_retry():
    """
    Демонструє обробку rate limit помилок з автоматичним retry.
    """
    print("=" * 60)
    print("Приклад 2: Rate Limit з retry логікою")
    print("=" * 60)
    
    def simulate_api_with_rate_limit(attempt: int):
        """Симулює API call що може повернути rate limit"""
        if attempt < 2:
            # Перші 2 спроби - rate limit
            raise RateLimitError(
                "Rate limit exceeded for chat endpoint",
                status_code=429,
                headers={"retry-after": "5"},
                body={
                    "limit_type": "chat",
                    "current_usage": 100,
                    "limit": 100,
                    "retry_after": 5
                }
            )
        else:
            # 3-я спроба успішна
            return {"response": "Success!"}
    
    def call_with_retry(max_retries: int = 3) -> Optional[dict]:
        """Виклик з retry логікою"""
        for attempt in range(max_retries):
            try:
                print(f"Retry attempt {attempt + 1}/{max_retries}...")
                result = simulate_api_with_rate_limit(attempt)
                print(f"Success: {result}")
                return result
            
            except RateLimitError as e:
                print(f"WARNING: Rate limit hit: {e.message}")
                print(f"   Usage: {e.current_usage}/{e.limit}")
                
                if attempt == max_retries - 1:
                    # Останній retry - викидаємо помилку
                    print(f"ERROR: Max retries reached. Giving up.")
                    raise
                
                # Чекаємо перед наступною спробою
                wait_time = e.retry_after or 10
                print(f"   Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return None
    
    try:
        result = call_with_retry()
    except RateLimitError as e:
        print(f"ERROR: Failed after all retries: {e}")
    
    print()


# ============================================================================
# Приклад 3: Обробка validation помилок
# ============================================================================

def example_validation_errors():
    """
    Демонструє обробку validation помилок від API.
    """
    print("=" * 60)
    print("Приклад 3: Validation помилки")
    print("=" * 60)
    
    def simulate_bad_request():
        """Симулює помилку валідації"""
        raise BadRequestError(
            "Invalid request parameters",
            status_code=400,
            body={
                "validation_errors": [
                    "Field 'messages' is required",
                    "Field 'messages' cannot be empty",
                    "Field 'model' must be one of: friday_medium, friday_big"
                ]
            }
        )
    
    try:
        simulate_bad_request()
    
    except BadRequestError as e:
        print(f"ERROR: Bad request: {e.message}")
        
        if e.validation_errors:
            print(f"   Validation errors ({len(e.validation_errors)}):")
            for i, error in enumerate(e.validation_errors, 1):
                print(f"   {i}. {error}")
        
        print(f"\n   Tip: Check your request parameters")
    
    print()


# ============================================================================
# Приклад 4: Обробка мережевих помилок
# ============================================================================

def example_network_errors():
    """
    Демонструє обробку мережевих помилок та таймаутів.
    """
    print("=" * 60)
    print("Приклад 4: Мережеві помилки")
    print("=" * 60)
    
    # Приклад 4.1: Connection Error
    print("\n4.1 Connection Error:")
    try:
        raise APIConnectionError(
            "Failed to connect to API server",
            original_error=ConnectionError("Network is unreachable")
        )
    except APIConnectionError as e:
        print(f"ERROR: Connection failed: {e.message}")
        if e.original_error:
            print(f"   Details: {e.original_error}")
        print(f"   Tip: Check your internet connection")
    
    # Приклад 4.2: Timeout Error
    print("\n4.2 Timeout Error:")
    try:
        raise APITimeoutError(
            "Request timed out after 30 seconds",
            timeout=30.0
        )
    except APITimeoutError as e:
        print(f"ERROR: Request timed out: {e.message}")
        print(f"   Timeout: {e.timeout} seconds")
        print(f"   Tip: Try increasing the timeout or retry later")
    
    print()


# ============================================================================
# Приклад 5: Обробка server помилок з exponential backoff
# ============================================================================

def example_server_errors_with_backoff():
    """
    Демонструє обробку server помилок з exponential backoff.
    """
    print("=" * 60)
    print("Приклад 5: Server помилки з exponential backoff")
    print("=" * 60)
    
    def simulate_server_error(attempt: int):
        """Симулює server помилку"""
        if attempt < 3:
            raise InternalServerError(
                "Internal server error occurred",
                status_code=500
            )
        return {"response": "Finally worked!"}
    
    def call_with_exponential_backoff(max_retries: int = 4) -> Optional[dict]:
        """Виклик з exponential backoff"""
        for attempt in range(max_retries):
            try:
                print(f"Retry attempt {attempt + 1}/{max_retries}...")
                result = simulate_server_error(attempt)
                print(f"Success: {result}")
                return result
            
            except (InternalServerError, ServiceUnavailableError) as e:
                print(f"WARNING: Server error: {e.message}")
                
                if attempt == max_retries - 1:
                    print(f"ERROR: Max retries reached.")
                    raise
                
                # Exponential backoff: 1s, 2s, 4s, 8s...
                wait_time = 2 ** attempt
                print(f"   Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return None
    
    try:
        result = call_with_exponential_backoff()
    except (InternalServerError, ServiceUnavailableError) as e:
        print(f"ERROR: Server error persists: {e}")
    
    print()


# ============================================================================
# Приклад 6: Детальний logging помилок
# ============================================================================

def example_error_logging():
    """
    Демонструє детальний logging помилок для debugging.
    """
    print("=" * 60)
    print("Приклад 6: Детальний logging помилок")
    print("=" * 60)
    
    # Налаштування logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    def simulate_api_error():
        """Симулює API помилку"""
        raise RateLimitError(
            "Daily chat limit reached",
            status_code=429,
            headers={
                "x-request-id": "req-abc123",
                "retry-after": "3600"
            },
            body={
                "limit_type": "chat",
                "current_usage": 500,
                "limit": 500
            }
        )
    
    try:
        simulate_api_error()
    
    except APIError as e:
        # Детальний logging
        logger.error(
            "API request failed",
            extra={
                "error_type": e.__class__.__name__,
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_message": e.message,
            }
        )
        
        # Спеціальна обробка для RateLimitError
        if isinstance(e, RateLimitError):
            logger.warning(
                "Rate limit information",
                extra={
                    "limit_type": e.limit_type,
                    "usage": e.current_usage,
                    "limit": e.limit,
                    "retry_after": e.retry_after,
                }
            )
    
    print()


# ============================================================================
# Приклад 7: Клієнт-side validation
# ============================================================================

def example_client_validation():
    """
    Демонструє валідацію на стороні клієнта перед відправкою запиту.
    """
    print("=" * 60)
    print("Приклад 7: Client-side validation")
    print("=" * 60)
    
    def validate_messages(messages):
        """Валідація messages перед API call"""
        if not messages:
            raise ValidationError(
                "Messages cannot be empty",
                field="messages"
            )
        
        if not isinstance(messages, list):
            raise ValidationError(
                f"Messages must be a list, got {type(messages).__name__}",
                field="messages",
                value=messages
            )
        
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise ValidationError(
                    f"Message at index {i} must be a dict",
                    field=f"messages[{i}]",
                    value=msg
                )
            
            if "role" not in msg:
                raise ValidationError(
                    f"Message at index {i} missing 'role' field",
                    field=f"messages[{i}].role"
                )
            
            if msg["role"] not in ["user", "assistant", "system"]:
                raise ValidationError(
                    f"Invalid role: {msg['role']}. Must be one of: user, assistant, system",
                    field=f"messages[{i}].role",
                    value=msg["role"]
                )
    
    # Тест 1: Порожній список
    print("\nТест 1: Порожній список messages")
    try:
        validate_messages([])
    except ValidationError as e:
        print(f"ERROR: Validation failed: {e.message}")
        print(f"   Field: {e.field}")
    
    # Тест 2: Невалідний тип
    print("\nТест 2: Невалідний тип messages")
    try:
        validate_messages("invalid")
    except ValidationError as e:
        print(f"ERROR: Validation failed: {e.message}")
        print(f"   Field: {e.field}")
        print(f"   Value: {e.value}")
    
    # Тест 3: Невалідна роль
    print("\nТест 3: Невалідна роль в message")
    try:
        validate_messages([
            {"role": "invalid_role", "content": "Hello"}
        ])
    except ValidationError as e:
        print(f"ERROR: Validation failed: {e.message}")
        print(f"   Field: {e.field}")
        print(f"   Value: {e.value}")
    
    # Тест 4: Валідні messages
    print("\nТест 4: Валідні messages")
    try:
        validate_messages([
            {"role": "user", "content": "Hello"}
        ])
        print("Validation passed!")
    except ValidationError as e:
        print(f"ERROR: Unexpected validation error: {e}")
    
    print()


# ============================================================================
# Приклад 8: Catch всіх FridayAI помилок
# ============================================================================

def example_catch_all_friday_errors():
    """
    Демонструє як ловити всі FridayAI помилки одночасно.
    """
    print("=" * 60)
    print("Приклад 8: Catch всіх FridayAI помилок")
    print("=" * 60)
    
    def simulate_random_error(error_type: str):
        """Симулює різні типи помилок"""
        errors = {
            "auth": AuthenticationError("Invalid API key"),
            "rate": RateLimitError("Rate limit exceeded"),
            "connection": APIConnectionError("Connection failed"),
            "timeout": APITimeoutError("Request timeout"),
            "validation": ValidationError("Invalid input"),
        }
        raise errors.get(error_type, FridayError("Unknown error"))
    
    error_types = ["auth", "rate", "connection", "timeout", "validation"]
    
    for error_type in error_types:
        try:
            print(f"\nTesting {error_type} error...")
            simulate_random_error(error_type)
        
        except FridayError as e:
            # Ловимо всі FridayAI помилки
            error_name = e.__class__.__name__
            print(f"ERROR: Caught {error_name}: {e.message}")
            
            # Можна додати специфічну обробку для певних типів
            if isinstance(e, RateLimitError):
                print(f"   -> This is a rate limit error")
            elif isinstance(e, APIConnectionError):
                print(f"   -> This is a connection error")
    
    print()


# ============================================================================
# Приклад 9: Контекстний менеджер для обробки помилок
# ============================================================================

class ErrorHandler:
    """
    Контекстний менеджер для зручної обробки помилок.
    """
    
    def __init__(self, operation_name: str, retry: bool = False):
        self.operation_name = operation_name
        self.retry = retry
    
    def __enter__(self):
        print(f"\nStarting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"Completed: {self.operation_name}")
            return True
        
        if issubclass(exc_type, FridayError):
            print(f"ERROR: Failed: {self.operation_name}")
            print(f"   Error: {exc_val}")
            
            if isinstance(exc_val, RateLimitError) and self.retry:
                print(f"   Will retry after {exc_val.retry_after}s")
            
            # Suppress exception (не прокидувати далі)
            return True
        
        # Не FridayError - прокидуємо далі
        return False


def example_context_manager():
    """
    Демонструє використання контекстного менеджера для помилок.
    """
    print("=" * 60)
    print("Приклад 9: Контекстний менеджер")
    print("=" * 60)
    
    with ErrorHandler("Chat completion"):
        raise AuthenticationError("Invalid API key")
    
    with ErrorHandler("Image generation", retry=True):
        raise RateLimitError(
            "Rate limit",
            headers={"retry-after": "60"}
        )
    
    with ErrorHandler("Successful operation"):
        print("   Operation in progress...")
        # Все ОК, помилки немає
    
    print()


# ============================================================================
# Головна функція
# ============================================================================

def main():
    """
    Запускає всі приклади.
    """
    print("\n" + "=" * 60)
    print(" FridayAI SDK - Приклади обробки помилок")
    print("=" * 60 + "\n")
    
    examples = [
        example_basic_error_handling,
        example_rate_limit_with_retry,
        example_validation_errors,
        example_network_errors,
        example_server_errors_with_backoff,
        example_error_logging,
        example_client_validation,
        example_catch_all_friday_errors,
        example_context_manager,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"WARNING: Example failed with unexpected error: {e}")
            print()
    
    print("=" * 60)
    print(" Всі приклади виконано!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
