"""
Приклади використання Pydantic моделей FridayAI SDK

Демонструє як працювати з моделями для type-safe коду.

ПРИМІТКА: Для запуску потрібно встановити pydantic: pip install pydantic>=2.0
Ці приклади показують концепції використання моделей.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock models для демонстрації без pydantic
print("NOTE: Running in demo mode without pydantic")
print("    Install pydantic for full functionality: pip install pydantic>=2.0\n")


print("=" * 60)
print(" FridayAI SDK - Pydantic Models Concepts")
print("=" * 60 + "\n")


# ============================================================================
# Демонстрація концепцій
# ============================================================================

print("Приклад 1: Message Model")
print("-" * 60)
print("""
# Створення простого message
msg = Message(role="user", content="Hello, Friday!")

# Мультимодальний контент
msg = Message(
    role="user",
    content=[
        {"type": "text", "text": "What's in this image?"},
        {"type": "image", "image": {"url": "https://..."}}
    ]
)

# Автоматична валідація
try:
    msg = Message(role="invalid", content="Test")
except ValidationError:
    print("Invalid role!")
""")
print()

print("Приклад 2: ChatCompletion")
print("-" * 60)
print("""
# Парсинг API response
api_response = {
    "id": "chatcmpl-123",
    "model": "friday_big",
    "choices": [{
        "message": {"role": "assistant", "content": "Hello!"}
    }]
}

completion = ChatCompletion(**api_response)
print(completion.choices[0].message.content)  # Type-safe!

# Серіалізація
data = completion.model_dump()
json_str = completion.model_dump_json()
""")
print()

print("Приклад 3: FridayAI -> OpenAI Conversion")
print("-" * 60)
print("""
# FridayAI повертає просту структуру
friday_response = {"response": "Hello there!"}

# Helper конвертує у OpenAI-compatible формат
completion = create_chat_completion_from_friday_response(
    friday_response,
    model="friday_big"
)

# Тепер це ChatCompletion з правильною структурою
assert completion.object == "chat.completion"
assert completion.choices[0].message.role == "assistant"
""")
print()

print("Приклад 4: Streaming Chunks")
print("-" * 60)
print("""
# Парсинг SSE chunks
for chunk_data in stream:
    chunk = ChatCompletionChunk(**chunk_data)
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
    if chunk.choices[0].finish_reason == "stop":
        break
""")
print()

print("Приклад 5: Vector Search Results")
print("-" * 60)
print("""
search_result = SearchResult(**api_response)

# Property для зручного доступу
print(f"Found {search_result.count} results")

for point in search_result.points:
    print(f"{point.id}: {point.score:.2f}")
    print(f"  {point.payload['text']}")
""")
print()

print("Приклад 6: Usage Status")
print("-" * 60)
print("""
status = UsageStatus(**api_response)

# Type-safe доступ з автодоповненням
print(f"Chat: {status.usage.chat}/{status.limits.chat}")
print(f"Remaining: {status.remaining.chat}")

# IDE знає всі поля!
""")
print()

print("Приклад 7: Validation")
print("-" * 60)
print("""
# Автоматична валідація при створенні
msg = Message(
    role="user",  # Має бути 'user', 'assistant', або 'system'
    content="Hello"  # Не може бути порожнім
)

# Pydantic автоматично перевіряє:
# - Типи полів (str, int, List, etc.)
# - Required vs Optional
# - Custom validators
# - Формат даних
""")
print()

print("Приклад 8: Type Hints для IDE")
print("-" * 60)
print("""
def process_completion(completion: ChatCompletion) -> str:
    # IDE автоматично підказує:
    # - completion.id (str)
    # - completion.model (str)
    # - completion.choices (List[Choice])
    # - completion.choices[0].message.content (str)
    
    return completion.choices[0].message.content

# Автодоповнення працює!
""")
print()



print("=" * 60)
print(" Всі приклади виконано!")
print("=" * 60)
