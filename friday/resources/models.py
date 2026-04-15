"""
Pydantic моделі для FridayAI SDK.

Цей модуль визначає всі data models для валідації та type hints:
- Chat completions (input/output)
- Images
- Audio
- Embeddings
- Vector collections
- Usage tracking

Всі моделі максимально сумісні з OpenAI API для легкої міграції.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import time

# ============================================================================
# Chat Models
# ============================================================================


class Message(BaseModel):
    """
    Повідомлення для chat API (input).
    
    Підтримує два формати content:
    - Простий: str - текстове повідомлення
    - Розширений: List[Dict] - мультимодальний контент (текст, зображення, файли)
    
    Attributes:
        role: Роль відправника ('user', 'assistant', 'system')
        content: Контент повідомлення
        name: Опціональне ім'я відправника
    
    Example:
        >>> # Простий текст
        >>> msg = Message(role="user", content="Hello")
        >>> 
        >>> # З зображенням
        >>> msg = Message(
        ...     role="user",
        ...     content=[
        ...         {"type": "text", "text": "What's in this image?"},
        ...         {"type": "image", "image": {"url": "https://..."}}
        ...     ]
        ... )
    """
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Валідація що role один з допустимих значень."""
        allowed_roles = ["user", "assistant", "system"]
        if v not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, got '{v}'")
        return v
    
    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: Union[str, List]) -> Union[str, List]:
        """Валідація що content не порожній."""
        if isinstance(v, str) and not v.strip():
            raise ValueError("content string cannot be empty")
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("content list cannot be empty")
        return v


class ChatCompletionMessage(BaseModel):
    """
    Повідомлення у відповіді від chat API.
    
    Attributes:
        role: Завжди 'assistant' для відповідей
        content: Текст відповіді
    
    Example:
        >>> msg = ChatCompletionMessage(
        ...     role="assistant",
        ...     content="I'm doing well, thank you!"
        ... )
    """
    role: Literal["assistant"]
    content: str
    
    model_config = ConfigDict(extra="allow")


class Choice(BaseModel):
    """
    Один з варіантів відповіді від chat API.
    
    Attributes:
        index: Індекс choice (зазвичай 0)
        message: Повідомлення від асистента
        finish_reason: Причина завершення ('stop', 'length', etc.)
    
    Example:
        >>> choice = Choice(
        ...     index=0,
        ...     message=ChatCompletionMessage(role="assistant", content="Hello!"),
        ...     finish_reason="stop"
        ... )
    """
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[Literal["stop", "length", "content_filter"]] = None
    
    model_config = ConfigDict(extra="allow")


class ChatCompletion(BaseModel):
    """
    Повна відповідь від chat completions API.
    
    OpenAI-сумісна структура для легкої міграції.
    
    Attributes:
        id: Унікальний ID completion
        object: Тип об'єкта (завжди 'chat.completion')
        created: Unix timestamp створення
        model: Назва моделі
        choices: Список варіантів відповідей
        usage: Опціональна інформація про використання токенів
    
    Example:
        >>> completion = ChatCompletion(
        ...     id="chatcmpl-123",
        ...     created=1234567890,
        ...     model="friday_big",
        ...     choices=[Choice(...)]
        ... )
        >>> print(completion.choices[0].message.content)
    """
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Dict[str, int]] = None
    
    model_config = ConfigDict(extra="allow")
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує у dict для серіалізації."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Конвертує у JSON string."""
        return self.model_dump_json()


# Streaming models

class Delta(BaseModel):
    """
    Delta для streaming chunks.
    
    Містить часткові дані що додаються до response.
    
    Attributes:
        role: Роль (тільки в першому chunk)
        content: Частина контенту
    """
    role: Optional[str] = None
    content: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class ChunkChoice(BaseModel):
    """
    Choice для streaming chunk.
    
    Attributes:
        index: Індекс choice
        delta: Часткові дані
        finish_reason: Причина завершення (тільки в останньому chunk)
    """
    index: int
    delta: Delta
    finish_reason: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class ChatCompletionChunk(BaseModel):
    """
    Streaming chunk від chat completions API.
    
    Використовується при stream=True.
    
    Attributes:
        id: ID stream session
        object: Тип об'єкта (завжди 'chat.completion.chunk')
        created: Unix timestamp
        model: Назва моделі
        choices: Список delta choices
    
    Example:
        >>> chunk = ChatCompletionChunk(
        ...     id="chatcmpl-stream-123",
        ...     created=1234567890,
        ...     model="friday_big",
        ...     choices=[ChunkChoice(index=0, delta=Delta(content="Hello"))]
        ... )
        >>> print(chunk.choices[0].delta.content)  # "Hello"
    """
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChunkChoice]
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Image Models
# ============================================================================


