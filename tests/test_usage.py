"""
Unit тести для Usage resource
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "friday" / "resources"))
sys.path.insert(0, str(PROJECT_ROOT / "friday"))

# Mock models
class MockUsageStatus:
    def __init__(self, **kwargs):
        self.limits = kwargs.get("limits", {})
        self.usage = kwargs.get("usage", {})

class MockChatLog:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test")

class MockChatLogsResponse:
    def __init__(self, **kwargs):
        self.items = kwargs.get("items", [])

class MockUserInfo:
    def __init__(self, **kwargs):
        self.info = kwargs.get("info", "")

sys.modules['_models'] = Mock()
sys.modules['_models'].UsageStatus = MockUsageStatus
sys.modules['_models'].ChatLog = MockChatLog
sys.modules['_models'].ChatLogsResponse = MockChatLogsResponse
sys.modules['_models'].UserInfo = MockUserInfo
sys.modules['_models'].OkResponse = dict

from usage import Usage, Logs, Users


class TestUsageRetrieve:
    """Тести для Usage.retrieve()"""
    
    def test_retrieve(self):
        """Тест отримання статусу"""
        client = Mock()
        client.api_key = "test-key"
        client._make_request = Mock(return_value={
            "limits": {"chat": 100},
            "usage": {"chat": 25},
            "remaining": {"chat": 75}
        })
        
        usage = Usage(client)
        result = usage.retrieve()
        
        assert isinstance(result, MockUsageStatus)
        client._make_request.assert_called_once_with(
            "GET",
            "/usage/status",
            params={"token": "test-key"}
        )


class TestLogs:
    """Тести для Logs"""
    
    def test_list(self):
        """Тест списку логів"""
        client = Mock()
        client.api_key = "test-key"
        client._make_request = Mock(return_value={
            "items": [{"id": "1"}, {"id": "2"}]
        })
        
        logs = Logs(client)
        result = logs.list()
        
        assert isinstance(result, MockChatLogsResponse)
    
    def test_retrieve(self):
        """Тест отримання логу"""
        client = Mock()
        client.api_key = "test-key"
        client._make_request = Mock(return_value={"id": "abc"})
        
        logs = Logs(client)
        result = logs.retrieve(id="abc")
        
        assert isinstance(result, MockChatLog)


class TestUsers:
    """Тести для Users"""
    
    def test_retrieve(self):
        """Тест отримання інформації"""
        client = Mock()
        client.api_key = "test-key"
        client._make_request = Mock(return_value={"info": "test"})
        
        users = Users(client)
        result = users.retrieve()
        
        assert isinstance(result, MockUserInfo)
    
    def test_update(self):
        """Тест оновлення"""
        client = Mock()
        client.api_key = "test-key"
        client._make_request = Mock(return_value={"ok": True})
        
        users = Users(client)
        result = users.update(info="New info")
        
        assert result["ok"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
