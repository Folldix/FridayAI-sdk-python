"""
Images Resource для FridayAI SDK.

Забезпечує доступ до image generation та editing API.
"""

from typing import Optional, Union

try:
    from .._client import BaseClient, AsyncClient
    from .models import ImageResponse
except ImportError:
    from _client import BaseClient, AsyncClient  # type: ignore
    from _models import ImageResponse  # type: ignore


class Images:
    """
    Images resource для генерації та редагування зображень.
    
    Забезпечує методи для:
    - Генерації зображень з текстового опису
    - Редагування існуючих зображень
    - Синхронні та асинхронні запити
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Генерація зображення
        >>> image = client.images.generate(
        ...     prompt="A sunset over the ocean",
        ...     size="1024x1024"
        ... )
        >>> print(image.image_url)
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Images resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
    
    def generate(
        self,
        *,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageResponse:
        """
        Генерує зображення з текстового опису.
        
        Args:
            prompt: Текстовий опис зображення для генерації
            size: Розмір зображення (наприклад "1024x1024", "512x512")
            **kwargs: Додаткові параметри
        
        Returns:
            ImageResponse з URL згенерованого зображення
        
        Raises:
            ValueError: Якщо prompt порожній
            APIError: При помилках API
        
        Example:
            >>> # Базова генерація
            >>> image = client.images.generate(
            ...     prompt="A beautiful sunset over mountains"
            ... )
            >>> print(image.image_url)
            
            >>> # З кастомним розміром
            >>> image = client.images.generate(
            ...     prompt="A cat sitting on a table",
            ...     size="512x512"
            ... )
            
            >>> # Детальний опис
            >>> image = client.images.generate(
            ...     prompt="A futuristic city at night with neon lights, "
            ...            "cyberpunk style, highly detailed, 4k quality"
            ... )
        """
        # Валідація
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        
        # Формування payload для FridayAI API
        payload = {
            "payload": prompt,  # prompt -> payload (FridayAI маппінг)
            "size": size
        }
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "POST",
            "/generate-image",
            json=payload
        )
        
        # Парсинг відповіді
        return ImageResponse(**response)
    
    def edit(
        self,
        *,
        image_url: str,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageResponse:
        """
        Редагує існуюче зображення згідно з описом змін.
        
        Args:
            image_url: URL існуючого зображення для редагування
            prompt: Опис змін які потрібно внести
            size: Розмір результуючого зображення
            **kwargs: Додаткові параметри
        
        Returns:
            ImageResponse з URL відредагованого зображення
        
        Raises:
            ValueError: Якщо image_url або prompt порожні
            APIError: При помилках API
        
        Example:
            >>> # Редагування зображення
            >>> image = client.images.edit(
            ...     image_url="https://example.com/original.jpg",
            ...     prompt="Add a rainbow to the sky"
            ... )
            >>> print(image.image_url)
            
            >>> # Зміна стилю
            >>> image = client.images.edit(
            ...     image_url="https://example.com/photo.jpg",
            ...     prompt="Convert to oil painting style",
            ...     size="1024x1024"
            ... )
            
            >>> # Додавання об'єктів
            >>> image = client.images.edit(
            ...     image_url="https://example.com/landscape.jpg",
            ...     prompt="Add birds flying in the sky"
            ... )
        """
        # Валідація
        if not image_url:
            raise ValueError("image_url is required")
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        
        # Формування payload
        payload = {
            "image_url": image_url,
            "payload": prompt,  # prompt -> payload
            "size": size
        }
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "POST",
            "/modify-image",
            json=payload
        )
        
        # Парсинг відповіді
        return ImageResponse(**response)
    
    async def agenerate(
        self,
        *,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageResponse:
        """
        Асинхронна версія generate().
        
        Генерує зображення асинхронно.
        
        Args:
            Ті самі що у generate()
        
        Returns:
            ImageResponse з URL зображення
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def main():
            ...     image = await client.images.agenerate(
            ...         prompt="A beautiful landscape"
            ...     )
            ...     print(image.image_url)
            >>> 
            >>> asyncio.run(main())
        """
        # Валідація
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        
        # Payload
        payload = {
            "payload": prompt,
            "size": size
        }
        payload.update(kwargs)
        
        # Async запит
        response = await self._client._make_request(
            "POST",
            "/generate-image",
            json=payload
        )
        
        return ImageResponse(**response)
    
    async def aedit(
        self,
        *,
        image_url: str,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageResponse:
        """
        Асинхронна версія edit().
        
        Редагує зображення асинхронно.
        
        Args:
            Ті самі що у edit()
        
        Returns:
            ImageResponse з URL відредагованого зображення
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def main():
            ...     image = await client.images.aedit(
            ...         image_url="https://example.com/original.jpg",
            ...         prompt="Make it brighter"
            ...     )
            ...     print(image.image_url)
            >>> 
            >>> asyncio.run(main())
        """
        # Валідація
        if not image_url:
            raise ValueError("image_url is required")
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        
        # Payload
        payload = {
            "image_url": image_url,
            "payload": prompt,
            "size": size
        }
        payload.update(kwargs)
        
        # Async запит
        response = await self._client._make_request(
            "POST",
            "/modify-image",
            json=payload
        )
        
        return ImageResponse(**response)


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Images",
]