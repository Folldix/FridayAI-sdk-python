"""
Приклад повного використання FridayAI SDK
"""

print("=" * 60)
print(" FridayAI SDK - Повний приклад використання")
print("=" * 60 + "\n")

print("Приклад 1: Базова ініціалізація")
print("-" * 60)
print("""
from friday import Friday

# Створення клієнта
client = Friday(api_key="sk-your-api-key-here")

# Тепер можна використовувати всі ресурси
print(client.chat)       # Chat resource
print(client.images)     # Images resource
print(client.audio)      # Audio resource
print(client.embeddings) # Embeddings resource
print(client.collections)# Collections resource
print(client.usage)      # Usage resource
""")
print()

print("Приклад 2: Chat Completions")
print("-" * 60)
print("""
# Простий чат
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello, Friday!"}
    ],
    model="friday_big"
)

print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")
""")
print()

print("Приклад 3: Images")
print("-" * 60)
print("""
# Генерація зображення
image = client.images.generate(
    prompt="A beautiful sunset over the ocean"
)

print(f"Image URL: {image.image_url}")

# Редагування
edited = client.images.edit(
    image_url="https://example.com/image.jpg",
    prompt="Add a rainbow"
)
""")
print()

print("Приклад 4: Audio (TTS)")
print("-" * 60)
print("""
# Генерація голосу
audio = client.audio.speech.create(
    input="Hello, how are you today?",
    emotion="happy"
)

print(f"Audio URL: {audio.audio_url}")

# Збереження
import requests
response = requests.get(audio.audio_url)
with open("speech.mp3", "wb") as f:
    f.write(response.content)
""")
print()

print("Приклад 5: Embeddings")
print("-" * 60)
print("""
# Генерація embeddings
embedding = client.embeddings.create(
    input="Python programming language"
)

vector = embedding.data[0].embedding
print(f"Vector dimensions: {len(vector)}")

# Batch
embeddings = client.embeddings.create(
    input=["Text 1", "Text 2", "Text 3"]
)
""")
print()

print("Приклад 6: Collections (Vector DB)")
print("-" * 60)
print("""
# Створення колекції
client.collections.create("my_docs")

# Додавання векторів
points = [
    {
        "id": "doc-1",
        "vector": embedding.data[0].embedding,
        "payload": {"text": "Document 1"}
    }
]

client.collections.upsert(name="my_docs", points=points)

# Пошук
results = client.collections.search(
    name="my_docs",
    query=embedding.data[0].embedding,
    limit=5
)
""")
print()

print("Приклад 7: Usage & Monitoring")
print("-" * 60)
print("""
# Перевірка лімітів
status = client.usage.retrieve()

print(f"Chat: {status.usage.chat}/{status.limits.chat}")
print(f"Remaining: {status.remaining.chat}")

# Логи
logs = client.usage.logs.list(limit=10)

# Профіль
info = client.usage.users.retrieve()
""")
print()

print("Приклад 8: Context Manager")
print("-" * 60)
print("""
# Автоматичне закриття з'єднань
with Friday(api_key="sk-...") as client:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response.choices[0].message.content)
# Автоматично викликається client.close()
""")
print()

print("Приклад 9: Async використання")
print("-" * 60)
print("""
import asyncio
from friday import AsyncFriday

async def main():
    async with AsyncFriday(api_key="sk-...") as client:
        # Всі методи async
        response = await client.chat.completions.acreate(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        image = await client.images.agenerate(
            prompt="A sunset"
        )
        
        embedding = await client.embeddings.acreate(
            input="Text"
        )
        
        print(response.choices[0].message.content)

asyncio.run(main())
""")
print()

print("Приклад 10: RAG Pipeline")
print("-" * 60)
print("""
# 1. Індексація документів
docs = [
    "Python is a programming language",
    "JavaScript is used for web development",
    "Machine learning uses neural networks"
]

# Генерація embeddings
embeddings = client.embeddings.create(input=docs)

# Створення колекції
client.collections.create("knowledge_base")

# Додавання в vector DB
points = [
    {
        "id": f"doc-{i}",
        "vector": emb.embedding,
        "payload": {"text": docs[i]}
    }
    for i, emb in enumerate(embeddings.data)
]

client.collections.upsert(name="knowledge_base", points=points)

# 2. Retrieval
query = "Tell me about Python"
query_emb = client.embeddings.create(input=query)

results = client.collections.search(
    name="knowledge_base",
    query=query_emb.data[0].embedding,
    limit=3
)

# 3. Augmentation
context = "\\n".join([
    point.payload["text"] for point in results.points
])

# 4. Generation
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": f"Context: {context}"},
        {"role": "user", "content": query}
    ]
)

print(response.choices[0].message.content)
""")
print()

print("Приклад 11: Error Handling")
print("-" * 60)
print("""
from friday import (
    Friday,
    RateLimitError,
    AuthenticationError,
    APIError
)

client = Friday(api_key="sk-...")

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError as e:
    print(f"Rate limit hit! Retry after {e.retry_after}s")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e.message}")
finally:
    client.close()
""")
print()

print("=" * 60)
print(" SDK Features Summary")
print("=" * 60 + "\n")

print("""
✅ Chat Completions (sync + async + streaming)
✅ Image Generation & Editing
✅ Text-to-Speech with emotions
✅ Embeddings with batch processing
✅ Vector Database (Qdrant)
✅ Usage Tracking & Monitoring
✅ OpenAI-compatible API
✅ Type-safe with Pydantic
✅ Error Handling
✅ Context Manager support
✅ Async/await support
✅ Retry with backoff
✅ Full documentation
""")

print("=" * 60)
print(" SDK готовий до використання!")
print("=" * 60)
