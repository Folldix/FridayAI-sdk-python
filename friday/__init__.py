"""
FridayAI Python SDK

Official Python client library for FridayAI API.
Provides OpenAI-compatible interface for easy integration.

Example:
    >>> from friday import Friday
    >>> 
    >>> client = Friday(api_key="sk-...")
    >>> 
    >>> # Chat
    >>> response = client.chat.completions.create(
    ...     messages=[{"role": "user", "content": "Hello"}]
    ... )
    >>> 
    >>> # Images
    >>> image = client.images.generate(prompt="A sunset")
    >>> 
    >>> # Audio
    >>> audio = client.audio.speech.create(input="Hello")
"""

# Core
from ._client import BaseClient, AsyncClient
from ._exceptions import (
    FridayError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    RateLimitError,
    InternalServerError,
    ServiceUnavailableError,
    APIConnectionError,
    APITimeoutError,
    ValidationError,
    BadRequestError,
)

# Models
from .resources.models import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage as ChatMessage,
    Choice as ChatChoice,
    ImageResponse,
    AudioResponse,
    EmbeddingResponse,
    Embedding,
    CollectionInfo,
    SearchResult,
    UpsertResult,
    UsageStatus,
    ChatLog,
    ChatLogsResponse,
    UserInfo,
)

# Resources
from .resources.chat import Chat
from .resources.images import Images
from .resources.audio import Audio
from .resources.embeddings import Embeddings
from .resources.collections import Collections
from .resources.usage import Usage

# Version
try:
    from ._version import __version__
except Exception:
    __version__ = "0.1.0"


class Friday:
    """
    FridayAI API Client
    
    Main client class for interacting with FridayAI API.
    Provides OpenAI-compatible interface for all API resources.
    
    Attributes:
        chat: Chat resource for completions
        images: Images resource for generation/editing
        audio: Audio resource for text-to-speech
        embeddings: Embeddings resource for vector generation
        collections: Collections resource for vector database
        usage: Usage resource for tracking and limits
    
    Example:
        >>> # Basic usage
        >>> client = Friday(api_key="sk-...")
        >>> 
        >>> response = client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     model="friday_big"
        ... )
        >>> print(response.choices[0].message.content)
        
        >>> # Context manager
        >>> with Friday(api_key="sk-...") as client:
        ...     response = client.chat.completions.create(...)
        
        >>> # Custom configuration
        >>> client = Friday(
        ...     api_key="sk-...",
        ...     base_url="https://custom.api.com",
        ...     timeout=60.0,
        ...     max_retries=5
        ... )
    """
    
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.fridayai.online/api",
        timeout: float = 300.0,
        max_retries: int = 2,
        **kwargs
    ):
        """
        Initialize FridayAI client.
        
        Args:
            api_key: Your FridayAI API key (required)
            base_url: Base URL for API (default: https://www.fridayai.online/api)
            timeout: Request timeout in seconds (default: 300.0)
            max_retries: Maximum number of retry attempts (default: 2)
            **kwargs: Additional configuration options
        
        Raises:
            ValueError: If api_key is not provided
        
        Example:
            >>> client = Friday(api_key="sk-...")
            >>> 
            >>> # With custom settings
            >>> client = Friday(
            ...     api_key="sk-...",
            ...     timeout=60.0,
            ...     max_retries=5
            ... )
        """
        if not api_key:
            raise ValueError("api_key is required")
        
        # Initialize HTTP client
        self._client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        
        # Initialize all resources
        self.chat = Chat(self._client)
        self.images = Images(self._client)
        self.audio = Audio(self._client)
        self.embeddings = Embeddings(self._client)
        self.collections = Collections(self._client)
        self.usage = Usage(self._client)
    
    def __enter__(self):
        """
        Enter context manager.
        
        Example:
            >>> with Friday(api_key="sk-...") as client:
            ...     response = client.chat.completions.create(...)
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close connections."""
        self.close()
    
    def close(self):
        """
        Close HTTP connections.
        
        Call this when you're done using the client to clean up resources.
        Automatically called when using context manager.
        
        Example:
            >>> client = Friday(api_key="sk-...")
            >>> # ... use client ...
            >>> client.close()
        """
        self._client.close()

    def health(self):
        """Return the API health status."""
        return self._client._make_request("GET", "/health")
    
    def __repr__(self):
        """String representation of the client."""
        return f"Friday(base_url='{self._client.base_url}')"


class AsyncFriday:
    """
    Async FridayAI API Client
    
    Asynchronous version of the main client.
    All methods return coroutines that must be awaited.
    
    Example:
        >>> import asyncio
        >>> 
        >>> async def main():
        ...     async with AsyncFriday(api_key="sk-...") as client:
        ...         response = await client.chat.completions.acreate(
        ...             messages=[{"role": "user", "content": "Hello"}]
        ...         )
        ...         print(response.choices[0].message.content)
        >>> 
        >>> asyncio.run(main())
    """
    
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.fridayai.online/api",
        timeout: float = 300.0,
        max_retries: int = 2,
        **kwargs
    ):
        """
        Initialize async FridayAI client.
        
        Args:
            api_key: Your FridayAI API key (required)
            base_url: Base URL for API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            **kwargs: Additional configuration options
        """
        if not api_key:
            raise ValueError("api_key is required")
        
        # Initialize async HTTP client
        self._client = AsyncClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs
        )
        
        # Initialize all resources
        self.chat = Chat(self._client)
        self.images = Images(self._client)
        self.audio = Audio(self._client)
        self.embeddings = Embeddings(self._client)
        self.collections = Collections(self._client)
        self.usage = Usage(self._client)
    
    async def __aenter__(self):
        """Enter async context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and close connections."""
        await self.close()
    
    async def close(self):
        """Close async HTTP connections."""
        await self._client.aclose()

    async def health(self):
        """Return the API health status."""
        return await self._client._make_request("GET", "/health")
    
    def __repr__(self):
        """String representation of the async client."""
        return f"AsyncFriday(base_url='{self._client.base_url}')"


# Public API
__all__ = [
    # Main clients
    "Friday",
    "AsyncFriday",
    
    # Exceptions
    "FridayError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    "APIConnectionError",
    "APITimeoutError",
    "ValidationError",
    "BadRequestError",
    
    # Models
    "ChatCompletion",
    "ChatCompletionChunk",
    "ChatMessage",
    "ChatChoice",
    "ImageResponse",
    "AudioResponse",
    "EmbeddingResponse",
    "Embedding",
    "CollectionInfo",
    "SearchResult",
    "UpsertResult",
    "UsageStatus",
    "ChatLog",
    "ChatLogsResponse",
    "UserInfo",
    
    # Version
    "__version__",
]
