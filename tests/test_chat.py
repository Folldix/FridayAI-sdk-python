"""
Unit тести для Chat resource
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "friday" / "resources"))
sys.path.insert(0, str(PROJECT_ROOT / "friday"))

# Mock залежності для тестів без реальних бібліотек
class MockChatCompletion:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-id")
        self.choices = kwargs.get("choices", [])
        self.model = kwargs.get("model", "friday_big")

class MockChatCompletionChunk:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-id")
        self.choices = kwargs.get("choices", [])

# Mock modules
sys.modules['_models'] = Mock()
sys.modules['_models'].ChatCompletion = MockChatCompletion
sys.modules['_models'].ChatCompletionChunk = MockChatCompletionChunk

from chat import Chat, Completions


class TestCompletions:
    """Тести для Completions класу"""
    
    def test_init(self):
        """Тест ініціалізації"""
        client = Mock()
        completions = Completions(client)
        assert completions._client == client
    
    def test_create_basic_mock(self):
        """Тест базового create з mock"""
        client = Mock()
        client._make_request = Mock(return_value={"response": "Hello!"})
        
        completions = Completions(client)
        
        # Mock utils функції
        with patch('chat.validate_model_name'), \
             patch('chat.prepare_messages', return_value=[{"role": "user", "content": "Hi"}]), \
             patch('chat.validate_messages'), \
             patch('chat.convert_friday_to_openai_format', return_value={
                 "id": "test",
                 "object": "chat.completion",
                 "created": 123,
                 "model": "friday_big",
                 "choices": []
             }):
            
            response = completions.create(
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            # Перевірка що запит виконано
            client._make_request.assert_called_once()
            call_args = client._make_request.call_args
            
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/chat/completions"
            assert call_args[1]["json"]["conversation"] == [{"role": "user", "content": "Hi"}]

    def test_create_prompt_alias(self):
        client = Mock()
        client._make_request = Mock(return_value={"response": "Hello!"})

        completions = Completions(client)

        with patch('chat.validate_model_name'), \
             patch('chat.prepare_messages', return_value=[{"role": "user", "content": "Hi"}]), \
             patch('chat.validate_messages'), \
             patch('chat.convert_friday_to_openai_format', return_value={
                 "id": "test",
                 "object": "chat.completion",
                 "created": 123,
                 "model": "friday_big",
                 "choices": []
             }):
            completions.create(prompt="Hi")

        assert client._make_request.call_args[1]["json"]["conversation"] == [
            {"role": "user", "content": "Hi"}
        ]


class TestChat:
    """Тести для Chat класу"""
    
    def test_init(self):
        """Тест ініціалізації Chat"""
        client = Mock()
        chat = Chat(client)
        
        assert chat._completions is not None
        assert isinstance(chat._completions, Completions)
    
    def test_completions_property(self):
        """Тест completions property"""
        client = Mock()
        chat = Chat(client)
        
        completions = chat.completions
        assert isinstance(completions, Completions)

    def test_message_endpoint(self):
        client = Mock()
        client._make_request = Mock(return_value={"response": "ok"})
        chat = Chat(client)

        with patch('chat.validate_model_name'), \
             patch('chat.prepare_messages', return_value=[{"role": "user", "content": "Hi"}]), \
             patch('chat.validate_messages'):
            result = chat.message(prompt="Hi", model="friday_medium")

        assert result == {"response": "ok"}
        client._make_request.assert_called_once_with(
            "POST",
            "/message",
            json={
                "conversation": [{"role": "user", "content": "Hi"}],
                "model": "friday_medium",
            }
        )

    def test_bot_endpoint(self):
        client = Mock()
        client._make_request = Mock(return_value={"response": "ok"})
        chat = Chat(client)

        with patch('chat.validate_model_name'), \
             patch('chat.prepare_messages', return_value=[{"role": "user", "content": "Hi"}]), \
             patch('chat.validate_messages'):
            chat.bot(prompt="Hi", clients=[{"id": "client-1"}])

        assert client._make_request.call_args[0] == ("POST", "/bot")
        assert client._make_request.call_args[1]["json"]["clients"] == [{"id": "client-1"}]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
