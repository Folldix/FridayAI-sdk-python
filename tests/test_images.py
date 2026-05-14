"""
Unit тести для Images resource
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "friday" / "resources"))
sys.path.insert(0, str(PROJECT_ROOT / "friday"))

# Mock залежності
class MockImageResponse:
    def __init__(self, **kwargs):
        self.image_url = kwargs.get("image_url", "https://test.com/image.png")

sys.modules['_models'] = Mock()
sys.modules['_models'].ImageResponse = MockImageResponse

from images import Images


class TestImagesGenerate:
    """Тести для generate методу"""
    
    def test_generate_basic(self):
        """Тест базової генерації"""
        client = Mock()
        client._make_request = Mock(return_value={
            "image_url": "https://cdn.fridayai.com/test.png"
        })
        
        images = Images(client)
        result = images.generate(prompt="A sunset")
        
        # Перевірки
        assert isinstance(result, MockImageResponse)
        assert result.image_url == "https://cdn.fridayai.com/test.png"
        
        # Перевірка API call
        client._make_request.assert_called_once()
        call_args = client._make_request.call_args
        
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/generate-image"
        assert call_args[1]["json"]["payload"] == "A sunset"
        assert call_args[1]["json"]["size"] == "1024x1024"
    
    def test_generate_with_size(self):
        """Тест з кастомним розміром"""
        client = Mock()
        client._make_request = Mock(return_value={
            "image_url": "https://cdn.fridayai.com/test.png"
        })
        
        images = Images(client)
        result = images.generate(
            prompt="A cat",
            size="512x512"
        )
        
        # Перевірка розміру в payload
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["size"] == "512x512"
    
    def test_generate_empty_prompt(self):
        """Тест що порожній prompt викликає помилку"""
        client = Mock()
        images = Images(client)
        
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            images.generate(prompt="")
        
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            images.generate(prompt="   ")
    
    def test_generate_with_kwargs(self):
        """Тест з додатковими kwargs"""
        client = Mock()
        client._make_request = Mock(return_value={
            "image_url": "https://test.com/img.png"
        })
        
        images = Images(client)
        result = images.generate(
            prompt="Test",
            custom_param="value"
        )
        
        # Перевірка що kwargs додано
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["custom_param"] == "value"


class TestImagesEdit:
    """Тести для edit методу"""
    
    def test_edit_basic(self):
        """Тест базового редагування"""
        client = Mock()
        client._make_request = Mock(return_value={
            "image_url": "https://cdn.fridayai.com/edited.png"
        })
        
        images = Images(client)
        result = images.edit(
            image_url="https://example.com/original.jpg",
            prompt="Add a rainbow"
        )
        
        # Перевірки
        assert result.image_url == "https://cdn.fridayai.com/edited.png"
        
        # Перевірка API call
        client._make_request.assert_called_once()
        call_args = client._make_request.call_args
        
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/modify-image"
        
        payload = call_args[1]["json"]
        assert payload["image_url"] == "https://example.com/original.jpg"
        assert payload["payload"] == "Add a rainbow"
        assert payload["size"] == "1024x1024"
    
    def test_edit_empty_image_url(self):
        """Тест що порожній image_url викликає помилку"""
        client = Mock()
        images = Images(client)
        
        with pytest.raises(ValueError, match="image_url is required"):
            images.edit(image_url="", prompt="Test")
    
    def test_edit_empty_prompt(self):
        """Тест що порожній prompt викликає помилку"""
        client = Mock()
        images = Images(client)
        
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            images.edit(
                image_url="https://example.com/img.jpg",
                prompt=""
            )
    
    def test_edit_with_size(self):
        """Тест редагування з кастомним розміром"""
        client = Mock()
        client._make_request = Mock(return_value={
            "image_url": "https://test.com/edited.png"
        })
        
        images = Images(client)
        result = images.edit(
            image_url="https://example.com/original.jpg",
            prompt="Change style",
            size="512x512"
        )
        
        # Перевірка розміру
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["size"] == "512x512"


class TestImagesInit:
    """Тести для ініціалізації"""
    
    def test_init(self):
        """Тест ініціалізації Images"""
        client = Mock()
        images = Images(client)
        
        assert images._client == client


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])