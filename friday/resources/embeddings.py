"""
Embeddings Resource для FridayAI SDK.

Забезпечує доступ до embeddings API для генерації векторних представлень тексту.
"""

from typing import Union, List

try:
    from .._client import BaseClient, AsyncClient
    from .models import EmbeddingResponse, Embedding
except ImportError:
    from _client import BaseClient, AsyncClient  # type: ignore
    from _models import EmbeddingResponse, Embedding  # type: ignore


class Embeddings:
    """
    Embeddings resource для генерації векторних представлень тексту.
    
    Забезпечує методи для:
    - Генерації embeddings для тексту
    - Batch processing множинних текстів
    - Синхронні та асинхронні запити
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Генерація embedding
        >>> embedding = client.embeddings.create(
        ...     input="Hello, world!",
        ...     model="embedding-model"
        ... )
        >>> print(len(embedding.data[0].embedding))
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Embeddings resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
    
    def create(
        self,
        *,
        input: Union[str, List[str]],
        model: str = "embedding-model",
        **kwargs
    ) -> EmbeddingResponse:
        """
        Створює embeddings для тексту або списку текстів.
        
        Args:
            input: Текст або список текстів для embedding
            model: Назва моделі embeddings
            **kwargs: Додаткові параметри
        
        Returns:
            EmbeddingResponse з векторними представленнями
        
        Raises:
            ValueError: Якщо input порожній
            APIError: При помилках API
        
        Example:
            >>> # Один текст
            >>> embedding = client.embeddings.create(
            ...     input="Hello, world!"
            ... )
            >>> vector = embedding.data[0].embedding
            >>> print(len(vector))  # Розмірність вектора
            
            >>> # Множинні тексти
            >>> embeddings = client.embeddings.create(
            ...     input=[
            ...         "First text",
            ...         "Second text",
            ...         "Third text"
            ...     ]
            ... )
            >>> for emb in embeddings.data:
            ...     print(f"Index {emb.index}: {len(emb.embedding)} dims")
            
            >>> # Для пошуку
            >>> doc_embeddings = client.embeddings.create(
            ...     input=["Doc 1", "Doc 2", "Doc 3"]
            ... )
            >>> query_embedding = client.embeddings.create(
            ...     input="Search query"
            ... )
        """
        # Валідація
        if not input:
            raise ValueError("input cannot be empty")
        
        # Нормалізація input до списку
        if isinstance(input, str):
            input_list = [input]
            single_input = True
        else:
            input_list = input
            single_input = False
            
            # Валідація що список не порожній
            if len(input_list) == 0:
                raise ValueError("input list cannot be empty")
        
        # Формування payload
        payload = {
            "input": input if not single_input else input_list[0],
            "model": model
        }
        
        # Додаткові параметри
        payload.update(kwargs)
        
        # API запит
        response = self._client._make_request(
            "POST",
            "/embeddings",
            json=payload
        )
        
        # Парсинг відповіді
        return self._parse_response(response, input_list, model)
    
    async def acreate(
        self,
        *,
        input: Union[str, List[str]],
        model: str = "embedding-model",
        **kwargs
    ) -> EmbeddingResponse:
        """
        Асинхронна версія create().
        
        Створює embeddings асинхронно.
        
        Args:
            Ті самі що у create()
        
        Returns:
            EmbeddingResponse з векторами
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def main():
            ...     embedding = await client.embeddings.acreate(
            ...         input="Hello from async!"
            ...     )
            ...     print(embedding.data[0].embedding[:5])
            >>> 
            >>> asyncio.run(main())
        """
        # Валідація
        if not input:
            raise ValueError("input cannot be empty")
        
        # Нормалізація
        if isinstance(input, str):
            input_list = [input]
            single_input = True
        else:
            input_list = input
            single_input = False
            
            if len(input_list) == 0:
                raise ValueError("input list cannot be empty")
        
        # Payload
        payload = {
            "input": input if not single_input else input_list[0],
            "model": model
        }
        payload.update(kwargs)
        
        # Async запит
        response = await self._client._make_request(
            "POST",
            "/embeddings",
            json=payload
        )
        
        return self._parse_response(response, input_list, model)
    
    def _parse_response(
        self,
        response: dict,
        input_texts: List[str],
        model: str
    ) -> EmbeddingResponse:
        """
        Парсить відповідь API у EmbeddingResponse.
        
        Підтримує різні формати відповідей:
        - OpenAI-compatible (з полем "data")
        - FridayAI формат (потребує конвертації)
        
        Args:
            response: Dict відповідь від API
            input_texts: Список вхідних текстів
            model: Назва моделі
        
        Returns:
            EmbeddingResponse об'єкт
        """
        # Якщо response вже в OpenAI форматі
        if "data" in response and "object" in response:
            return EmbeddingResponse(**response)
        
        # Інакше конвертуємо у OpenAI формат
        # FridayAI може повертати просто масив embeddings
        # або dict з embedding полем
        
        embeddings_data = []
        
        # Перевіряємо різні формати
        if "embedding" in response:
            # Один embedding
            embeddings_data.append(
                Embedding(
                    object="embedding",
                    embedding=response["embedding"],
                    index=0
                )
            )
        elif "embeddings" in response:
            # Множинні embeddings
            for i, emb in enumerate(response["embeddings"]):
                embeddings_data.append(
                    Embedding(
                        object="embedding",
                        embedding=emb,
                        index=i
                    )
                )
        else:
            # Fallback - припускаємо що response є список
            if isinstance(response, list):
                for i, emb in enumerate(response):
                    embeddings_data.append(
                        Embedding(
                            object="embedding",
                            embedding=emb,
                            index=i
                        )
                    )
        
        # Створюємо OpenAI-compatible response
        return EmbeddingResponse(
            object="list",
            data=embeddings_data,
            model=model,
            usage=None
        )


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Embeddings",
]