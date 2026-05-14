"""One-shot manual smoke test for the main API modules."""

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from friday import Friday

from _common import optional_base_url, require_api_key, section


def main() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    with Friday(**kwargs) as client:
        section("1) Chat")
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": "what is RGB?"}],
            model="friday_big",
        )
        print(chat.choices[0].message.content)

        section("2) Image")
        image = client.images.generate(
            prompt="Minimalistic logo of a Friday robot, flat vector style"
        )
        print("Image URL:", image.image_url)

        section("3) Audio")
        audio = client.audio.speech.create(
            input="Friday API smoke test. Audio module is operational.",
            emotion="neutral",
        )
        print("Audio URL:", audio.audio_url)

        section("4) Embeddings")
        emb = client.embeddings.create(
            input=["python sdk", "vector embeddings", "weather forecast"]
        )
        print("Embeddings returned:", len(emb.data))
        print("Embedding dims (index 0):", len(emb.data[0].embedding))

        section("5) Usage")
        usage = client.usage.retrieve()
        print(
            "Chat usage:",
            f"{usage.usage.chat}/{usage.limits.chat}",
            f"(remaining {usage.remaining.chat})",
        )


if __name__ == "__main__":
    main()
