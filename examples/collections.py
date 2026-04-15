"""
Приклади використання Collections Resource
"""

print("=" * 60)
print(" FridayAI SDK - Collections Resource Examples")
print("=" * 60 + "\n")

print("Приклад 1: Базові CRUD операції")
print("-" * 60)
print("""
from friday import Friday

client = Friday(api_key="sk-...")

# Список колекцій
collections = client.collections.list()
print(collections)  # ['docs', 'products']

# Створення колекції
result = client.collections.create("my_docs")
print(result)

# Інформація про колекцію
info = client.collections.retrieve("my_docs")
print(info.result)

# Видалення
result = client.collections.delete("old_collection")
""")
print()

print("Приклад 2: Додавання векторів")
print("-" * 60)
print("""
# Генерація embeddings
texts = ["Doc 1 text", "Doc 2 text", "Doc 3 text"]
embeddings = client.embeddings.create(input=texts)

# Підготовка points
points = []
for i, emb in enumerate(embeddings.data):
    points.append({
        "id": f"doc-{i+1}",
        "vector": emb.embedding,
        "payload": {
            "text": texts[i],
            "category": "general"
        }
    })

# Upsert
result = client.collections.upsert(
    name="my_docs",
    points=points
)
print(f"Operation ID: {result.operation_id}")
""")
print()

print("Приклад 3: Semantic search")
print("-" * 60)
print("""
# Пошуковий запит
query = "Tell me about Python"
query_emb = client.embeddings.create(input=query)

# Пошук схожих
results = client.collections.search(
    name="my_docs",
    query=query_emb.data[0].embedding,
    limit=5,
    score_threshold=0.7
)

# Результати
for point in results.points:
    print(f"ID: {point.id}")
    print(f"Score: {point.score:.4f}")
    print(f"Text: {point.payload['text']}")
    print()
""")
print()

print("Приклад 4: З фільтрами")
print("-" * 60)
print("""
# Пошук тільки в категорії 'tech'
results = client.collections.search(
    name="my_docs",
    query=query_vector,
    limit=10,
    filter={
        "must": [
            {"key": "category", "match": {"value": "tech"}}
        ]
    }
)
""")
print()

print("Приклад 5: RAG pipeline")
print("-" * 60)
print("""
# 1. Індексація документів
docs = ["Doc 1", "Doc 2", "Doc 3"]
embeddings = client.embeddings.create(input=docs)

points = [
    {
        "id": f"doc-{i}",
        "vector": emb.embedding,
        "payload": {"text": docs[i]}
    }
    for i, emb in enumerate(embeddings.data)
]

client.collections.upsert(name="knowledge", points=points)

# 2. Retrieval
query = "What is Python?"
query_emb = client.embeddings.create(input=query)

results = client.collections.search(
    name="knowledge",
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

print("=" * 60)
print(" Best Practices")
print("=" * 60 + "\n")

print("""
1. Створюйте окремі колекції для різних типів даних
2. Використовуйте payload для метаданих
3. Додавайте фільтри для точнішого пошуку
4. Встановлюйте score_threshold для якості
5. Batch upsert для множинних документів
6. Використовуйте RAG для контекстних відповідей
""")

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)