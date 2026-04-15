"""
Приклади використання Chat Resource
"""

print("=" * 60)
print(" FridayAI SDK - Chat Resource Examples")
print("=" * 60 + "\n")

print("Приклад 1: Базовий запит")
print("-" * 60)
print("""
from friday import Friday

client = Friday(api_key="sk-...")

response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello, Friday!"}
    ],
    model="friday_big"
)

print(response.choices[0].message.content)
# "Hello! How can I help you today?"
""")
print()

print("Приклад 2: Streaming")
print("-" * 60)
print("""
stream = client.chat.completions.create(
    messages="Tell me a story",
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")
""")
print()

print("Приклад 3: З зображенням")
print("-" * 60)
print("""
response = client.chat.completions.create(
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image", "image": {"url": "https://..."}}
        ]
    }]
)
""")
print()

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)