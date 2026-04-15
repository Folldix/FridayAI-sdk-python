"""
Приклади використання HTTP клієнта FridayAI SDK

Демонструє різні способи використання BaseClient та AsyncClient.

ПРИМІТКА: Ці приклади показують концепції використання.
Для реального запуску потрібно встановити httpx: pip install httpx
"""

import sys
import os
import time
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Для демонстрації без httpx створюємо mock класи
class MockBaseClient:
    def __init__(self, api_key, base_url="https://www.fridayai.online/api", 
                 timeout=300.0, max_retries=2, default_headers=None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
    
    def _prepare_headers(self, headers=None):
        prepared = {
            "X-User-Token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "friday-python/0.1.0",
        }
        prepared.update(self.default_headers)
        if headers:
            prepared.update(headers)
        return prepared
    
    def _should_retry(self, error, attempt):
        from _exceptions import (
            ServiceUnavailableError,
            APITimeoutError,
            APIConnectionError,
            InternalServerError,
            AuthenticationError,
            RateLimitError,
        )
        
        if attempt >= self.max_retries:
            return False
        
        if isinstance(error, InternalServerError):
            return attempt == 0
        
        retryable = (ServiceUnavailableError, APITimeoutError, APIConnectionError)
        return isinstance(error, retryable)
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

class MockAsyncClient(MockBaseClient):
    async def aclose(self):
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.aclose()

# Використовуємо mock класи
BaseClient = MockBaseClient
AsyncClient = MockAsyncClient

from _exceptions import (
    FridayError,
    APIError,
    RateLimitError,
    ServiceUnavailableError,
    APITimeoutError,
)


# Налаштування logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
# Приклад 1: Базове використання
# ============================================================================

def example_basic_usage():
    """
    Демонструє базове використання BaseClient.
    """
    print("=" * 60)
    print("Приклад 1: Базове використання BaseClient")
    print("=" * 60)
    
    # Створюємо клієнт
    client = BaseClient(
        api_key="test-api-key",
        timeout=30.0
    )
    
    print(f"✅ Client створено")
    print(f"   Base URL: {client.base_url}")
    print(f"   Timeout: {client.timeout}s")
    print(f"   Max retries: {client.max_retries}")
    
    # В реальному використанні тут був би запит до API
    # response = client._make_request("POST", "/chat/completions", json={...})
    
    # Закриваємо клієнт
    client.close()
    print("✅ Client закрито\n")


# ============================================================================
# Приклад 2: Context Manager
# ============================================================================

def example_context_manager():
    """
    Демонструє використання context manager для автоматичного закриття.
    """
    print("=" * 60)
    print("Приклад 2: Context Manager")
    print("=" * 60)
    
    # З context manager - автоматичне закриття
    with BaseClient(api_key="test-key") as client:
        print("✅ Client створено в context manager")
        print(f"   API key: {client.api_key[:10]}...")
        
        # Тут можна робити запити
        # response = client._make_request(...)
    
    print("✅ Client автоматично закрито після виходу з блоку\n")


# ============================================================================
# Приклад 3: Кастомна конфігурація
# ============================================================================

def example_custom_configuration():
    """
    Демонструє кастомну конфігурацію клієнта.
    """
    print("=" * 60)
    print("Приклад 3: Кастомна конфігурація")
    print("=" * 60)
    
    # Клієнт з кастомними параметрами
    client = BaseClient(
        api_key="sk-custom-key",
        base_url="https://custom-api.com/v1",
        timeout=120.0,
        max_retries=5,
        default_headers={
            "X-Custom-Header": "CustomValue",
            "X-App-Version": "1.0.0"
        }
    )
    
    print("✅ Кастомний client створено:")
    print(f"   Base URL: {client.base_url}")
    print(f"   Timeout: {client.timeout}s")
    print(f"   Max retries: {client.max_retries}")
    print(f"   Default headers: {client.default_headers}")
    
    client.close()
    print()


# ============================================================================
# Приклад 4: Prepare Headers
# ============================================================================

def example_prepare_headers():
    """
    Демонструє роботу з headers.
    """
    print("=" * 60)
    print("Приклад 4: Prepare Headers")
    print("=" * 60)
    
    client = BaseClient(
        api_key="sk-test-123",
        default_headers={"X-Default": "default-value"}
    )
    
    # Дефолтні headers
    headers1 = client._prepare_headers()
    print("✅ Дефолтні headers:")
    for key, value in headers1.items():
        if key == "X-User-Token":
            value = value[:10] + "..."  # Не показуємо повний ключ
        print(f"   {key}: {value}")
    
    # З додатковими headers
    headers2 = client._prepare_headers(
        headers={"X-Request-ID": "req-123"}
    )
    print("\n✅ З додатковими headers:")
    print(f"   X-Request-ID: {headers2['X-Request-ID']}")
    
    client.close()
    print()


# ============================================================================
# Приклад 5: Обробка помилок
# ============================================================================

def example_error_handling():
    """
    Демонструє обробку різних типів помилок.
    """
    print("=" * 60)
    print("Приклад 5: Обробка помилок")
    print("=" * 60)
    
    client = BaseClient(api_key="test-key")
    
    # Симуляція різних помилок
    print("\n1. Authentication Error:")
    try:
        # В реальності це був би запит що повертає 401
        from _exceptions import AuthenticationError
        raise AuthenticationError("Invalid API key")
    except AuthenticationError as e:
        print(f"   ❌ {e.__class__.__name__}: {e.message}")
    
    print("\n2. Rate Limit Error:")
    try:
        from _exceptions import RateLimitError
        error = RateLimitError(
            "Rate limit exceeded",
            headers={"retry-after": "60"}
        )
        error.retry_after = 60
        raise error
    except RateLimitError as e:
        print(f"   ❌ {e.__class__.__name__}: {e.message}")
        print(f"   Retry after: {e.retry_after} seconds")
    
    print("\n3. Timeout Error:")
    try:
        from _exceptions import APITimeoutError
        raise APITimeoutError("Request timeout", timeout=30.0)
    except APITimeoutError as e:
        print(f"   ❌ {e.__class__.__name__}: {e.message}")
        print(f"   Timeout: {e.timeout}s")
    
    print("\n4. Generic API Error:")
    try:
        from _exceptions import APIError
        raise APIError(
            "API error occurred",
            status_code=500,
            headers={"x-request-id": "req-123"}
        )
    except APIError as e:
        print(f"   ❌ {e.__class__.__name__}: {e.message}")
        print(f"   Status: {e.status_code}")
        print(f"   Request ID: {e.request_id}")
    
    client.close()
    print()


# ============================================================================
# Приклад 6: Retry логіка
# ============================================================================

def example_retry_logic():
    """
    Демонструє retry логіку клієнта.
    """
    print("=" * 60)
    print("Приклад 6: Retry логіка")
    print("=" * 60)
    
    client = BaseClient(
        api_key="test-key",
        max_retries=3
    )
    
    # Тест _should_retry для різних помилок
    print("\nПеревірка _should_retry для різних помилок:\n")
    
    # ServiceUnavailableError - should retry
    error1 = ServiceUnavailableError("Service down")
    should_retry1 = client._should_retry(error1, 0)
    print(f"1. ServiceUnavailableError (attempt 0): {should_retry1} ✅")
    
    # APITimeoutError - should retry
    from _exceptions import APITimeoutError
    error2 = APITimeoutError("Timeout")
    should_retry2 = client._should_retry(error2, 0)
    print(f"2. APITimeoutError (attempt 0): {should_retry2} ✅")
    
    # AuthenticationError - should NOT retry
    from _exceptions import AuthenticationError
    error3 = AuthenticationError("Invalid key")
    should_retry3 = client._should_retry(error3, 0)
    print(f"3. AuthenticationError (attempt 0): {should_retry3} ❌")
    
    # RateLimitError - should NOT retry (користувач обробляє)
    error4 = RateLimitError("Rate limit")
    should_retry4 = client._should_retry(error4, 0)
    print(f"4. RateLimitError (attempt 0): {should_retry4} ❌")
    
    # Max retries exceeded
    error5 = ServiceUnavailableError("Down")
    should_retry5 = client._should_retry(error5, 3)  # Після 3 спроб
    print(f"5. ServiceUnavailableError (attempt 3): {should_retry5} ❌")
    
    client.close()
    print()


# ============================================================================
# Приклад 7: Async Client
# ============================================================================

async def example_async_client():
    """
    Демонструє використання AsyncClient.
    """
    print("=" * 60)
    print("Приклад 7: Async Client")
    print("=" * 60)
    
    # Створюємо async client
    async with AsyncClient(api_key="test-key") as client:
        print("✅ AsyncClient створено в async context manager")
        print(f"   Base URL: {client.base_url}")
        print(f"   Timeout: {client.timeout}s")
        
        # В реальності тут був би async запит
        # response = await client._make_request("POST", "/chat/completions", ...)
        
        print("✅ В async context - можна робити await запити")
    
    print("✅ AsyncClient автоматично закрито\n")


# ============================================================================
# Приклад 8: Logging
# ============================================================================

def example_logging():
    """
    Демонструє logging можливості.
    """
    print("=" * 60)
    print("Приклад 8: Logging")
    print("=" * 60)
    
    # Встановлюємо DEBUG рівень для детального logging
    logging.getLogger("friday.client").setLevel(logging.DEBUG)
    
    print("\n✅ Logging рівень встановлено на DEBUG")
    print("   Тепер всі запити будуть детально логуватись:\n")
    
    client = BaseClient(api_key="sk-secret-key")
    
    print("📝 Client створено - в логах буде інформація про ініціалізацію")
    
    # При реальному запиті будуть логи:
    # - Making request (метод, URL, headers без API ключа)
    # - Request completed (статус, час виконання)
    # - Request failed (якщо помилка)
    
    client.close()
    
    # Повертаємо назад INFO рівень
    logging.getLogger("friday.client").setLevel(logging.INFO)
    print("\n✅ Logging рівень повернуто на INFO\n")


# ============================================================================
# Приклад 9: Метрики та моніторинг
# ============================================================================

def example_metrics():
    """
    Демонструє як можна додати метрики.
    """
    print("=" * 60)
    print("Приклад 9: Метрики та моніторинг")
    print("=" * 60)
    
    # Можна розширити BaseClient для збору метрик
    class MetricsClient(BaseClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.request_count = 0
            self.error_count = 0
            self.total_time = 0.0
        
        def _make_request(self, *args, **kwargs):
            self.request_count += 1
            start_time = time.time()
            
            try:
                result = super()._make_request(*args, **kwargs)
                elapsed = time.time() - start_time
                self.total_time += elapsed
                return result
            except Exception as e:
                self.error_count += 1
                elapsed = time.time() - start_time
                self.total_time += elapsed
                raise
        
        def get_metrics(self):
            avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
            error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
            
            return {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": f"{error_rate:.2%}",
                "total_time": f"{self.total_time:.2f}s",
                "avg_time": f"{avg_time:.2f}s"
            }
    
    print("✅ Створено MetricsClient з підрахунком статистики\n")
    
    client = MetricsClient(api_key="test-key")
    
    # Симуляція запитів
    print("📊 Симуляція 5 запитів...\n")
    
    # В реальності тут були б реальні запити
    # Для прикладу просто встановимо значення
    client.request_count = 5
    client.error_count = 1
    client.total_time = 2.5
    
    # Отримання метрик
    metrics = client.get_metrics()
    
    print("📈 Метрики:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    client.close()
    print()


# ============================================================================
# Приклад 10: Best Practices
# ============================================================================

def example_best_practices():
    """
    Демонструє найкращі практики використання клієнта.
    """
    print("=" * 60)
    print("Приклад 10: Best Practices")
    print("=" * 60)
    
    print("\n✅ Best Practice 1: Використовуйте context manager")
    print("   with BaseClient(api_key='...') as client:")
    print("       # Автоматичне закриття\n")
    
    print("✅ Best Practice 2: Налаштуйте timeout під ваші потреби")
    print("   # Короткі операції")
    print("   client = BaseClient(api_key='...', timeout=10.0)")
    print("   # Довгі операції (streaming)")
    print("   client = BaseClient(api_key='...', timeout=600.0)\n")
    
    print("✅ Best Practice 3: Використовуйте retry для тимчасових помилок")
    print("   client = BaseClient(api_key='...', max_retries=5)")
    print("   # Автоматичний retry при 503, timeout\n")
    
    print("✅ Best Practice 4: Включіть logging для debugging")
    print("   logging.getLogger('friday.client').setLevel(logging.DEBUG)\n")
    
    print("✅ Best Practice 5: Обробляйте специфічні помилки")
    print("   try:")
    print("       response = client._make_request(...)")
    print("   except RateLimitError as e:")
    print("       time.sleep(e.retry_after)")
    print("   except APIError as e:")
    print("       logger.error(f'Request ID: {e.request_id}')\n")
    
    print("✅ Best Practice 6: Не логуйте API ключі")
    print("   # Завжди маскуйте sensitive дані в логах\n")


# ============================================================================
# Головна функція
# ============================================================================

def main():
    """
    Запускає всі приклади.
    """
    print("\n" + "=" * 60)
    print(" FridayAI SDK - HTTP Client Examples")
    print("=" * 60 + "\n")
    
    examples = [
        example_basic_usage,
        example_context_manager,
        example_custom_configuration,
        example_prepare_headers,
        example_error_handling,
        example_retry_logic,
        example_logging,
        example_metrics,
        example_best_practices,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"⚠️  Example failed: {e}\n")
    
    # Async приклад окремо
    print("Запуск async прикладу...")
    try:
        asyncio.run(example_async_client())
    except Exception as e:
        print(f"⚠️  Async example failed: {e}\n")
    
    print("=" * 60)
    print(" Всі приклади виконано!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()