"""
Unit тести для модуля _utils.py

Тестує всі utility функції.
"""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _utils import (
    # Format conversion
    convert_friday_to_openai_format,
    prepare_messages,
    # Encoding
    encode_image_to_base64,
    encode_file_to_base64,
    is_base64_url,
    # Streaming
    parse_sse_event,
    # ID generation
    generate_chat_id,
    generate_request_id,
    # Validation
    validate_model_name,
    validate_messages,
    # Miscellaneous
    compute_file_hash,
    truncate_text,
    merge_dicts,
    # Constants
    VALID_MODELS,
    VALID_ROLES,
)


# ============================================================================
# Format Conversion Tests
# ============================================================================


class TestConvertFridayToOpenAI:
    """Тести для convert_friday_to_openai_format"""
    
    def test_basic_conversion(self):
        """Тест базової конвертації"""
        friday_response = {"response": "Hello, how can I help?"}
        
        result = convert_friday_to_openai_format(
            friday_response,
            model="friday_big"
        )
        
        assert result["object"] == "chat.completion"
        assert result["model"] == "friday_big"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert result["choices"][0]["message"]["content"] == "Hello, how can I help?"
        assert result["choices"][0]["finish_reason"] == "stop"
    
    def test_with_custom_request_id(self):
        """Тест з кастомним request_id"""
        friday_response = {"response": "Test"}
        
        result = convert_friday_to_openai_format(
            friday_response,
            model="friday_medium",
            request_id="custom-id-123"
        )
        
        assert result["id"] == "custom-id-123"
    
    def test_generates_id_if_not_provided(self):
        """Тест що ID генерується автоматично"""
        friday_response = {"response": "Test"}
        
        result = convert_friday_to_openai_format(friday_response)
        
        assert "id" in result
        assert result["id"].startswith("chatcmpl-")


