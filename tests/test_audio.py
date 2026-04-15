"""
Unit тести для Audio resource
"""

import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock залежності
class MockAudioResponse:
    def __init__(self, **kwargs):
        self.audio_url = kwargs.get("audio_url", "https://test.com/audio.mp3")

sys.modules['_models'] = Mock()
sys.modules['_models'].AudioResponse = MockAudioResponse

from audio import Audio, Speech


class TestSpeechCreate:
    """Тести для create методу"""
    
    def test_create_basic(self):
        """Тест базової генерації"""
        client = Mock()
        client._make_request = Mock(return_value={
            "audio_url": "https://cdn.fridayai.com/test.mp3"
        })
        
        speech = Speech(client)
        result = speech.create(input="Hello, world!")
        
        # Перевірки
        assert isinstance(result, MockAudioResponse)
        assert result.audio_url == "https://cdn.fridayai.com/test.mp3"
        
        # Перевірка API call
        client._make_request.assert_called_once()
        call_args = client._make_request.call_args
        
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/generate-voice"
        assert call_args[1]["json"]["payload"] == "Hello, world!"
        assert call_args[1]["json"]["emotion"] == "neutral"
    
    def test_create_with_emotion(self):
        """Тест з кастомною емоцією"""
        client = Mock()
        client._make_request = Mock(return_value={
            "audio_url": "https://cdn.fridayai.com/happy.mp3"
        })
        
        speech = Speech(client)
        result = speech.create(
            input="I'm happy!",
            emotion="happy"
        )
        
        # Перевірка emotion в payload
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["emotion"] == "happy"
        assert call_args["json"]["payload"] == "I'm happy!"
    
    def test_create_empty_input(self):
        """Тест що порожній input викликає помилку"""
        client = Mock()
        speech = Speech(client)
        
        with pytest.raises(ValueError, match="input cannot be empty"):
            speech.create(input="")
        
        with pytest.raises(ValueError, match="input cannot be empty"):
            speech.create(input="   ")
    
    def test_create_with_kwargs(self):
        """Тест з додатковими kwargs"""
        client = Mock()
        client._make_request = Mock(return_value={
            "audio_url": "https://test.com/audio.mp3"
        })
        
        speech = Speech(client)
        result = speech.create(
            input="Test",
            custom_param="value"
        )
        
        # Перевірка що kwargs додано
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["custom_param"] == "value"
    
    def test_create_different_emotions(self):
        """Тест різних емоцій"""
        client = Mock()
        client._make_request = Mock(return_value={
            "audio_url": "https://test.com/audio.mp3"
        })
        
        speech = Speech(client)
        
        emotions = ["neutral", "happy", "sad", "angry", "excited"]
        
        for emotion in emotions:
            speech.create(input="Test", emotion=emotion)
            
            call_args = client._make_request.call_args[1]
            assert call_args["json"]["emotion"] == emotion


class TestAudio:
    """Тести для Audio класу"""
    
    def test_init(self):
        """Тест ініціалізації Audio"""
        client = Mock()
        audio = Audio(client)
        
        assert audio._speech is not None
        assert isinstance(audio._speech, Speech)
    
    def test_speech_property(self):
        """Тест speech property"""
        client = Mock()
        audio = Audio(client)
        
        speech = audio.speech
        assert isinstance(speech, Speech)
        assert speech == audio._speech


class TestSpeechInit:
    """Тести для ініціалізації"""
    
    def test_init(self):
        """Тест ініціалізації Speech"""
        client = Mock()
        speech = Speech(client)
        
        assert speech._client == client


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])