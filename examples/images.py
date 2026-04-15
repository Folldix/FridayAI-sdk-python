"""
Приклади використання Images Resource
"""

print("=" * 60)
print(" FridayAI SDK - Images Resource Examples")
print("=" * 60 + "\n")

print("Приклад 1: Базова генерація зображення")
print("-" * 60)
print("""
from friday import Friday

client = Friday(api_key="sk-...")

# Генерація зображення
image = client.images.generate(
    prompt="A sunset over the ocean"
)

print(image.image_url)
# https://cdn.fridayai.com/images/abc123.png

# Збереження зображення
import requests

response = requests.get(image.image_url)
with open("sunset.png", "wb") as f:
    f.write(response.content)
""")
print()

print("Приклад 2: З кастомним розміром")
print("-" * 60)
print("""
# Маленьке зображення
image = client.images.generate(
    prompt="A cute cat",
    size="512x512"
)

# Велике зображення
image = client.images.generate(
    prompt="A detailed landscape",
    size="1920x1080"
)

# Квадратне HD
image = client.images.generate(
    prompt="Abstract art",
    size="1024x1024"
)
""")
print()

print("Приклад 3: Детальний опис")
print("-" * 60)
print("""
image = client.images.generate(
    prompt=\"\"\"
    A futuristic cyberpunk city at night,
    with neon lights reflecting on wet streets,
    flying cars in the sky,
    highly detailed, 4k quality,
    cinematic lighting
    \"\"\"
)
""")
print()

print("Приклад 4: Редагування зображення")
print("-" * 60)
print("""
# Редагування існуючого зображення
edited_image = client.images.edit(
    image_url="https://example.com/original.jpg",
    prompt="Add a rainbow to the sky"
)

print(edited_image.image_url)
""")
print()

print("Приклад 5: Зміна стилю")
print("-" * 60)
print("""
# Конвертація в інший стиль
edited = client.images.edit(
    image_url="https://example.com/photo.jpg",
    prompt="Convert to oil painting style"
)

# Додавання ефектів
edited = client.images.edit(
    image_url="https://example.com/landscape.jpg",
    prompt="Make it look like a vintage photograph from the 1970s"
)
""")
print()

print("Приклад 6: Async використання")
print("-" * 60)
print("""
import asyncio

async def generate_images():
    client = Friday(api_key="sk-...")
    
    # Генерація декількох зображень паралельно
    tasks = [
        client.images.agenerate(prompt="A sunset"),
        client.images.agenerate(prompt="A mountain"),
        client.images.agenerate(prompt="A forest")
    ]
    
    images = await asyncio.gather(*tasks)
    
    for i, img in enumerate(images):
        print(f"Image {i+1}: {img.image_url}")

asyncio.run(generate_images())
""")
print()

print("Приклад 7: Обробка помилок")
print("-" * 60)
print("""
from friday.exceptions import APIError, RateLimitError

try:
    image = client.images.generate(
        prompt="A beautiful landscape"
    )
except ValueError as e:
    print(f"Validation error: {e}")
except RateLimitError as e:
    print(f"Rate limit! Retry after {e.retry_after}s")
except APIError as e:
    print(f"API error: {e.message}")
""")
print()

print("Приклад 8: Серія зображень")
print("-" * 60)
print("""
# Генерація серії пов'язаних зображень
prompts = [
    "A medieval castle at dawn",
    "The same castle at noon",
    "The same castle at sunset",
    "The same castle at night"
]

images = []
for prompt in prompts:
    image = client.images.generate(prompt=prompt)
    images.append(image)
    print(f"Generated: {image.image_url}")
""")
print()

print("Приклад 9: З використанням base64 зображення")
print("-" * 60)
print("""
from friday._utils import encode_image_to_base64

# Кодуємо локальне зображення
local_image_url = encode_image_to_base64("my_photo.jpg")

# Редагуємо
edited = client.images.edit(
    image_url=local_image_url,
    prompt="Add dramatic lighting"
)
""")
print()

print("Приклад 10: Batch generation")
print("-" * 60)
print("""
def generate_batch(prompts: list) -> list:
    \"\"\"Генерує batch зображень\"\"\"
    results = []
    
    for i, prompt in enumerate(prompts):
        print(f"Generating {i+1}/{len(prompts)}: {prompt}")
        
        try:
            image = client.images.generate(prompt=prompt)
            results.append(image)
        except Exception as e:
            print(f"Error: {e}")
            results.append(None)
    
    return results

# Використання
prompts = [
    "A red apple",
    "A green tree",
    "A blue ocean"
]

images = generate_batch(prompts)
""")
print()

print("=" * 60)
print(" Best Practices")
print("=" * 60 + "\n")

print("""
1. Будьте детальні в описах для кращих результатів
2. Експериментуйте з різними розмірами
3. Обробляйте помилки (особливо RateLimitError)
4. Використовуйте async для batch generation
5. Зберігайте URL зображень для подальшого використання
6. Валідуйте prompts перед відправкою
""")

print("=" * 60)
print(" Всі приклади показано!")
print("=" * 60)