class ImageResponse(BaseModel):
    """
    Відповідь від image generation API (FridayAI формат).
    
    Attributes:
        image_url: URL згенерованого зображення
    
    Example:
        >>> response = ImageResponse(
        ...     image_url="https://cdn.fridayai.com/images/123.png"
        ... )
    """
    image_url: str
    
    model_config = ConfigDict(extra="allow")


class Image(BaseModel):
    """
    OpenAI-compatible image object.
    
    Attributes:
        url: URL зображення
    """
    url: str
    
    model_config = ConfigDict(extra="allow")


class ImagesResponse(BaseModel):
    """
    OpenAI-compatible images response.
    
    Attributes:
        created: Unix timestamp
        data: Список Image об'єктів
    
    Example:
        >>> response = ImagesResponse(
        ...     created=1234567890,
        ...     data=[Image(url="https://...")]
        ... )
    """
    created: int
    data: List[Image]
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Audio Models
# ============================================================================


class AudioResponse(BaseModel):
    """
    Відповідь від audio generation (TTS) API.
    
    Attributes:
        audio_url: URL згенерованого аудіо файлу
    
    Example:
        >>> response = AudioResponse(
        ...     audio_url="https://cdn.fridayai.com/audio/123.mp3"
        ... )
    """
    audio_url: str
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Embedding Models
# ============================================================================


class Embedding(BaseModel):
    """
    Single embedding object.
    
    Attributes:
        object: Тип об'єкта (завжди 'embedding')
        embedding: Vector embedding
        index: Індекс в batch
    """
    object: Literal["embedding"] = "embedding"
    embedding: List[float]
    index: int
    
    model_config = ConfigDict(extra="allow")


class EmbeddingResponse(BaseModel):
    """
    Відповідь від embeddings API.
    
    OpenAI-compatible format.
    
    Attributes:
        object: Тип об'єкта (завжди 'list')
        data: Список Embedding об'єктів
        model: Назва моделі
        usage: Інформація про використання
    
    Example:
        >>> response = EmbeddingResponse(
        ...     data=[Embedding(embedding=[0.1, 0.2, ...], index=0)],
        ...     model="embedding-model"
        ... )
    """
    object: Literal["list"] = "list"
    data: List[Embedding]
    model: str
    usage: Optional[Dict[str, int]] = None
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Collection Models (Qdrant Vector Database)
# ============================================================================


class CollectionInfo(BaseModel):
    """
    Інформація про vector collection.
    
    Attributes:
        result: Dict з деталями колекції
        status: Статус операції
        time: Час виконання операції
    
    Example:
        >>> info = CollectionInfo(
        ...     result={"vectors_count": 1000},
        ...     status="ok",
        ...     time=0.123
        ... )
    """
    result: Dict[str, Any]
    status: str
    time: float
    
    model_config = ConfigDict(extra="allow")


class Point(BaseModel):
    """
    Vector point для Qdrant.
    
    Attributes:
        id: Унікальний ID point (string або int)
        vector: Vector embedding
        payload: Опціональні метадані
    
    Example:
        >>> point = Point(
        ...     id="point-1",
        ...     vector=[0.1, 0.2, 0.3, ...],
        ...     payload={"text": "Some text", "category": "tech"}
        ... )
    """
    id: Union[str, int]
    vector: List[float]
    payload: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(extra="allow")


class ScoredPoint(BaseModel):
    """
    Point з similarity score від search операції.
    
    Attributes:
        id: ID point
        score: Similarity score (0.0 - 1.0)
        payload: Метадані
        vector: Опціонально сам вектор
    
    Example:
        >>> point = ScoredPoint(
        ...     id="point-1",
        ...     score=0.95,
        ...     payload={"text": "Relevant text"}
        ... )
    """
    id: Union[str, int]
    score: float
    payload: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None
    
    model_config = ConfigDict(extra="allow")


