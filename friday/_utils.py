"""
Utility функції для FridayAI SDK.

Цей модуль містить допоміжні функції для:
- Конвертація форматів (FridayAI ↔ OpenAI)
- Кодування файлів та зображень у base64
- Парсинг SSE (Server-Sent Events)
- Генерація унікальних IDs
- Валідація даних
"""

import base64
import hashlib
import json
import mimetypes
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Iterator
from pathlib import Path


# ============================================================================
# Format Conversion
# ============================================================================


def convert_friday_to_openai_format(
    response: Dict[str, Any],
    model: str = "friday_big",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Конвертує відповідь FridayAI API у OpenAI-compatible формат.
    
    FridayAI повертає просту структуру: {"response": "text"}
    Ця функція перетворює її у повний OpenAI ChatCompletion формат.
    
    Args:
        response: Dict відповідь від FridayAI API
        model: Назва моделі
        request_id: Опціональний ID запиту (генерується якщо None)
    
    Returns:
        OpenAI-compatible dict з повною структурою ChatCompletion
    
    Example:
        >>> friday_response = {"response": "Hello there!"}
        >>> openai_format = convert_friday_to_openai_format(
        ...     friday_response,
        ...     model="friday_big"
        ... )
        >>> print(openai_format["choices"][0]["message"]["content"])
        "Hello there!"
    """
    # Витягуємо текст відповіді
    response_text = response.get("text")
    if response_text is None:
        response_value = response.get("response", "")
        response_text = response_value if isinstance(response_value, str) else str(response_value)
    
    # Генеруємо ID якщо не передано
    if request_id is None:
        request_id = generate_chat_id()
    
    # Створюємо OpenAI-compatible структуру
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": None  # FridayAI не повертає usage info
    }


def prepare_messages(
    messages: Union[str, List[Dict], Dict],
    *,
    system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Підготовка messages для API запиту.
    
    Приймає різні формати input та нормалізує їх:
    - str: конвертує у [{"role": "user", "content": "..."}]
    - List[Dict]: валідує та повертає як є
    - Dict: загортає у список
    
    Args:
        messages: Messages у будь-якому форматі
        system_prompt: Опціональний system prompt (додається на початок)
    
    Returns:
        Список messages у правильному форматі
    
    Raises:
        ValueError: Якщо messages невалідного формату
    
    Example:
        >>> # З string
        >>> msgs = prepare_messages("Hello, Friday!")
        >>> # [{"role": "user", "content": "Hello, Friday!"}]
        
        >>> # З system prompt
        >>> msgs = prepare_messages(
        ...     "What's the weather?",
        ...     system_prompt="You are a weather assistant"
        ... )
        >>> # [
        >>> #   {"role": "system", "content": "You are..."},
        >>> #   {"role": "user", "content": "What's the weather?"}
        >>> # ]
    """
    # Конвертуємо у список
    if isinstance(messages, str):
        # Простий string → user message
        result = [{"role": "user", "content": messages}]
    elif isinstance(messages, dict):
        # Один dict → загортаємо у список
        result = [messages]
    elif isinstance(messages, list):
        # Вже список
        result = messages
    else:
        raise ValueError(
            f"messages must be str, dict, or list, got {type(messages).__name__}"
        )
    
    # Додаємо system prompt якщо є
    if system_prompt:
        result = [
            {"role": "system", "content": system_prompt},
            *result
        ]
    
    return result


# ============================================================================
# Encoding
# ============================================================================


def encode_image_to_base64(
    image_path: str,
    *,
    format: str = "PNG"
) -> str:
    """
    Кодує зображення у base64 data URL.
    
    Args:
        image_path: Шлях до файлу зображення
        format: Формат зображення (PNG, JPEG, GIF, etc.)
    
    Returns:
        Base64 data URL (data:image/png;base64,...)
    
    Raises:
        FileNotFoundError: Якщо файл не знайдено
        IOError: Якщо помилка читання файлу
    
    Example:
        >>> data_url = encode_image_to_base64("photo.jpg", format="JPEG")
        >>> # data:image/jpeg;base64,/9j/4AAQSkZJRg...
        
        >>> # Використання в API request
        >>> messages = [{
        ...     "role": "user",
        ...     "content": [
        ...         {"type": "text", "text": "What's in this image?"},
        ...         {"type": "image", "image": {"url": data_url}}
        ...     ]
        ... }]
    """
    # Перевіряємо що файл існує
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Читаємо файл
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # Кодуємо у base64
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    
    # Визначаємо MIME type
    format_lower = format.lower()
    mime_type = f"image/{format_lower}"
    
    # Створюємо data URL
    data_url = f"data:{mime_type};base64,{base64_data}"
    
    return data_url


def encode_file_to_base64(
    file_path: str,
    *,
    mime_type: Optional[str] = None,
    filename: Optional[str] = None
) -> str:
    """
    Кодує файл у base64 data URL.
    
    Автоматично визначає MIME type з розширення файлу якщо не вказано.
    
    Args:
        file_path: Шлях до файлу
        mime_type: Опціональний MIME type (auto-detect якщо None)
        filename: Опціональне ім'я файлу (використовується з file_path якщо None)
    
    Returns:
        Base64 data URL (data:application/pdf;base64,...)
    
    Raises:
        FileNotFoundError: Якщо файл не знайдено
    
    Example:
        >>> # PDF файл
        >>> data_url = encode_file_to_base64("document.pdf")
        >>> # data:application/pdf;base64,JVBERi0xLj...
        
        >>> # З вказаним MIME type
        >>> data_url = encode_file_to_base64(
        ...     "data.csv",
        ...     mime_type="text/csv"
        ... )
    """
    # Перевіряємо що файл існує
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Читаємо файл
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    # Кодуємо у base64
    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    
    # Визначаємо MIME type
    if mime_type is None:
        # Auto-detect з розширення
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Fallback до application/octet-stream
            mime_type = "application/octet-stream"
    
    # Створюємо data URL
    data_url = f"data:{mime_type};base64,{base64_data}"
    
    return data_url


def is_base64_url(url: str) -> bool:
    """
    Перевіряє чи є URL base64 data URL.
    
    Args:
        url: URL для перевірки
    
    Returns:
        True якщо це base64 data URL, False якщо звичайний URL
    
    Example:
        >>> is_base64_url("data:image/png;base64,iVBOR...")
        True
        
        >>> is_base64_url("https://example.com/image.jpg")
        False
    """
    return url.startswith("data:")


# ============================================================================
# Streaming
# ============================================================================


def parse_sse_event(line: str) -> Optional[Dict[str, Any]]:
    """
    Парсить SSE (Server-Sent Events) event line.
    
    SSE формат:
    - data: {"id": "...", "choices": [...]}
    - data: [DONE]
    
    Args:
        line: Рядок SSE event
    
    Returns:
        Parsed dict або None якщо [DONE] або invalid JSON
    
    Example:
        >>> line = 'data: {"id": "123", "object": "chat.completion.chunk"}'
        >>> data = parse_sse_event(line)
        >>> print(data["id"])
        "123"
        
        >>> line = 'data: [DONE]'
        >>> data = parse_sse_event(line)
        >>> # None (кінець stream)
    """
    # Видаляємо "data: " prefix
    if not line.startswith("data: "):
        return None
    
    data_str = line[6:].strip()  # Видалити "data: "
    
    # Перевіряємо чи це [DONE]
    if data_str == "[DONE]":
        return None
    
    # Парсимо JSON
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        # Невалідний JSON - пропускаємо
        return None


def stream_chat_completion(
    response
) -> Iterator[Dict[str, Any]]:
    """
    Генератор для streaming chat completions.
    
    Парсить SSE stream та yield parsed chunks.
    
    Args:
        response: Streaming HTTP response (httpx.Response з stream=True)
    
    Yields:
        Parsed chunk dicts
    
    Example:
        >>> response = client.post(..., stream=True)
        >>> for chunk in stream_chat_completion(response):
        ...     content = chunk["choices"][0]["delta"].get("content", "")
        ...     if content:
        ...         print(content, end="")
    """
    for line in response.iter_lines():
        if line.startswith("data:") and line[5:].strip() == "[DONE]":
            break
        # Парсимо SSE event
        data = parse_sse_event(line)
        
        # [DONE] або invalid → закінчуємо
        if data is None:
            continue
        
        # Yield parsed chunk
        yield data


# ============================================================================
# ID Generation
# ============================================================================


def generate_chat_id(prefix: str = "chatcmpl") -> str:
    """
    Генерує унікальний ID для chat completion.
    
    Використовує random bytes для генерації унікального ID.
    
    Args:
        prefix: Prefix для ID (за замовчуванням "chatcmpl")
    
    Returns:
        Унікальний ID (наприклад "chatcmpl-7f8a9b0c1d2e")
    
    Example:
        >>> chat_id = generate_chat_id()
        >>> # "chatcmpl-a1b2c3d4e5f6"
        
        >>> custom_id = generate_chat_id(prefix="custom")
        >>> # "custom-a1b2c3d4e5f6"
    """
    # Генеруємо random bytes
    random_bytes = os.urandom(8)
    
    # Кодуємо у hex
    random_hex = random_bytes.hex()[:12]  # Беремо перші 12 символів
    
    # Додаємо prefix
    return f"{prefix}-{random_hex}"


def generate_request_id() -> str:
    """
    Генерує унікальний request ID.
    
    Використовує UUID4 для гарантованої унікальності.
    
    Returns:
        UUID string
    
    Example:
        >>> req_id = generate_request_id()
        >>> # "550e8400-e29b-41d4-a716-446655440000"
    """
    return str(uuid.uuid4())


# ============================================================================
# Validation
# ============================================================================


VALID_MODELS = ["friday_medium", "friday_big"]
VALID_ROLES = ["user", "assistant", "system"]


def validate_model_name(model: str) -> str:
    """
    Валідує назву моделі.
    
    Args:
        model: Назва моделі
    
    Returns:
        Валідна назва моделі (незмінна)
    
    Raises:
        ValueError: Якщо модель невалідна
    
    Example:
        >>> validate_model_name("friday_big")
        "friday_big"
        
        >>> validate_model_name("gpt-4")
        # ValueError: Invalid model name
    """
    if model not in VALID_MODELS:
        raise ValueError(
            f"Invalid model name: {model}. "
            f"Must be one of {VALID_MODELS}"
        )
    return model


def validate_messages(messages: List[Dict]) -> None:
    """
    Валідує список messages.
    
    Перевіряє:
    - Чи messages не порожній
    - Чи кожен message має role та content
    - Чи role один з допустимих
    
    Args:
        messages: Список messages для валідації
    
    Raises:
        ValueError: Якщо messages невалідні
    
    Example:
        >>> validate_messages([
        ...     {"role": "user", "content": "Hello"}
        ... ])
        # OK - не raise помилки
        
        >>> validate_messages([])
        # ValueError: messages cannot be empty
        
        >>> validate_messages([{"role": "invalid", "content": "Hi"}])
        # ValueError: Invalid role
    """
    # Перевірка що не порожній
    if not messages:
        raise ValueError("messages cannot be empty")
    
    # Перевірка кожного message
    for i, msg in enumerate(messages):
        # Має бути dict
        if not isinstance(msg, dict):
            raise ValueError(
                f"Message at index {i} must be a dict, "
                f"got {type(msg).__name__}"
            )
        
        # Має бути role
        if "role" not in msg:
            raise ValueError(f"Message at index {i} missing 'role' field")
        
        # Має бути content
        if "content" not in msg:
            raise ValueError(f"Message at index {i} missing 'content' field")
        
        # role має бути валідним
        role = msg["role"]
        if role not in VALID_ROLES:
            raise ValueError(
                f"Message at index {i} has invalid role: {role}. "
                f"Must be one of {VALID_ROLES}"
            )


# ============================================================================
# Miscellaneous
# ============================================================================


def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Обчислює hash файлу.
    
    Args:
        file_path: Шлях до файлу
        algorithm: Алгоритм хешування (sha256, md5, etc.)
    
    Returns:
        Hex string hash
    
    Example:
        >>> file_hash = compute_file_hash("document.pdf")
        >>> # "a1b2c3d4e5f6789..."
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        # Читаємо блоками для великих файлів
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    Обрізає текст до максимальної довжини.
    
    Args:
        text: Текст для обрізання
        max_length: Максимальна довжина
        suffix: Суфікс для обрізаного тексту
    
    Returns:
        Обрізаний текст
    
    Example:
        >>> truncate_text("Very long text here...", max_length=10)
        "Very lo..."
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Об'єднує декілька словників.
    
    Пізніші словники перезаписують ранніші.
    
    Args:
        *dicts: Словники для об'єднання
    
    Returns:
        Об'єднаний словник
    
    Example:
        >>> result = merge_dicts(
        ...     {"a": 1, "b": 2},
        ...     {"b": 3, "c": 4}
        ... )
        >>> # {"a": 1, "b": 3, "c": 4}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    # Format conversion
    "convert_friday_to_openai_format",
    "prepare_messages",
    
    # Encoding
    "encode_image_to_base64",
    "encode_file_to_base64",
    "is_base64_url",
    
    # Streaming
    "parse_sse_event",
    "stream_chat_completion",
    
    # ID generation
    "generate_chat_id",
    "generate_request_id",
    
    # Validation
    "validate_model_name",
    "validate_messages",
    
    # Miscellaneous
    "compute_file_hash",
    "truncate_text",
    "merge_dicts",
    
    # Constants
    "VALID_MODELS",
    "VALID_ROLES",
]