class TestPrepareMessages:
    """Тести для prepare_messages"""
    
    def test_from_string(self):
        """Тест конвертації з string"""
        result = prepare_messages("Hello, Friday!")
        
        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello, Friday!"
    
    def test_from_list(self):
        """Тест з list of dicts"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        result = prepare_messages(messages)
        
        assert result == messages
    
    def test_from_single_dict(self):
        """Тест з одного dict"""
        message = {"role": "user", "content": "Test"}
        
        result = prepare_messages(message)
        
        assert len(result) == 1
        assert result[0] == message
    
    def test_with_system_prompt(self):
        """Тест з system prompt"""
        result = prepare_messages(
            "User message",
            system_prompt="You are a helpful assistant"
        )
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[0]["content"] == "You are a helpful assistant"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "User message"
    
    def test_invalid_type(self):
        """Тест з невалідним типом"""
        with pytest.raises(ValueError, match="messages must be"):
            prepare_messages(123)


# ============================================================================
# Encoding Tests
# ============================================================================


class TestEncoding:
    """Тести для encoding функцій"""
    
    def test_encode_image_to_base64(self, tmp_path):
        """Тест кодування зображення"""
        # Створюємо тестовий файл
        img_file = tmp_path / "test.png"
        img_file.write_bytes(b"fake image data")
        
        result = encode_image_to_base64(str(img_file), format="PNG")
        
        assert result.startswith("data:image/png;base64,")
        assert len(result) > 30
    
    def test_encode_image_file_not_found(self):
        """Тест що помилка викидається для неіснуючого файлу"""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64("nonexistent.jpg")
    
    def test_encode_file_to_base64(self, tmp_path):
        """Тест кодування файлу"""
        # Створюємо тестовий PDF файл
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf data")
        
        result = encode_file_to_base64(str(pdf_file))
        
        assert result.startswith("data:")
        assert "base64," in result
    
    def test_encode_file_with_custom_mime_type(self, tmp_path):
        """Тест з кастомним MIME type"""
        file = tmp_path / "data.csv"
        file.write_bytes(b"a,b,c\n1,2,3")
        
        result = encode_file_to_base64(str(file), mime_type="text/csv")
        
        assert result.startswith("data:text/csv;base64,")
    
    def test_is_base64_url(self):
        """Тест перевірки base64 URL"""
        assert is_base64_url("data:image/png;base64,iVBOR...") is True
        assert is_base64_url("https://example.com/image.jpg") is False
        assert is_base64_url("data:application/pdf;base64,JVB...") is True


# ============================================================================
# Streaming Tests
# ============================================================================


class TestStreaming:
    """Тести для streaming функцій"""
    
    def test_parse_sse_event_with_json(self):
        """Тест парсингу JSON SSE event"""
        line = 'data: {"id": "123", "object": "chat.completion.chunk"}'
        
        result = parse_sse_event(line)
        
        assert result is not None
        assert result["id"] == "123"
        assert result["object"] == "chat.completion.chunk"
    
    def test_parse_sse_event_done(self):
        """Тест парсингу [DONE]"""
        line = 'data: [DONE]'
        
        result = parse_sse_event(line)
        
        assert result is None
    
    def test_parse_sse_event_invalid_json(self):
        """Тест невалідного JSON"""
        line = 'data: {invalid json}'
        
        result = parse_sse_event(line)
        
        assert result is None
    
    def test_parse_sse_event_no_prefix(self):
        """Тест рядка без data: prefix"""
        line = '{"id": "123"}'
        
        result = parse_sse_event(line)
        
        assert result is None


# ============================================================================
# ID Generation Tests
# ============================================================================


class TestIDGeneration:
    """Тести для генерації IDs"""
    
    def test_generate_chat_id(self):
        """Тест генерації chat ID"""
        id1 = generate_chat_id()
        id2 = generate_chat_id()
        
        assert id1.startswith("chatcmpl-")
        assert id2.startswith("chatcmpl-")
        assert id1 != id2  # Мають бути унікальні
        assert len(id1) > 10
    
    def test_generate_chat_id_custom_prefix(self):
        """Тест з кастомним prefix"""
        result = generate_chat_id(prefix="custom")
        
        assert result.startswith("custom-")
    
    def test_generate_request_id(self):
        """Тест генерації request ID"""
        id1 = generate_request_id()
        id2 = generate_request_id()
        
        # UUID формат
        assert len(id1) == 36
        assert "-" in id1
        assert id1 != id2


# ============================================================================
# Validation Tests
# ============================================================================


class TestValidation:
    """Тести для validation функцій"""
    
    def test_validate_model_name_valid(self):
        """Тест валідації правильних моделей"""
        assert validate_model_name("friday_big") == "friday_big"
        assert validate_model_name("friday_medium") == "friday_medium"
    
    def test_validate_model_name_invalid(self):
        """Тест валідації невалідної моделі"""
        with pytest.raises(ValueError, match="Invalid model name"):
            validate_model_name("gpt-4")
    
    def test_validate_messages_valid(self):
        """Тест валідації правильних messages"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        
        # Не повинно викидати помилку
        validate_messages(messages)
    
    def test_validate_messages_empty(self):
        """Тест валідації порожнього списку"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_messages([])
    
    def test_validate_messages_missing_role(self):
        """Тест валідації messages без role"""
        messages = [{"content": "Hello"}]
        
        with pytest.raises(ValueError, match="missing 'role'"):
            validate_messages(messages)
    
    def test_validate_messages_missing_content(self):
        """Тест валідації messages без content"""
        messages = [{"role": "user"}]
        
        with pytest.raises(ValueError, match="missing 'content'"):
            validate_messages(messages)
    
    def test_validate_messages_invalid_role(self):
        """Тест валідації messages з невалідною роллю"""
        messages = [{"role": "invalid", "content": "Hello"}]
        
        with pytest.raises(ValueError, match="invalid role"):
            validate_messages(messages)


# ============================================================================
# Miscellaneous Tests
# ============================================================================


class TestMiscellaneous:
    """Тести для miscellaneous функцій"""
    
    def test_compute_file_hash(self, tmp_path):
        """Тест обчислення hash файлу"""
        file = tmp_path / "test.txt"
        file.write_text("test content")
        
        hash_result = compute_file_hash(str(file))
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA256 hash length
    
    def test_truncate_text(self):
        """Тест обрізання тексту"""
        text = "This is a very long text that should be truncated"
        
        result = truncate_text(text, max_length=20)
        
        assert len(result) == 20
        assert result.endswith("...")
    
    def test_truncate_text_short(self):
        """Тест що короткий текст не обрізається"""
        text = "Short"
        
        result = truncate_text(text, max_length=20)
        
        assert result == "Short"
    
    def test_merge_dicts(self):
        """Тест об'єднання словників"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = {"d": 5}
        
        result = merge_dicts(dict1, dict2, dict3)
        
        assert result == {"a": 1, "b": 3, "c": 4, "d": 5}


# ============================================================================
# Constants Tests
# ============================================================================


class TestConstants:
    """Тести для констант"""
    
    def test_valid_models(self):
        """Тест що VALID_MODELS містить правильні моделі"""
        assert "friday_big" in VALID_MODELS
        assert "friday_medium" in VALID_MODELS
        assert len(VALID_MODELS) == 2
    
    def test_valid_roles(self):
        """Тест що VALID_ROLES містить правильні ролі"""
        assert "user" in VALID_ROLES
        assert "assistant" in VALID_ROLES
        assert "system" in VALID_ROLES
        assert len(VALID_ROLES) == 3


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])