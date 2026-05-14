"""
Приклади використання utils функцій FridayAI SDK
"""

import sys
import os

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("=" * 60)
print(" FridayAI SDK - Utils Examples")
print("=" * 60 + "\n")


# ============================================================================
# Приклад 1: Конвертація форматів
# ============================================================================

print("Приклад 1: Конвертація FridayAI -> OpenAI")
print("-" * 60)
print("""
from friday._utils import convert_friday_to_openai_format

# FridayAI повертає просту структуру
friday_response = {"response": "I can help you with that!"}

# Конвертуємо у OpenAI-compatible формат
openai_format = convert_friday_to_openai_format(
    friday_response,
    model="friday_big"
)

# Тепер це повний ChatCompletion object
print(openai_format)
# {
#     "id": "chatcmpl-abc123",
#     "object": "chat.completion",
#     "created": 1234567890,
#     "model": "friday_big",
#     "choices": [{
#         "index": 0,
#         "message": {
#             "role": "assistant",
#             "content": "I can help you with that!"
#         },
#         "finish_reason": "stop"
#     }],
#     "usage": None
# }
""")
print()


# ============================================================================
# Приклад 2: Підготовка messages
# ============================================================================

print("Приклад 2: Підготовка messages")
print("-" * 60)
print("""
from friday._utils import prepare_messages

# З простого string
messages = prepare_messages("Hello, Friday!")
# [{"role": "user", "content": "Hello, Friday!"}]

# З system prompt
messages = prepare_messages(
    "What's the weather?",
    system_prompt="You are a weather assistant"
)
# [
#     {"role": "system", "content": "You are a weather assistant"},
#     {"role": "user", "content": "What's the weather?"}
# ]

# Вже готові messages
messages = prepare_messages([
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"},
    {"role": "user", "content": "How are you?"}
])
""")
print()


# ============================================================================
# Приклад 3: Кодування зображень
# ============================================================================

print("Приклад 3: Кодування зображень")
print("-" * 60)
print("""
from friday._utils import encode_image_to_base64

# Кодуємо зображення
data_url = encode_image_to_base64("photo.jpg", format="JPEG")
# data:image/jpeg;base64,/9j/4AAQSkZJRg...

# Використовуємо в API request
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image", "image": {"url": data_url}}
        ]
    }
]

response = client.chat.completions.create(
    messages=messages,
    model="friday_big"
)
""")
print()


# ============================================================================
# Приклад 4: Парсинг SSE
# ============================================================================

print("Приклад 4: Streaming з SSE")
print("-" * 60)
print("""
from friday._utils import parse_sse_event, stream_chat_completion

# Парсинг окремого SSE event
line = 'data: {"id": "123", "choices": [{"delta": {"content": "Hi"}}]}'
data = parse_sse_event(line)
print(data["choices"][0]["delta"]["content"])  # "Hi"

# Streaming з response
response = client.post(..., stream=True)

for chunk in stream_chat_completion(response):
    content = chunk["choices"][0]["delta"].get("content", "")
    if content:
        print(content, end="")
""")
print()


# ============================================================================
# Приклад 5: Валідація
# ============================================================================

print("Приклад 5: Валідація даних")
print("-" * 60)
print("""
from friday._utils import validate_model_name, validate_messages

# Валідація моделі
try:
    model = validate_model_name("friday_big")
    print(f"Valid model: {model}")
except ValueError as e:
    print(f"Invalid model: {e}")

# Валідація messages
try:
    validate_messages([
        {"role": "user", "content": "Hello"}
    ])
    print("Messages are valid!")
except ValueError as e:
    print(f"Invalid messages: {e}")
""")
print()


# ============================================================================
# Приклад 6: Генерація IDs
# ============================================================================

print("Приклад 6: Генерація IDs")
print("-" * 60)
print("""
from friday._utils import generate_chat_id, generate_request_id

# Chat completion ID
chat_id = generate_chat_id()
# "chatcmpl-a1b2c3d4e5f6"

# З кастомним prefix
custom_id = generate_chat_id(prefix="custom")
# "custom-a1b2c3d4e5f6"

# Request ID (UUID)
req_id = generate_request_id()
# "550e8400-e29b-41d4-a716-446655440000"
""")
print()


# ============================================================================
# Приклад 7: Допоміжні функції
# ============================================================================

print("Приклад 7: Допоміжні функції")
print("-" * 60)
print("""
from friday._utils import (
    truncate_text,
    merge_dicts,
    compute_file_hash,
    is_base64_url
)

# Обрізання тексту
text = truncate_text("Very long text here...", max_length=15)
# "Very long t..."

# Об'єднання словників
config = merge_dicts(
    {"timeout": 30, "retries": 2},
    {"timeout": 60},  # Перезаписує timeout
    {"debug": True}   # Додає новий ключ
)
# {"timeout": 60, "retries": 2, "debug": True}

# Hash файлу
file_hash = compute_file_hash("document.pdf")
# "a1b2c3d4e5f6789..."

# Перевірка URL
is_data_url = is_base64_url("data:image/png;base64,...")
# True

is_http_url = is_base64_url("https://example.com/img.jpg")
# False
""")
print()


print("=" * 60)
print(" Best Practices")
print("=" * 60 + "\n")

print("""
1. Використовуйте prepare_messages() для нормалізації input
   - Приймає string, dict, або list
   - Додає system prompt якщо потрібно

2. Використовуйте convert_friday_to_openai_format() для сумісності
   - Легка міграція з OpenAI
   - Уніфікований формат

3. Валідуйте дані перед відправкою
   - validate_model_name() для моделей
   - validate_messages() для messages

4. Для streaming використовуйте stream_chat_completion()
   - Автоматичний парсинг SSE
   - Обробка [DONE]

5. Кодуйте файли та зображення у base64 для API
   - encode_image_to_base64() для зображень
   - encode_file_to_base64() для файлів
""")

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)