class SearchResult(BaseModel):
    """
    Результат пошуку у vector collection.
    
    Attributes:
        result: Dict з результатами пошуку
        status: Статус операції
        time: Час виконання
    
    Example:
        >>> result = SearchResult(
        ...     result={"points": [...]},
        ...     status="ok",
        ...     time=0.05
        ... )
        >>> for point in result.points:
        ...     print(f"Score: {point.score}")
    """
    result: Dict[str, Any]
    status: str
    time: float
    
    model_config = ConfigDict(extra="allow")
    
    @property
    def points(self) -> List[ScoredPoint]:
        """
        Витягує та парсить points з result.
        
        Returns:
            Список ScoredPoint об'єктів
        """
        points_data = self.result.get("points", [])
        return [ScoredPoint(**p) for p in points_data]
    
    @property
    def count(self) -> int:
        """Кількість знайдених points."""
        return len(self.points)


class UpsertResult(BaseModel):
    """
    Результат upsert операції у collection.
    
    Attributes:
        result: Dict з деталями операції
        status: Статус операції
        time: Час виконання
    
    Example:
        >>> result = UpsertResult(
        ...     result={"operation_id": 123},
        ...     status="ok",
        ...     time=0.1
        ... )
    """
    result: Dict[str, Any]
    status: str
    time: float
    
    model_config = ConfigDict(extra="allow")
    
    @property
    def operation_id(self) -> Optional[int]:
        """ID операції якщо доступний."""
        return self.result.get("operation_id")


# ============================================================================
# Usage Models
# ============================================================================


class Limits(BaseModel):
    """
    Ліміти використання API.
    
    Attributes:
        chat: Ліміт chat запитів
        image: Ліміт image generation
        voice: Ліміт voice generation
    """
    chat: int
    image: int
    voice: int
    
    model_config = ConfigDict(extra="allow")


class Usage(BaseModel):
    """
    Поточне використання API.
    
    Attributes:
        chat: Використано chat запитів
        image: Використано image generations
        voice: Використано voice generations
    """
    chat: int
    image: int
    voice: int
    
    model_config = ConfigDict(extra="allow")


class Remaining(BaseModel):
    """
    Залишок квоти.
    
    Attributes:
        chat: Залишок chat запитів
        image: Залишок image generations
        voice: Залишок voice generations
    """
    chat: int
    image: int
    voice: int
    
    model_config = ConfigDict(extra="allow")


class UsageStatus(BaseModel):
    """
    Статус використання та ліміти користувача.
    
    Attributes:
        token_hash: Hash токену користувача
        limits: Максимальні ліміти
        usage: Поточне використання
        remaining: Залишок
    
    Example:
        >>> status = UsageStatus(
        ...     token_hash="abc123...",
        ...     limits=Limits(chat=100, image=50, voice=30),
        ...     usage=Usage(chat=25, image=10, voice=5),
        ...     remaining=Remaining(chat=75, image=40, voice=25)
        ... )
        >>> print(f"Chat usage: {status.usage.chat}/{status.limits.chat}")
    """
    token_hash: str
    limits: Limits
    usage: Usage
    remaining: Remaining
    
    model_config = ConfigDict(extra="allow")


class ChatLog(BaseModel):
    """
    Лог chat conversation.
    
    Attributes:
        id: ID логу (MongoDB _id)
        conversation: Список повідомлень
        response: Відповідь асистента
        model: Назва моделі
        date: Дата у форматі YYYY-MM-DD
        user: Опціональне ім'я користувача
    
    Example:
        >>> log = ChatLog(
        ...     id="507f1f77bcf86cd799439011",
        ...     conversation=[{"role": "user", "content": "Hi"}],
        ...     response="Hello!",
        ...     model="friday_big",
        ...     date="2024-01-01"
        ... )
    """
    id: str = Field(alias="_id")
    conversation: List[Dict[str, Any]]
    response: str
    model: str
    date: str
    user: Optional[str] = None
    
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True  # Дозволити _id та id
    )


class ChatLogsResponse(BaseModel):
    """
    Відповідь зі списком логів.
    
    Attributes:
        items: Список ChatLog об'єктів
    """
    items: List[ChatLog]
    
    model_config = ConfigDict(extra="allow")


