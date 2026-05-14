"""
Audio Resource для FridayAI SDK.

Забезпечує доступ до Text-to-Speech (TTS) API.
"""

from typing import Optional, Union

try:
    from .._client import BaseClient, AsyncClient
    from .models import AudioResponse
except ImportError:
    from _client import BaseClient, AsyncClient  # type: ignore
    from _models import AudioResponse  # type: ignore


class Speech:
    """
    Speech resource для Text-to-Speech генерації.
    
    Забезпечує методи для:
    - Генерації аудіо з тексту
    - Підтримки різних емоцій голосу
    - Синхронні та асинхронні запити
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Генерація аудіо
        >>> audio = client.audio.speech.create(
        ...     input="Hello, how are you today?"
        ... )
        >>> print(audio.audio_url)
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Speech resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
    
    def create(
        self,
        *,
        input: str,
        emotion: str = "neutral",
        **kwargs
    ) -> AudioResponse:
        """
        Генерує аудіо з тексту (Text-to-Speech).
        
        Args:
            input: Текст для озвучення
            emotion: Емоція голосу (за замовчуванням "neutral")
                Можливі значення: "neutral", "happy", "sad", etc.
            **kwargs: Додаткові параметри
        
        Returns:
            AudioResponse з URL згенерованого аудіо файлу
        
        Raises:
            ValueError: Якщо input порожній
            APIError: При помилках API
        
        Example:
            >>> # Базова генерація
            >>> audio = client.audio.speech.create(
            ...     input="Hello, world!"
            ... )
            >>> print(audio.audio_url)
            
            >>> # З емоцією
            >>> audio = client.audio.speech.create(
            ...     input="I'm so happy to see you!",
            ...     emotion="happy"
            ... )
            
            >>> # Збереження аудіо
            >>> import requests
            >>> response = requests.get(audio.audio_url)
            >>> with open("speech.mp3", "wb") as f:
            ...     f.write(response.content)
        """
        # Валідація
        if not input or not input.strip():
            raise ValueError("input cannot be empty")
        
        # Формування payload для FridayAI API
        payload = {
            "payload": input,  # input -> payload (FridayAI маппінг)
            "emotion": emotion
        }
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "POST",
            "/generate-voice",
            json=payload
        )
        
        # Парсинг відповіді
        return AudioResponse(**response)
    
    async def acreate(
        self,
        *,
        input: str,
        emotion: str = "neutral",
        **kwargs
    ) -> AudioResponse:
        """
        Асинхронна версія create().
        
        Генерує аудіо асинхронно.
        
        Args:
            Ті самі що у create()
        
        Returns:
            AudioResponse з URL аудіо файлу
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def main():
            ...     audio = await client.audio.speech.acreate(
            ...         input="Hello from async!"
            ...     )
            ...     print(audio.audio_url)
            >>> 
            >>> asyncio.run(main())
        """
        # Валідація
        if not input or not input.strip():
            raise ValueError("input cannot be empty")
        
        # Payload
        payload = {
            "payload": input,
            "emotion": emotion
        }
        payload.update(kwargs)
        
        # Async запит
        response = await self._client._make_request(
            "POST",
            "/generate-voice",
            json=payload
        )
        
        return AudioResponse(**response)


class Audio:
    """
    Audio resource.
    
    Головний namespace для audio-related операцій.
    
    Attributes:
        speech: Speech resource для TTS генерації
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Доступ до speech
        >>> audio = client.audio.speech.create(
        ...     input="Hello, world!"
        ... )
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Audio resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._speech = Speech(client)
    
    @property
    def speech(self) -> Speech:
        """
        Повертає Speech resource.
        
        Returns:
            Speech instance
        """
        return self._speech


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Audio",
    "Speech",
]