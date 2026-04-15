"""
Unit тести для модуля _models.py

Тестує всі Pydantic моделі та helper функції.
"""

import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _models import (
    # Chat models
    Message,
    ChatCompletionMessage,
    Choice,
    ChatCompletion,
    Delta,
    ChunkChoice,
    ChatCompletionChunk,
    # Image models
    ImageResponse,
    Image,
    ImagesResponse,
    # Audio models
    AudioResponse,
    # Embedding models
    Embedding,
    EmbeddingResponse,
    # Collection models
    CollectionInfo,
    Point,
    ScoredPoint,
    SearchResult,
    UpsertResult,
    # Usage models
    Limits,
    Usage,
    Remaining,
    UsageStatus,
    ChatLog,
    UserInfo,
    # Common models
    ErrorResponse,
    HealthResponse,
    OkResponse,
    # Helper functions
    create_chat_completion_from_friday_response,
    create_chat_completion_chunk,
)


# ============================================================================
# Chat Models Tests
# ============================================================================


class TestMessage:
    """Тести для Message model"""
    
    def test_message_creation_with_string_content(self):
        """Тест створення Message з текстовим контентом"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
    
    def test_message_creation_with_list_content(self):
        """Тест створення Message з list контентом"""
        content = [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image", "image": {"url": "https://example.com/img.jpg"}}
        ]
        msg = Message(role="user", content=content)
        assert msg.role == "user"
        assert isinstance(msg.content, list)
        assert len(msg.content) == 2
    
    def test_message_with_name(self):
        """Тест Message з полем name"""
        msg = Message(role="user", content="Hi", name="John")
        assert msg.name == "John"
    
    def test_message_invalid_role(self):
        """Тест що невалідна роль викликає помилку"""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="invalid_role", content="Test")
        assert "role must be one of" in str(exc_info.value)
    
    def test_message_empty_string_content(self):
        """Тест що порожній string не дозволений"""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content="   ")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_message_empty_list_content(self):
        """Тест що порожній list не дозволений"""
        with pytest.raises(ValidationError) as exc_info:
            Message(role="user", content=[])
        assert "cannot be empty" in str(exc_info.value)


class TestChatCompletion:
    """Тести для ChatCompletion model"""
    
    def test_chat_completion_creation(self):
        """Тест створення ChatCompletion"""
        completion = ChatCompletion(
            id="chatcmpl-123",
            created=1234567890,
            model="friday_big",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="Hello!"
                    ),
                    finish_reason="stop"
                )
            ]
        )
        
        assert completion.id == "chatcmpl-123"
        assert completion.object == "chat.completion"
        assert completion.model == "friday_big"
        assert len(completion.choices) == 1
        assert completion.choices[0].message.content == "Hello!"
    
    def test_chat_completion_from_dict(self):
        """Тест парсингу ChatCompletion з dict"""
        data = {
            "id": "test-id",
            "created": 123,
            "model": "friday_big",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Response text"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        
        completion = ChatCompletion(**data)
        assert completion.id == "test-id"
        assert completion.choices[0].message.content == "Response text"
    
    def test_chat_completion_to_dict(self):
        """Тест серіалізації ChatCompletion у dict"""
        completion = ChatCompletion(
            id="test",
            created=123,
            model="friday_big",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content="Hi"),
                    finish_reason="stop"
                )
            ]
        )
        
        data = completion.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == "test"
        assert data["model"] == "friday_big"
    
    def test_chat_completion_to_json(self):
        """Тест серіалізації ChatCompletion у JSON"""
        completion = ChatCompletion(
            id="test",
            created=123,
            model="friday_big",
            choices=[]
        )
        
        json_str = completion.to_json()
        assert isinstance(json_str, str)
        assert '"id":"test"' in json_str or '"id": "test"' in json_str


class TestChatCompletionChunk:
    """Тести для ChatCompletionChunk model"""
    
    def test_chunk_creation(self):
        """Тест створення streaming chunk"""
        chunk = ChatCompletionChunk(
            id="chatcmpl-stream-123",
            created=123,
            model="friday_big",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=Delta(content="Hello"),
                    finish_reason=None
                )
            ]
        )
        
        assert chunk.id == "chatcmpl-stream-123"
        assert chunk.object == "chat.completion.chunk"
        assert chunk.choices[0].delta.content == "Hello"
        assert chunk.choices[0].finish_reason is None
    
    def test_chunk_with_finish_reason(self):
        """Тест останнього chunk з finish_reason"""
        chunk = ChatCompletionChunk(
            id="test",
            created=123,
            model="friday_big",
            choices=[
                ChunkChoice(
                    index=0,
                    delta=Delta(content=None),
                    finish_reason="stop"
                )
            ]
        )
        
        assert chunk.choices[0].finish_reason == "stop"
        assert chunk.choices[0].delta.content is None


# ============================================================================
# Image Models Tests
# ============================================================================


class TestImageModels:
    """Тести для Image models"""
    
    def test_image_response(self):
        """Тест ImageResponse"""
        response = ImageResponse(
            image_url="https://cdn.fridayai.com/img.png"
        )
        assert response.image_url == "https://cdn.fridayai.com/img.png"
    
    def test_image(self):
        """Тест Image (OpenAI format)"""
        img = Image(url="https://example.com/img.jpg")
        assert img.url == "https://example.com/img.jpg"
    
    def test_images_response(self):
        """Тест ImagesResponse"""
        response = ImagesResponse(
            created=123,
            data=[
                Image(url="https://example.com/1.jpg"),
                Image(url="https://example.com/2.jpg")
            ]
        )
        assert len(response.data) == 2
        assert response.data[0].url == "https://example.com/1.jpg"


# ============================================================================
# Audio Models Tests
# ============================================================================


class TestAudioModels:
    """Тести для Audio models"""
    
    def test_audio_response(self):
        """Тест AudioResponse"""
        response = AudioResponse(
            audio_url="https://cdn.fridayai.com/audio.mp3"
        )
        assert response.audio_url == "https://cdn.fridayai.com/audio.mp3"


# ============================================================================
# Embedding Models Tests
# ============================================================================


class TestEmbeddingModels:
    """Тести для Embedding models"""
    
    def test_embedding(self):
        """Тест Embedding"""
        emb = Embedding(
            embedding=[0.1, 0.2, 0.3],
            index=0
        )
        assert emb.object == "embedding"
        assert len(emb.embedding) == 3
        assert emb.index == 0
    
    def test_embedding_response(self):
        """Тест EmbeddingResponse"""
        response = EmbeddingResponse(
            data=[
                Embedding(embedding=[0.1, 0.2], index=0),
                Embedding(embedding=[0.3, 0.4], index=1)
            ],
            model="embedding-model"
        )
        
        assert response.object == "list"
        assert len(response.data) == 2
        assert response.model == "embedding-model"


# ============================================================================
# Collection Models Tests
# ============================================================================


class TestCollectionModels:
    """Тести для Collection models"""
    
    def test_collection_info(self):
        """Тест CollectionInfo"""
        info = CollectionInfo(
            result={"vectors_count": 1000},
            status="ok",
            time=0.123
        )
        assert info.status == "ok"
        assert info.time == 0.123
        assert info.result["vectors_count"] == 1000
    
    def test_point(self):
        """Тест Point"""
        point = Point(
            id="point-1",
            vector=[0.1, 0.2, 0.3],
            payload={"text": "Test", "category": "tech"}
        )
        assert point.id == "point-1"
        assert len(point.vector) == 3
        assert point.payload["text"] == "Test"
    
    def test_point_with_int_id(self):
        """Тест Point з integer ID"""
        point = Point(
            id=123,
            vector=[0.1, 0.2]
        )
        assert point.id == 123
    
    def test_scored_point(self):
        """Тест ScoredPoint"""
        point = ScoredPoint(
            id="point-1",
            score=0.95,
            payload={"text": "Relevant"}
        )
        assert point.score == 0.95
        assert point.payload["text"] == "Relevant"
    
    def test_search_result(self):
        """Тест SearchResult"""
        result = SearchResult(
            result={
                "points": [
                    {"id": "1", "score": 0.95, "payload": {"text": "A"}},
                    {"id": "2", "score": 0.87, "payload": {"text": "B"}}
                ]
            },
            status="ok",
            time=0.05
        )
        
        assert result.status == "ok"
        assert result.count == 2
        assert len(result.points) == 2
        assert result.points[0].score == 0.95
    
    def test_upsert_result(self):
        """Тест UpsertResult"""
        result = UpsertResult(
            result={"operation_id": 123},
            status="ok",
            time=0.1
        )
        assert result.operation_id == 123


# ============================================================================
# Usage Models Tests
# ============================================================================


class TestUsageModels:
    """Тести для Usage models"""
    
    def test_usage_status(self):
        """Тест UsageStatus"""
        status = UsageStatus(
            token_hash="abc123",
            limits=Limits(chat=100, image=50, voice=30),
            usage=Usage(chat=25, image=10, voice=5),
            remaining=Remaining(chat=75, image=40, voice=25)
        )
        
        assert status.token_hash == "abc123"
        assert status.limits.chat == 100
        assert status.usage.chat == 25
        assert status.remaining.chat == 75
    
    def test_chat_log(self):
        """Тест ChatLog"""
        log = ChatLog(
            _id="507f1f77bcf86cd799439011",
            conversation=[{"role": "user", "content": "Hi"}],
            response="Hello!",
            model="friday_big",
            date="2024-01-01"
        )
        
        assert log.id == "507f1f77bcf86cd799439011"
        assert log.model == "friday_big"
        assert len(log.conversation) == 1
    
    def test_user_info(self):
        """Тест UserInfo"""
        info = UserInfo(info="Name: John, Age: 30")
        assert "John" in info.info


# ============================================================================
# Common Models Tests
# ============================================================================


class TestCommonModels:
    """Тести для Common models"""
    
    def test_error_response(self):
        """Тест ErrorResponse"""
        error = ErrorResponse(error="Invalid API key")
        assert error.error == "Invalid API key"
    
    def test_health_response(self):
        """Тест HealthResponse"""
        health = HealthResponse(status="ok")
        assert health.status == "ok"
    
    def test_ok_response(self):
        """Тест OkResponse"""
        ok = OkResponse(ok=True)
        assert ok.ok is True


# ============================================================================
# Helper Functions Tests
# ============================================================================


class TestHelperFunctions:
    """Тести для helper функцій"""
    
    def test_create_chat_completion_from_friday_response(self):
        """Тест конвертації FridayAI response у ChatCompletion"""
        friday_response = {"response": "Hello, how can I help?"}
        
        completion = create_chat_completion_from_friday_response(
            friday_response,
            model="friday_big"
        )
        
        assert isinstance(completion, ChatCompletion)
        assert completion.model == "friday_big"
        assert completion.choices[0].message.content == "Hello, how can I help?"
        assert completion.choices[0].message.role == "assistant"
        assert completion.choices[0].finish_reason == "stop"
        assert completion.id.startswith("chatcmpl-")
    
    def test_create_chat_completion_chunk(self):
        """Тест створення ChatCompletionChunk"""
        chunk = create_chat_completion_chunk(
            content="Hello",
            model="friday_big"
        )
        
        assert isinstance(chunk, ChatCompletionChunk)
        assert chunk.model == "friday_big"
        assert chunk.choices[0].delta.content == "Hello"
        assert chunk.choices[0].finish_reason is None
    
    def test_create_chat_completion_chunk_finish(self):
        """Тест створення останнього chunk"""
        chunk = create_chat_completion_chunk(
            content="",
            model="friday_big",
            finish=True
        )
        
        assert chunk.choices[0].delta.content is None
        assert chunk.choices[0].finish_reason == "stop"


# ============================================================================
# Extra Fields Tests
# ============================================================================


class TestExtraFields:
    """Тести для extra fields (allow config)"""
    
    def test_chat_completion_with_extra_fields(self):
        """Тест що додаткові поля допускаються"""
        completion = ChatCompletion(
            id="test",
            created=123,
            model="friday_big",
            choices=[],
            custom_field="custom_value"  # Додаткове поле
        )
        
        # Pydantic 2.0 зберігає extra fields
        assert hasattr(completion, "custom_field") or "custom_field" in completion.model_extra
    
    def test_message_with_extra_fields(self):
        """Тест що Message допускає extra fields"""
        msg = Message(
            role="user",
            content="Test",
            custom_data={"key": "value"}
        )
        
        # Extra field має бути збережений
        assert hasattr(msg, "custom_data") or "custom_data" in msg.model_extra


# ============================================================================
# Serialization Tests
# ============================================================================


class TestSerialization:
    """Тести для серіалізації моделей"""
    
    def test_model_dump(self):
        """Тест model_dump()"""
        msg = Message(role="user", content="Test")
        data = msg.model_dump()
        
        assert isinstance(data, dict)
        assert data["role"] == "user"
        assert data["content"] == "Test"
    
    def test_model_dump_json(self):
        """Тест model_dump_json()"""
        msg = Message(role="user", content="Test")
        json_str = msg.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "user" in json_str
        assert "Test" in json_str
    
    def test_model_dump_exclude(self):
        """Тест exclude певних полів"""
        completion = ChatCompletion(
            id="test",
            created=123,
            model="friday_big",
            choices=[]
        )
        
        data = completion.model_dump(exclude={"created"})
        assert "created" not in data
        assert "id" in data


# ============================================================================
# Запуск тестів
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])