"""
Приклади використання Audio Resource
"""

print("=" * 60)
print(" FridayAI SDK - Audio Resource Examples")
print("=" * 60 + "\n")

print("Приклад 1: Базова генерація аудіо")
print("-" * 60)
print("""
from friday import Friday

client = Friday(api_key="sk-...")

# Генерація аудіо
audio = client.audio.speech.create(
    input="Hello, how are you today?"
)

print(audio.audio_url)
# https://cdn.fridayai.com/audio/abc123.mp3

# Збереження аудіо
import requests

response = requests.get(audio.audio_url)
with open("speech.mp3", "wb") as f:
    f.write(response.content)
""")
print()

print("Приклад 2: З різними емоціями")
print("-" * 60)
print("""
# Радісний голос
audio = client.audio.speech.create(
    input="I'm so happy to see you!",
    emotion="happy"
)

# Сумний голос
audio = client.audio.speech.create(
    input="I'm feeling a bit down today.",
    emotion="sad"
)

# Нейтральний (за замовчуванням)
audio = client.audio.speech.create(
    input="This is a neutral statement."
)

# Злий голос
audio = client.audio.speech.create(
    input="I'm not happy about this!",
    emotion="angry"
)
""")
print()

print("Приклад 3: Довгий текст")
print("-" * 60)
print("""
long_text = \"\"\"
Welcome to FridayAI!
This is an example of converting long text into speech.
You can use this feature for various applications like
audiobooks, voice assistants, or accessibility tools.
\"\"\"

audio = client.audio.speech.create(input=long_text)
print(f"Generated: {audio.audio_url}")
""")
print()

print("Приклад 4: Async використання")
print("-" * 60)
print("""
import asyncio

async def main():
    client = Friday(api_key="sk-...")
    
    audio = await client.audio.speech.acreate(
        input="Hello from async!"
    )
    
    print(audio.audio_url)

asyncio.run(main())
""")
print()

print("Приклад 5: Batch generation")
print("-" * 60)
print("""
texts = [
    "Hello, welcome to chapter 1",
    "This is chapter 2 of our story",
    "And here we have chapter 3"
]

audios = []
for i, text in enumerate(texts):
    print(f"Generating {i+1}/{len(texts)}")
    
    audio = client.audio.speech.create(input=text)
    audios.append(audio)
    
    # Збереження
    response = requests.get(audio.audio_url)
    with open(f"chapter_{i+1}.mp3", "wb") as f:
        f.write(response.content)
""")
print()

print("Приклад 6: Async batch generation")
print("-" * 60)
print("""
import asyncio

async def generate_batch(texts: list) -> list:
    \"\"\"Генерує batch аудіо\"\"\"
    tasks = [
        client.audio.speech.acreate(input=text)
        for text in texts
    ]
    return await asyncio.gather(*tasks)

# Використання
texts = [
    "First sentence",
    "Second sentence", 
    "Third sentence"
]

audios = asyncio.run(generate_batch(texts))

for i, audio in enumerate(audios):
    print(f"Audio {i+1}: {audio.audio_url}")
""")
print()

print("Приклад 7: Обробка помилок")
print("-" * 60)
print("""
from friday.exceptions import APIError, RateLimitError

try:
    audio = client.audio.speech.create(
        input="Hello, world!"
    )
except ValueError as e:
    print(f"Validation error: {e}")
except RateLimitError as e:
    print(f"Rate limit! Retry after {e.retry_after}s")
except APIError as e:
    print(f"API error: {e.message}")
""")
print()

print("Приклад 8: Створення аудіокниги")
print("-" * 60)
print("""
# Розбиваємо книгу на розділи
chapters = [
    "Chapter 1: Once upon a time...",
    "Chapter 2: The adventure begins...",
    "Chapter 3: A new friend appears..."
]

for i, chapter in enumerate(chapters, 1):
    print(f"Processing chapter {i}")
    
    # Генерація аудіо
    audio = client.audio.speech.create(
        input=chapter,
        emotion="neutral"
    )
    
    # Збереження
    response = requests.get(audio.audio_url)
    filename = f"audiobook_chapter_{i}.mp3"
    
    with open(filename, "wb") as f:
        f.write(response.content)
    
    print(f"Saved: {filename}")
""")
print()

print("Приклад 9: Різні мови (якщо підтримується)")
print("-" * 60)
print("""
# Англійський
audio_en = client.audio.speech.create(
    input="Hello, how are you?"
)

# Український
audio_uk = client.audio.speech.create(
    input="Привіт, як справи?"
)

# Інші мови...
""")
print()

print("Приклад 10: Інтеграція з іншими features")
print("-" * 60)
print("""
# Згенерувати текст, потім озвучити
chat_response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Write a short poem"}
    ]
)

poem = chat_response.choices[0].message.content

# Озвучити поему
audio = client.audio.speech.create(
    input=poem,
    emotion="neutral"
)

print(f"Poem audio: {audio.audio_url}")
""")
print()

print("=" * 60)
print(" Best Practices")
print("=" * 60 + "\n")

print("""
1. Валідуйте текст перед відправкою
2. Розбивайте довгі тексти на частини
3. Обробляйте помилки (особливо RateLimitError)
4. Використовуйте async для batch generation
5. Зберігайте URL для подальшого використання
6. Експериментуйте з різними емоціями
7. Для аудіокниг використовуйте нейтральну емоцію
""")

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)