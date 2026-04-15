"""
Usage Resource для FridayAI SDK.

Забезпечує доступ до tracking API для моніторингу використання та лімітів.
"""

from typing import Optional, Dict, Any, Union
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _client import BaseClient, AsyncClient
from _models import UsageStatus, ChatLog, ChatLogsResponse, UserInfo, OkResponse


class Logs:
    """
    Logs resource для роботи з логами чатів.
    
    Example:
        >>> # Список логів
        >>> logs = client.usage.logs.list(date="2024-01-15")
        >>> 
        >>> # Конкретний лог
        >>> log = client.usage.logs.retrieve(id="abc123")
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """Ініціалізує Logs resource."""
        self._client = client
    
    def list(
        self,
        *,
        date: Optional[str] = None,
        model: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> ChatLogsResponse:
        """
        Повертає список логів чату.
        
        Args:
            date: Дата у форматі YYYY-MM-DD (опціонально)
            model: Фільтр за моделлю (опціонально)
            limit: Кількість записів (за замовчуванням 50)
            **kwargs: Додаткові параметри
        
        Returns:
            ChatLogsResponse зі списком логів
        
        Example:
            >>> # Всі логи
            >>> logs = client.usage.logs.list()
            >>> 
            >>> # За датою
            >>> logs = client.usage.logs.list(date="2024-01-15")
            >>> 
            >>> # За моделлю
            >>> logs = client.usage.logs.list(model="friday_big")
        """
        params = {"limit": limit}
        
        if date is not None:
            params["date"] = date
        if model is not None:
            params["model"] = model
        
        params.update(kwargs)
        
        response = self._client._make_request(
            "GET",
            "/usage/chat-logs",
            params=params
        )
        
        return ChatLogsResponse(**response)
    
    def retrieve(self, id: str) -> ChatLog:
        """
        Повертає конкретний лог за ID.
        
        Args:
            id: ID логу
        
        Returns:
            ChatLog об'єкт
        
        Raises:
            ValueError: Якщо id порожній
            NotFoundError: Якщо лог не знайдено
        
        Example:
            >>> log = client.usage.logs.retrieve(id="abc123")
            >>> print(log.conversation)
            >>> print(log.response)
        """
        if not id:
            raise ValueError("log id cannot be empty")
        
        response = self._client._make_request(
            "GET",
            "/usage/chat-log",
            params={"id": id}
        )
        
        return ChatLog(**response)
    
    async def alist(
        self,
        *,
        date: Optional[str] = None,
        model: Optional[str] = None,
        limit: int = 50,
        **kwargs
    ) -> ChatLogsResponse:
        """Async версія list()"""
        params = {"limit": limit}
        
        if date is not None:
            params["date"] = date
        if model is not None:
            params["model"] = model
        
        params.update(kwargs)
        
        response = await self._client._make_request(
            "GET",
            "/usage/chat-logs",
            params=params
        )
        
        return ChatLogsResponse(**response)
    
    async def aretrieve(self, id: str) -> ChatLog:
        """Async версія retrieve()"""
        if not id:
            raise ValueError("log id cannot be empty")
        
        response = await self._client._make_request(
            "GET",
            "/usage/chat-log",
            params={"id": id}
        )
        
        return ChatLog(**response)


class Users:
    """
    Users resource для управління інформацією користувача.
    
    Example:
        >>> # Отримання інформації
        >>> info = client.usage.users.retrieve()
        >>> 
        >>> # Оновлення
        >>> client.usage.users.update(info="Name: John")
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """Ініціалізує Users resource."""
        self._client = client
    
    def retrieve(self) -> UserInfo:
        """
        Повертає персональну інформацію користувача.
        
        Returns:
            UserInfo об'єкт
        
        Example:
            >>> info = client.usage.users.retrieve()
            >>> print(info.info)
        """
        response = self._client._make_request(
            "GET",
            "/usage/user-info"
        )
        
        return UserInfo(**response)
    
    def update(self, *, info: str, **kwargs) -> Dict[str, Any]:
        """
        Оновлює персональну інформацію користувача.
        
        Args:
            info: Персональна інформація
            **kwargs: Додаткові параметри
        
        Returns:
            Dict з результатом
        
        Raises:
            ValueError: Якщо info порожній
        
        Example:
            >>> result = client.usage.users.update(
            ...     info="Name: John, Preferences: tech news"
            ... )
        """
        if not info or not info.strip():
            raise ValueError("info cannot be empty")
        
        payload = {"info": info}
        payload.update(kwargs)
        
        response = self._client._make_request(
            "POST",
            "/usage/user-info",
            json=payload
        )
        
        return response
    
    def delete(self) -> Dict[str, Any]:
        """
        Видаляє персональну інформацію користувача.
        
        Returns:
            Dict з результатом
        
        Example:
            >>> result = client.usage.users.delete()
            >>> print(result)  # {"ok": True}
        """
        response = self._client._make_request(
            "DELETE",
            "/usage/user-info"
        )
        
        return response
    
    async def aretrieve(self) -> UserInfo:
        """Async версія retrieve()"""
        response = await self._client._make_request("GET", "/usage/user-info")
        return UserInfo(**response)
    
    async def aupdate(self, *, info: str, **kwargs) -> Dict[str, Any]:
        """Async версія update()"""
        if not info or not info.strip():
            raise ValueError("info cannot be empty")
        
        payload = {"info": info}
        payload.update(kwargs)
        
        response = await self._client._make_request(
            "POST",
            "/usage/user-info",
            json=payload
        )
        
        return response
    
    async def adelete(self) -> Dict[str, Any]:
        """Async версія delete()"""
        response = await self._client._make_request("DELETE", "/usage/user-info")
        return response


class Usage:
    """
    Usage resource для моніторингу використання та лімітів.
    
    Attributes:
        logs: Logs resource для роботи з логами
        users: Users resource для управління профілем
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Статус використання
        >>> status = client.usage.retrieve()
        >>> print(f"Chat: {status.usage.chat}/{status.limits.chat}")
        >>> 
        >>> # Логи
        >>> logs = client.usage.logs.list()
        >>> 
        >>> # Профіль
        >>> info = client.usage.users.retrieve()
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Usage resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
        self._logs = Logs(client)
        self._users = Users(client)
    
    @property
    def logs(self) -> Logs:
        """Повертає Logs resource."""
        return self._logs
    
    @property
    def users(self) -> Users:
        """Повертає Users resource."""
        return self._users
    
    def retrieve(self) -> UsageStatus:
        """
        Повертає статус використання та ліміти.
        
        Returns:
            UsageStatus з інформацією про ліміти та використання
        
        Example:
            >>> status = client.usage.retrieve()
            >>> 
            >>> print(f"Chat limit: {status.limits.chat}")
            >>> print(f"Chat used: {status.usage.chat}")
            >>> print(f"Chat remaining: {status.remaining.chat}")
            >>> 
            >>> if status.remaining.chat < 10:
            ...     print("Warning: Low quota!")
        """
        response = self._client._make_request(
            "GET",
            "/usage/status"
        )
        
        return UsageStatus(**response)
    
    async def aretrieve(self) -> UsageStatus:
        """Async версія retrieve()"""
        response = await self._client._make_request("GET", "/usage/status")
        return UsageStatus(**response)


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Usage",
    "Logs",
    "Users",
]