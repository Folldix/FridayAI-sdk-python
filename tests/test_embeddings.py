"""
Unit тести для Embeddings resource
"""

import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock залежності
class MockEmbedding:
    def __init__(self, **kwargs):
        self.object = kwargs.get("object", "embedding")
        self.embedding = kwargs.get("embedding", [])
        self.index = kwargs.get("index", 0)

class MockEmbeddingResponse:
    def __init__(self, **kwargs):
        self.object = kwargs.get("object", "list")
        self.data = kwargs.get("data", [])
        self.model = kwargs.get("model", "embedding-model")
        self.usage = kwargs.get("usage")

sys.modules['_models'] = Mock()
sys.modules['_models'].Embedding = MockEmbedding
sys.modules['_models'].EmbeddingResponse = MockEmbeddingResponse

from embeddings import Embeddings


class TestEmbeddingsCreate:
    """Тести для create методу"""
    
    def test_create_single_text(self):
        """Тест створення embedding для одного тексту"""
        client = Mock()
        client._make_request = Mock(return_value={
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3],
                    "index": 0
                }
            ],
            "object": "list",
            "model": "embedding-model"
        })
        
        embeddings = Embeddings(client)
        result = embeddings.create(
            input="Hello, world!",
            model="embedding-model"
        )
        
        # Перевірки
        assert isinstance(result, MockEmbeddingResponse)
        assert result.object == "list"
        assert len(result.data) == 1
        
        # Перевірка API call
        client._make_request.assert_called_once()
        call_args = client._make_request.call_args
        
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/embeddings"
        assert call_args[1]["json"]["input"] == "Hello, world!"
        assert call_args[1]["json"]["model"] == "embedding-model"
    
    def test_create_multiple_texts(self):
        """Тест batch embeddings"""
        client = Mock()
        client._make_request = Mock(return_value={
            "data": [
                {"object": "embedding", "embedding": [0.1], "index": 0},
                {"object": "embedding", "embedding": [0.2], "index": 1},
                {"object": "embedding", "embedding": [0.3], "index": 2}
            ],
            "object": "list",
            "model": "embedding-model"
        })
        
        embeddings = Embeddings(client)
        result = embeddings.create(
            input=["Text 1", "Text 2", "Text 3"],
            model="embedding-model"
        )
        
        # Перевірки
        assert len(result.data) == 3
        
        # Перевірка input в payload
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["input"] == ["Text 1", "Text 2", "Text 3"]
    
    def test_create_empty_input_string(self):
        """Тест що порожній string викликає помилку"""
        client = Mock()
        embeddings = Embeddings(client)
        
        with pytest.raises(ValueError, match="input cannot be empty"):
            embeddings.create(input="")
    
    def test_create_empty_input_list(self):
        """Тест що порожній список викликає помилку"""
        client = Mock()
        embeddings = Embeddings(client)
        
        with pytest.raises(ValueError, match="input list cannot be empty"):
            embeddings.create(input=[])
    
    def test_create_with_kwargs(self):
        """Тест з додатковими kwargs"""
        client = Mock()
        client._make_request = Mock(return_value={
            "data": [{"object": "embedding", "embedding": [0.1], "index": 0}],
            "object": "list",
            "model": "embedding-model"
        })
        
        embeddings = Embeddings(client)
        result = embeddings.create(
            input="Test",
            model="embedding-model",
            custom_param="value"
        )
        
        # Перевірка kwargs
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["custom_param"] == "value"
    
    def test_parse_response_openai_format(self):
        """Тест парсингу OpenAI формату"""
        client = Mock()
        client._make_request = Mock(return_value={
            "data": [
                {"object": "embedding", "embedding": [0.1, 0.2], "index": 0}
            ],
            "object": "list",
            "model": "test-model"
        })
        
        embeddings = Embeddings(client)
        result = embeddings.create(input="Test")
        
        assert result.object == "list"
        assert result.model == "test-model"
    
    def test_parse_response_fridayai_format(self):
        """Тест парсингу FridayAI формату"""
        client = Mock()
        # FridayAI може повернути просто embedding
        client._make_request = Mock(return_value={
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        })
        
        embeddings = Embeddings(client)
        result = embeddings.create(input="Test")
        
        # Має конвертуватися в OpenAI формат
        assert result.object == "list"
        assert len(result.data) == 1
        assert result.data[0].embedding == [0.1, 0.2, 0.3, 0.4, 0.5]


class TestEmbeddingsInit:
    """Тести для ініціалізації"""
    
    def test_init(self):
        """Тест ініціалізації Embeddings"""
        client = Mock()
        embeddings = Embeddings(client)
        
        assert embeddings._client == client


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])