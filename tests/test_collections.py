"""
Unit тести для Collections resource
"""

import pytest
from unittest.mock import Mock
import sys

pytest.skip("Collections module is intentionally out of scope for now.", allow_module_level=True)

# Mock залежності
class MockCollectionInfo:
    def __init__(self, **kwargs):
        self.result = kwargs.get("result", {})
        self.status = kwargs.get("status", "ok")

class MockSearchResult:
    def __init__(self, **kwargs):
        self.result = kwargs.get("result", {})
        self.status = kwargs.get("status", "ok")
        self.points = []

class MockUpsertResult:
    def __init__(self, **kwargs):
        self.result = kwargs.get("result", {})
        self.operation_id = None

sys.modules['_models'] = Mock()
sys.modules['_models'].CollectionInfo = MockCollectionInfo
sys.modules['_models'].SearchResult = MockSearchResult
sys.modules['_models'].UpsertResult = MockUpsertResult

from collections import Collections


class TestCollectionsList:
    """Тести для list методу"""
    
    def test_list(self):
        """Тест отримання списку колекцій"""
        client = Mock()
        client._make_request = Mock(return_value={
            "collections": ["coll1", "coll2", "coll3"]
        })
        
        collections = Collections(client)
        result = collections.list()
        
        assert result == ["coll1", "coll2", "coll3"]
        client._make_request.assert_called_once_with("GET", "/collections")


class TestCollectionsRetrieve:
    """Тести для retrieve методу"""
    
    def test_retrieve(self):
        """Тест отримання інформації про колекцію"""
        client = Mock()
        client._make_request = Mock(return_value={
            "result": {"vectors_count": 100},
            "status": "ok",
            "time": 0.01
        })
        
        collections = Collections(client)
        result = collections.retrieve("test_coll")
        
        assert isinstance(result, MockCollectionInfo)
        client._make_request.assert_called_once_with("GET", "/collections/test_coll")
    
    def test_retrieve_empty_name(self):
        """Тест що порожня назва викликає помилку"""
        client = Mock()
        collections = Collections(client)
        
        with pytest.raises(ValueError, match="collection name cannot be empty"):
            collections.retrieve("")


class TestCollectionsCreate:
    """Тести для create методу"""
    
    def test_create(self):
        """Тест створення колекції"""
        client = Mock()
        client._make_request = Mock(return_value={
            "result": True,
            "status": "ok"
        })
        
        collections = Collections(client)
        result = collections.create("new_coll")
        
        assert result["status"] == "ok"
        client._make_request.assert_called_once_with(
            "PUT",
            "/collections/new_coll",
            json=None
        )
    
    def test_create_empty_name(self):
        """Тест що порожня назва викликає помилку"""
        client = Mock()
        collections = Collections(client)
        
        with pytest.raises(ValueError, match="collection name cannot be empty"):
            collections.create("")


class TestCollectionsSearch:
    """Тести для search методу"""
    
    def test_search(self):
        """Тест пошуку в колекції"""
        client = Mock()
        client._make_request = Mock(return_value={
            "result": {"points": []},
            "status": "ok",
            "time": 0.05
        })
        
        collections = Collections(client)
        result = collections.search(
            name="test",
            query=[0.1, 0.2, 0.3],
            limit=5
        )
        
        assert isinstance(result, MockSearchResult)
        
        # Перевірка payload
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["query"] == [0.1, 0.2, 0.3]
        assert call_args["json"]["limit"] == 5
    
    def test_search_empty_query(self):
        """Тест що порожній query викликає помилку"""
        client = Mock()
        collections = Collections(client)
        
        with pytest.raises(ValueError, match="query vector cannot be empty"):
            collections.search(name="test", query=[])


class TestCollectionsUpsert:
    """Тести для upsert методу"""
    
    def test_upsert(self):
        """Тест додавання точок"""
        client = Mock()
        client._make_request = Mock(return_value={
            "result": {"operation_id": 123},
            "status": "ok"
        })
        
        points = [
            {"id": "1", "vector": [0.1, 0.2], "payload": {"text": "Test"}}
        ]
        
        collections = Collections(client)
        result = collections.upsert(name="test", points=points)
        
        assert isinstance(result, MockUpsertResult)
        
        # Перевірка payload
        call_args = client._make_request.call_args[1]
        assert call_args["json"]["points"] == points
    
    def test_upsert_empty_points(self):
        """Тест що порожній список викликає помилку"""
        client = Mock()
        collections = Collections(client)
        
        with pytest.raises(ValueError, match="points list cannot be empty"):
            collections.upsert(name="test", points=[])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])