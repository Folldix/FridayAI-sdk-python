"""
Chat Resource для FridayAI SDK.

Забезпечує доступ до chat completions API з OpenAI-compatible інтерфейсом.
"""

from typing import Dict, Any, List, Optional, Union, Iterator, AsyncIterator

try:
    from .._client import BaseClient, AsyncClient
    from .models import ChatCompletion, ChatCompletionChunk
    from .._utils import (
        prepare_messages,
        validate_model_name,
        validate_messages,
        convert_friday_to_openai_format,
        stream_chat_completion,
    )
    from .._exceptions import ValidationError
except ImportError:
    from _client import BaseClient, AsyncClient  # type: ignore
    from _models import ChatCompletion, ChatCompletionChunk  # type: ignore
    from _utils import (  # type: ignore
        prepare_messages,
        validate_model_name,
        validate_messages,
        convert_friday_to_openai_format,
        stream_chat_completion,
    )
    from _exceptions import ValidationError  # type: ignore


class Completions:
    """
    Chat completions resource.
    
    Забезпечує методи для створення chat completions з підтримкою:
    - Синхронних та асинхронних запитів
    - Streaming режиму
    - Мультимодального контенту (текст, зображення, файли)
    - OpenAI-compatible API
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> response = client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     model="friday_big"
        ... )
        >>> print(response.choices[0].message.content)
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Completions resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._client = client
    
    def create(
        self,
        *,
        messages: Optional[Union[str, List[Dict], Dict]] = None,
        conversation: Optional[Union[str, List[Dict], Dict]] = None,
        prompt: Optional[str] = None,
        model: str = "friday_big",
        stream: bool = False,
        user: Optional[str] = None,
        info: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        extend_info: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """
        Створює chat completion.
        
        Args:
            messages: Повідомлення у форматі OpenAI:
                - str: простий текст (конвертується у user message)
                - Dict: одне повідомлення
                - List[Dict]: список повідомлень
            model: Модель для використання ("friday_big" або "friday_medium")
            stream: Включити streaming режим (SSE)
            user: Ім'я користувача (опціонально)
            info: Додаткова інформація про користувача (опціонально)
            tools: Список інструментів для function calling (опціонально)
            extend_info: Повернути розширену інформацію (опціонально)
            **kwargs: Додаткові параметри
        
        Returns:
            ChatCompletion якщо stream=False
            Iterator[ChatCompletionChunk] якщо stream=True
        
        Raises:
            ValidationError: Якщо параметри невалідні
            APIError: При помилках API
        
        Example:
            >>> # Базовий запит
            >>> response = client.chat.completions.create(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     model="friday_big"
            ... )
            
            >>> # Streaming
            >>> stream = client.chat.completions.create(
            ...     messages="Tell me a story",
            ...     stream=True
            ... )
            >>> for chunk in stream:
            ...     print(chunk.choices[0].delta.content, end="")
            
            >>> # З зображенням
            >>> response = client.chat.completions.create(
            ...     messages=[{
            ...         "role": "user",
            ...         "content": [
            ...             {"type": "text", "text": "What's in this image?"},
            ...             {"type": "image", "image": {"url": "https://..."}}
            ...         ]
            ...     }]
            ... )
        """
        # Валідація моделі
        if messages is None:
            messages = conversation if conversation is not None else prompt
        if messages is None:
            raise ValidationError("messages, conversation, or prompt is required")

        validate_model_name(model)
        
        # Підготовка messages
        prepared_messages = prepare_messages(messages)
        
        # Валідація messages
        validate_messages(prepared_messages)
        
        # Формування payload для FridayAI API
        payload = {
            "conversation": prepared_messages,  # messages -> conversation
            "model": model,
            "stream": stream
        }
        
        # Додаткові параметри
        if user is not None:
            payload["user"] = user
        if info is not None:
            payload["info"] = info
        if tools is not None:
            payload["tools"] = tools
        if extend_info:
            payload["extend_info"] = extend_info
        
        # Додаємо kwargs
        payload.update(kwargs)
        
        # Виконання запиту
        if stream:
            # Streaming mode
            response = self._client._make_request(
                "POST",
                "/chat/completions",
                json=payload,
                stream=True
            )
            return self._stream_response(response, model)
        else:
            # Normal mode
            response = self._client._make_request(
                "POST",
                "/chat/completions",
                json=payload
            )
            return self._parse_response(response, model)
    
    async def acreate(
        self,
        *,
        messages: Optional[Union[str, List[Dict], Dict]] = None,
        conversation: Optional[Union[str, List[Dict], Dict]] = None,
        prompt: Optional[str] = None,
        model: str = "friday_big",
        stream: bool = False,
        user: Optional[str] = None,
        info: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        extend_info: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """
        Асинхронна версія create().
        
        Створює chat completion асинхронно.
        
        Args:
            Ті самі що у create()
        
        Returns:
            ChatCompletion або AsyncIterator[ChatCompletionChunk]
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def main():
            ...     response = await client.chat.completions.acreate(
            ...         messages=[{"role": "user", "content": "Hello"}]
            ...     )
            ...     print(response.choices[0].message.content)
            >>> 
            >>> asyncio.run(main())
        """
        # Валідація
        if messages is None:
            messages = conversation if conversation is not None else prompt
        if messages is None:
            raise ValidationError("messages, conversation, or prompt is required")

        validate_model_name(model)
        prepared_messages = prepare_messages(messages)
        validate_messages(prepared_messages)
        
        # Payload
        payload = {
            "conversation": prepared_messages,
            "model": model,
            "stream": stream
        }
        
        if user is not None:
            payload["user"] = user
        if info is not None:
            payload["info"] = info
        if tools is not None:
            payload["tools"] = tools
        if extend_info:
            payload["extend_info"] = extend_info
        
        payload.update(kwargs)
        
        # Async request
        if stream:
            response = await self._client._make_request(
                "POST",
                "/chat/completions",
                json=payload,
                stream=True
            )
            return self._astream_response(response, model)
        else:
            response = await self._client._make_request(
                "POST",
                "/chat/completions",
                json=payload
            )
            return self._parse_response(response, model)
    
    def _parse_response(
        self,
        response: Dict[str, Any],
        model: str
    ) -> ChatCompletion:
        """
        Парсить відповідь від API у ChatCompletion.
        
        Args:
            response: Dict відповідь від FridayAI API
            model: Назва моделі
        
        Returns:
            ChatCompletion об'єкт
        """
        # FridayAI повертає: {"response": "text"}
        # Конвертуємо у OpenAI формат
        openai_dict = convert_friday_to_openai_format(response, model)
        
        # Створюємо Pydantic model
        return ChatCompletion(**openai_dict)
    
    def _stream_response(
        self,
        response,
        model: str
    ) -> Iterator[ChatCompletionChunk]:
        """
        Обробляє streaming відповідь.
        
        Args:
            response: Streaming HTTP response
            model: Назва моделі
        
        Yields:
            ChatCompletionChunk об'єкти
        """
        for chunk_data in stream_chat_completion(response):
            yield ChatCompletionChunk(**chunk_data)
    
    async def _astream_response(
        self,
        response,
        model: str
    ) -> AsyncIterator[ChatCompletionChunk]:
        """
        Асинхронна версія _stream_response.
        
        Args:
            response: Async streaming response
            model: Назва моделі
        
        Yields:
            ChatCompletionChunk об'єкти
        """
        # Async version
        async for chunk_data in self._astream_chat_completion(response):
            yield ChatCompletionChunk(**chunk_data)
    
    async def _astream_chat_completion(self, response) -> AsyncIterator[Dict]:
        """Async версія stream_chat_completion"""
        try:
            from .._utils import parse_sse_event
        except ImportError:
            from _utils import parse_sse_event  # type: ignore
        
        async for line in response.aiter_lines():
            data = parse_sse_event(line)
            if data is None:
                break
            yield data


class Chat:
    """
    Chat resource.
    
    Головний namespace для chat-related операцій.
    
    Attributes:
        completions: Completions resource для створення chat completions
    
    Example:
        >>> from friday import Friday
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> # Доступ до completions
        >>> response = client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
    """
    
    def __init__(self, client: Union[BaseClient, AsyncClient]) -> None:
        """
        Ініціалізує Chat resource.
        
        Args:
            client: BaseClient або AsyncClient instance
        """
        self._completions = Completions(client)
        self._client = client
    
    @property
    def completions(self) -> Completions:
        """
        Повертає Completions resource.
        
        Returns:
            Completions instance
        """
        return self._completions

    def message(
        self,
        *,
        messages: Optional[Union[str, List[Dict], Dict]] = None,
        conversation: Optional[Union[str, List[Dict], Dict]] = None,
        prompt: Optional[str] = None,
        model: str = "friday_medium",
        user: Optional[str] = None,
        info: Optional[str] = None,
        extend_info: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        payload = self._build_payload(
            messages=messages,
            conversation=conversation,
            prompt=prompt,
            model=model,
            user=user,
            info=info,
            extend_info=extend_info,
            **kwargs
        )
        return self._client._make_request("POST", "/message", json=payload)

    def bot(
        self,
        *,
        messages: Optional[Union[str, List[Dict], Dict]] = None,
        conversation: Optional[Union[str, List[Dict], Dict]] = None,
        prompt: Optional[str] = None,
        model: str = "friday_big",
        clients: Optional[List[Dict]] = None,
        user: Optional[str] = None,
        info: Optional[str] = None,
        extend_info: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        payload = self._build_payload(
            messages=messages,
            conversation=conversation,
            prompt=prompt,
            model=model,
            user=user,
            info=info,
            extend_info=extend_info,
            **kwargs
        )
        if clients is not None:
            payload["clients"] = clients
        return self._client._make_request("POST", "/bot", json=payload)

    async def amessage(self, **kwargs) -> Dict[str, Any]:
        payload = self._build_payload(**kwargs)
        return await self._client._make_request("POST", "/message", json=payload)

    async def abot(self, **kwargs) -> Dict[str, Any]:
        clients = kwargs.pop("clients", None)
        payload = self._build_payload(**kwargs)
        if clients is not None:
            payload["clients"] = clients
        return await self._client._make_request("POST", "/bot", json=payload)

    def _build_payload(
        self,
        *,
        messages: Optional[Union[str, List[Dict], Dict]] = None,
        conversation: Optional[Union[str, List[Dict], Dict]] = None,
        prompt: Optional[str] = None,
        model: str = "friday_medium",
        user: Optional[str] = None,
        info: Optional[str] = None,
        extend_info: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        if messages is None:
            messages = conversation if conversation is not None else prompt
        if messages is None:
            raise ValidationError("messages, conversation, or prompt is required")

        validate_model_name(model)
        prepared_messages = prepare_messages(messages)
        validate_messages(prepared_messages)

        payload: Dict[str, Any] = {
            "conversation": prepared_messages,
            "model": model,
        }
        if user is not None:
            payload["user"] = user
        if info is not None:
            payload["info"] = info
        if extend_info:
            payload["extend_info"] = extend_info
        payload.update(kwargs)
        return payload


# ============================================================================
# Публічний API модуля
# ============================================================================

__all__ = [
    "Chat",
    "Completions",
]