class UserInfo(BaseModel):
    """
    Персональна інформація користувача.
    
    Attributes:
        info: Текстова інформація про користувача
    
    Example:
        >>> user_info = UserInfo(
        ...     info="Name: John, Preferences: tech news"
        ... )
    """
    info: str
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Common Models
# ============================================================================


class ErrorResponse(BaseModel):
    """
    Відповідь з помилкою від API.
    
    Attributes:
        error: Повідомлення про помилку
    
    Example:
        >>> error = ErrorResponse(
        ...     error="Invalid API key provided"
        ... )
    """
    error: str
    
    model_config = ConfigDict(extra="allow")


class HealthResponse(BaseModel):
    """
    Відповідь від /health endpoint.
    
    Attributes:
        status: Статус сервісу (зазвичай 'ok')
    
    Example:
        >>> health = HealthResponse(status="ok")
    """
    status: str
    
    model_config = ConfigDict(extra="allow")


class OkResponse(BaseModel):
    """
    Generic success response.
    
    Attributes:
        ok: True якщо операція успішна
    """
    ok: bool
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Helper функції для створення моделей
# ============================================================================


def create_chat_completion_from_friday_response(
    response: Dict[str, Any],
    model: str = "friday_big"
) -> ChatCompletion:
    """
    Конвертує відповідь FridayAI API у ChatCompletion.
    
    FridayAI повертає просту структуру {"response": "text"},
    цей helper конвертує її у OpenAI-compatible ChatCompletion.
    
    Args:
        response: Dict відповідь від FridayAI API
        model: Назва моделі
    
    Returns:
        ChatCompletion об'єкт
    
    Example:
        >>> friday_response = {"response": "Hello!"}
        >>> completion = create_chat_completion_from_friday_response(
        ...     friday_response,
        ...     model="friday_big"
        ... )
        >>> print(completion.choices[0].message.content)  # "Hello!"
    """
    import hashlib
    import time
    
    # Генеруємо ID на основі response
    response_text = response.get("response", "")
    response_id = hashlib.md5(
        f"{response_text}{time.time()}".encode()
    ).hexdigest()[:16]
    
    return ChatCompletion(
        id=f"chatcmpl-{response_id}",
        object="chat.completion",
        created=int(time.time()),
        model=model,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    content=response_text
                ),
                finish_reason="stop"
            )
        ]
    )


def create_chat_completion_chunk(
    content: str,
    model: str = "friday_big",
    chunk_id: Optional[str] = None,
    finish: bool = False
) -> ChatCompletionChunk:
    """
    Створює ChatCompletionChunk для streaming.
    
    Args:
        content: Частина контенту
        model: Назва моделі
        chunk_id: ID chunk (генерується якщо None)
        finish: Чи це останній chunk
    
    Returns:
        ChatCompletionChunk об'єкт
    
    Example:
        >>> chunk = create_chat_completion_chunk("Hello", model="friday_big")
        >>> print(chunk.choices[0].delta.content)  # "Hello"
    """
    if chunk_id is None:
        import hashlib
        chunk_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:16]
    
    return ChatCompletionChunk(
        id=f"chatcmpl-{chunk_id}",
        object="chat.completion.chunk",
        created=int(time.time()),
        model=model,
        choices=[
            ChunkChoice(
                index=0,
                delta=Delta(content=content if not finish else None),
                finish_reason="stop" if finish else None
            )
        ]
    )


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    # Chat models
    "Message",
    "ChatCompletionMessage",
    "Choice",
    "ChatCompletion",
    "Delta",
    "ChunkChoice",
    "ChatCompletionChunk",
    
    # Image models
    "ImageResponse",
    "Image",
    "ImagesResponse",
    
    # Audio models
    "AudioResponse",
    
    # Embedding models
    "Embedding",
    "EmbeddingResponse",
    
    # Collection models
    "CollectionInfo",
    "Point",
    "ScoredPoint",
    "SearchResult",
    "UpsertResult",
    
    # Usage models
    "Limits",
    "Usage",
    "Remaining",
    "UsageStatus",
    "ChatLog",
    "ChatLogsResponse",
    "UserInfo",
    
    # Common models
    "ErrorResponse",
    "HealthResponse",
    "OkResponse",
    
    # Helper functions
    "create_chat_completion_from_friday_response",
    "create_chat_completion_chunk",
]