"""
Приклади використання Embeddings Resource
"""

print("=" * 60)
print(" FridayAI SDK - Embeddings Resource Examples")
print("=" * 60 + "\n")

print("Приклад 1: Базова генерація embedding")
print("-" * 60)
print("""
from friday import Friday

client = Friday(api_key="sk-...")

# Генерація embedding для одного тексту
embedding = client.embeddings.create(
    input="Hello, world!",
    model="embedding-model"
)

# Отримання вектора
vector = embedding.data[0].embedding
print(f"Vector dimension: {len(vector)}")
print(f"First 5 values: {vector[:5]}")
""")
print()

print("Приклад 2: Batch embeddings")
print("-" * 60)
print("""
# Генерація embeddings для множинних текстів
texts = [
    "Python is a programming language",
    "JavaScript is used for web development",
    "Machine learning uses neural networks"
]

embeddings = client.embeddings.create(
    input=texts,
    model="embedding-model"
)

# Обробка результатів
for emb in embeddings.data:
    print(f"Index {emb.index}:")
    print(f"  Dimensions: {len(emb.embedding)}")
    print(f"  First values: {emb.embedding[:3]}")
""")
print()

print("Приклад 3: Semantic search")
print("-" * 60)
print("""
import numpy as np

# Документи для пошуку
documents = [
    "Python is a high-level programming language",
    "JavaScript runs in web browsers",
    "Machine learning is a subset of AI",
    "React is a JavaScript library",
    "Deep learning uses neural networks"
]

# Створюємо embeddings для документів
doc_embeddings = client.embeddings.create(input=documents)

# Пошуковий запит
query = "Tell me about Python programming"
query_embedding = client.embeddings.create(input=query)

# Обчислюємо cosine similarity
query_vec = np.array(query_embedding.data[0].embedding)

similarities = []
for doc_emb in doc_embeddings.data:
    doc_vec = np.array(doc_emb.embedding)
    
    # Cosine similarity
    similarity = np.dot(query_vec, doc_vec) / (
        np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
    )
    
    similarities.append((doc_emb.index, similarity))

# Сортуємо за релевантністю
similarities.sort(key=lambda x: x[1], reverse=True)

print("Most relevant documents:")
for idx, score in similarities[:3]:
    print(f"{documents[idx]}: {score:.4f}")
""")
print()

print("Приклад 4: Кластеризація тексту")
print("-" * 60)
print("""
from sklearn.cluster import KMeans
import numpy as np

# Тексти для кластеризації
texts = [
    "Python programming",
    "JavaScript development",
    "Apple fruit",
    "Banana fruit",
    "Java programming",
    "Orange fruit"
]

# Генерація embeddings
embeddings = client.embeddings.create(input=texts)

# Конвертація у numpy array
vectors = np.array([
    emb.embedding for emb in embeddings.data
])

# K-means кластеризація
kmeans = KMeans(n_clusters=2, random_state=0)
clusters = kmeans.fit_predict(vectors)

# Виведення результатів
for i, text in enumerate(texts):
    print(f"{text}: Cluster {clusters[i]}")
""")
print()

print("Приклад 5: Async використання")
print("-" * 60)
print("""
import asyncio

async def main():
    client = Friday(api_key="sk-...")
    
    embedding = await client.embeddings.acreate(
        input="Hello from async!"
    )
    
    print(f"Dimensions: {len(embedding.data[0].embedding)}")
    print(f"First 5: {embedding.data[0].embedding[:5]}")

asyncio.run(main())
""")
print()

print("Приклад 6: Async batch processing")
print("-" * 60)
print("""
import asyncio

async def generate_embeddings_batch(texts: list):
    \"\"\"Генерує embeddings для batch текстів\"\"\"
    # Можна обробляти паралельно
    tasks = []
    
    # Розбиваємо на chunks по 10
    chunk_size = 10
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        task = client.embeddings.acreate(input=chunk)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Об'єднуємо результати
    all_embeddings = []
    for result in results:
        all_embeddings.extend(result.data)
    
    return all_embeddings

# Використання
texts = [f"Text number {i}" for i in range(100)]
embeddings = asyncio.run(generate_embeddings_batch(texts))
print(f"Generated {len(embeddings)} embeddings")
""")
print()

print("Приклад 7: Similarity matrix")
print("-" * 60)
print("""
import numpy as np

texts = ["Text A", "Text B", "Text C"]
embeddings = client.embeddings.create(input=texts)

# Створюємо матрицю векторів
vectors = np.array([emb.embedding for emb in embeddings.data])

# Обчислюємо similarity matrix
similarity_matrix = np.dot(vectors, vectors.T)

print("Similarity matrix:")
print(similarity_matrix)
""")
print()

print("Приклад 8: Recommender system")
print("-" * 60)
print("""
# Продукти
products = [
    "Laptop for programming",
    "Gaming mouse",
    "Mechanical keyboard",
    "Office chair",
    "Monitor 27 inch"
]

# Генерація embeddings
product_embeddings = client.embeddings.create(input=products)

# Користувацький запит
user_query = "I need something for coding"
query_embedding = client.embeddings.create(input=user_query)

# Знаходимо найбільш схожі продукти
query_vec = np.array(query_embedding.data[0].embedding)

recommendations = []
for prod_emb in product_embeddings.data:
    prod_vec = np.array(prod_emb.embedding)
    similarity = np.dot(query_vec, prod_vec)
    recommendations.append((prod_emb.index, similarity))

recommendations.sort(key=lambda x: x[1], reverse=True)

print("Recommended products:")
for idx, score in recommendations[:3]:
    print(f"{products[idx]}: {score:.4f}")
""")
print()

print("Приклад 9: Обробка помилок")
print("-" * 60)
print("""
from friday.exceptions import APIError, RateLimitError

try:
    embedding = client.embeddings.create(
        input="Test text"
    )
except ValueError as e:
    print(f"Validation error: {e}")
except RateLimitError as e:
    print(f"Rate limit! Retry after {e.retry_after}s")
except APIError as e:
    print(f"API error: {e.message}")
""")
print()

print("Приклад 10: Duplicate detection")
print("-" * 60)
print("""
# Тексти для перевірки на дублікати
texts = [
    "Hello, world!",
    "Hi there, world!",
    "Completely different text",
    "Hello, world!"  # Дублікат
]

embeddings = client.embeddings.create(input=texts)

# Перевірка схожості
threshold = 0.95

for i in range(len(embeddings.data)):
    for j in range(i + 1, len(embeddings.data)):
        vec_i = np.array(embeddings.data[i].embedding)
        vec_j = np.array(embeddings.data[j].embedding)
        
        similarity = np.dot(vec_i, vec_j) / (
            np.linalg.norm(vec_i) * np.linalg.norm(vec_j)
        )
        
        if similarity > threshold:
            print(f"Possible duplicate:")
            print(f"  Text {i}: {texts[i]}")
            print(f"  Text {j}: {texts[j]}")
            print(f"  Similarity: {similarity:.4f}")
""")
print()

print("=" * 60)
print(" Best Practices")
print("=" * 60 + "\n")

print("""
1. Нормалізуйте тексти перед генерацією embeddings
2. Використовуйте batch processing для множинних текстів
3. Кешуйте embeddings для повторного використання
4. Використовуйте cosine similarity для порівняння
5. Для великих dataset використовуйте vector databases
6. Async для паралельної обробки
7. Обробляйте помилки (особливо RateLimitError)
""")

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)