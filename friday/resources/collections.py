"""
Collections Resource для FridayAI SDK.

Забезпечує доступ до Qdrant vector database API для зберігання та пошуку векторів.
"""

from typing import List, Dict, Optional, Any, Union
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _client import BaseClient, AsyncClient
from _models import CollectionInfo, SearchResult, UpsertResult


class Collections:
    """
    Collections resource для роботи з vector database (Qdrant).
    
    Забезпечує методи для:
    - CRUD операцій з колекціями
    - Пошуку схожих векторів
    - Додавання/оновлення точок
    - Фільтрації результатів
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Створення колекції
        >>> client.collections.create("my_docs")
        >>> 
        >>> # Додавання даних
        >>> client.collections.upsert(
        ...     name="my_docs",
        ...     points=[{"id": "1", "vector": [...], "payload": {...}}]
        ... )
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Collections resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
    
    def list(self) -> List[str]:
        """
        Повертає список всіх колекцій.
        
        Returns:
            Список назв колекцій
        
        Example:
            >>> collections = client.collections.list()
            >>> print(collections)
            ['my_docs', 'products', 'articles']
        """
        response = self._client._make_request(
            "GET",
            "/collections"
        )
        
        # API повертає {"collections": [...]}
        return response.get("collections", [])
    
    def retrieve(self, name: str) -> CollectionInfo:
        """
        Повертає інформацію про колекцію.
        
        Args:
            name: Назва колекції
        
        Returns:
            CollectionInfo з деталями колекції
        
        Raises:
            ValueError: Якщо name порожній
            NotFoundError: Якщо колекція не існує
        
        Example:
            >>> info = client.collections.retrieve("my_docs")
            >>> print(info.result)
        """
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = self._client._make_request(
            "GET",
            f"/collections/{name}"
        )
        
        return CollectionInfo(**response)
    
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Створює нову колекцію.
        
        Args:
            name: Назва колекції
            **kwargs: Додаткові параметри конфігурації
        
        Returns:
            Dict з результатом створення
        
        Raises:
            ValueError: Якщо name порожній
            APIError: При помилках створення
        
        Example:
            >>> result = client.collections.create("my_docs")
            >>> print(result)
        """
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = self._client._make_request(
            "PUT",
            f"/collections/{name}",
            json=kwargs if kwargs else None
        )
        
        return response
    
    def delete(self, name: str) -> Dict[str, Any]:
        """
        Видаляє колекцію.
        
        Args:
            name: Назва колекції
        
        Returns:
            Dict з результатом видалення
        
        Raises:
            ValueError: Якщо name порожній
            NotFoundError: Якщо колекція не існує
        
        Example:
            >>> result = client.collections.delete("old_collection")
            >>> print(result)
        """
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = self._client._make_request(
            "DELETE",
            f"/collections/{name}"
        )
        
        return response
    
    def search(
        self,
        name: str,
        *,
        query: List[float],
        limit: int = 10,
        score_threshold: float = 0.0,
        filter: Optional[Dict] = None,
        **kwargs
    ) -> SearchResult:
        """
        Пошук схожих векторів у колекції.
        
        Args:
            name: Назва колекції
            query: Вектор для пошуку
            limit: Максимальна кількість результатів (за замовчуванням 10)
            score_threshold: Мінімальний score (за замовчуванням 0.0)
            filter: Фільтр для результатів (опціонально)
            **kwargs: Додаткові параметри пошуку
        
        Returns:
            SearchResult з знайденими точками
        
        Raises:
            ValueError: Якщо параметри невалідні
            NotFoundError: Якщо колекція не існує
        
        Example:
            >>> # Генерація query embedding
            >>> query_emb = client.embeddings.create(input="search text")
            >>> 
            >>> # Пошук схожих
            >>> results = client.collections.search(
            ...     name="my_docs",
            ...     query=query_emb.data[0].embedding,
            ...     limit=5,
            ...     score_threshold=0.7
            ... )
            >>> 
            >>> for point in results.points:
            ...     print(f"ID: {point.id}, Score: {point.score}")
            ...     print(f"Text: {point.payload['text']}")
        """
        if not name:
            raise ValueError("collection name cannot be empty")
        if not query:
            raise ValueError("query vector cannot be empty")
        
        # Формування payload
        payload = {
            "query": query,
            "limit": limit,
            "score_threshold": score_threshold
        }
        
        if filter is not None:
            payload["filter"] = filter
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "POST",
            f"/collections/{name}/points/query",
            json=payload
        )
        
        return SearchResult(**response)
    
    def upsert(
        self,
        name: str,
        *,
        points: List[Dict[str, Any]],
        **kwargs
    ) -> UpsertResult:
        """
        Додає або оновлює точки в колекції.
        
        Args:
            name: Назва колекції
            points: Список точок для додавання/оновлення
                Кожна точка: {"id": str, "vector": List[float], "payload": Dict}
            **kwargs: Додаткові параметри
        
        Returns:
            UpsertResult з результатом операції
        
        Raises:
            ValueError: Якщо параметри невалідні
            NotFoundError: Якщо колекція не існує
        
        Example:
            >>> # Додавання точок
            >>> points = [
            ...     {
            ...         "id": "doc-1",
            ...         "vector": [0.1, 0.2, 0.3, ...],
            ...         "payload": {
            ...             "text": "Document text",
            ...             "category": "tech"
            ...         }
            ...     },
            ...     {
            ...         "id": "doc-2",
            ...         "vector": [0.4, 0.5, 0.6, ...],
            ...         "payload": {
            ...             "text": "Another document",
            ...             "category": "science"
            ...         }
            ...     }
            ... ]
            >>> 
            >>> result = client.collections.upsert(
            ...     name="my_docs",
            ...     points=points
            ... )
            >>> print(f"Operation ID: {result.operation_id}")
        """
        if not name:
            raise ValueError("collection name cannot be empty")
        if not points:
            raise ValueError("points list cannot be empty")
        
        # Формування payload
        payload = {
            "points": points
        }
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "PUT",
            f"/collections/{name}/points",
            json=payload
        )
        
        return UpsertResult(**response)
    
    async def alist(self) -> List[str]:
        """Async версія list()"""
        response = await self._client._make_request("GET", "/collections")
        return response.get("collections", [])
    
    async def aretrieve(self, name: str) -> CollectionInfo:
        """Async версія retrieve()"""
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = await self._client._make_request("GET", f"/collections/{name}")
        return CollectionInfo(**response)
    
    async def acreate(self, name: str, **kwargs) -> Dict[str, Any]:
        """Async версія create()"""
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = await self._client._make_request(
            "PUT",
            f"/collections/{name}",
            json=kwargs if kwargs else None
        )
        return response
    
    async def adelete(self, name: str) -> Dict[str, Any]:
        """Async версія delete()"""
        if not name:
            raise ValueError("collection name cannot be empty")
        
        response = await self._client._make_request("DELETE", f"/collections/{name}")
        return response
    
    async def asearch(
        self,
        name: str,
        *,
        query: List[float],
        limit: int = 10,
        score_threshold: float = 0.0,
        filter: Optional[Dict] = None,
        **kwargs
    ) -> SearchResult:
        """Async версія search()"""
        if not name:
            raise ValueError("collection name cannot be empty")
        if not query:
            raise ValueError("query vector cannot be empty")
        
        payload = {
            "query": query,
            "limit": limit,
            "score_threshold": score_threshold
        }
        
        if filter is not None:
            payload["filter"] = filter
        
        payload.update(kwargs)
        
        response = await self._client._make_request(
            "POST",
            f"/collections/{name}/points/query",
            json=payload
        )
        
        return SearchResult(**response)
    
    async def aupsert(
        self,
        name: str,
        *,
        points: List[Dict[str, Any]],
        **kwargs
    ) -> UpsertResult:
        """Async версія upsert()"""
        if not name:
            raise ValueError("collection name cannot be empty")
        if not points:
            raise ValueError("points list cannot be empty")
        
        payload = {"points": points}
        payload.update(kwargs)
        
        response = await self._client._make_request(
            "PUT",
            f"/collections/{name}/points",
            json=payload
        )
        
        return UpsertResult(**response)


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Collections",
]