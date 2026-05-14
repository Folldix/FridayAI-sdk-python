"""Real image generation API examples."""

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pathlib import Path

import requests

from friday import Friday

from _common import OUTPUT_DIR, optional_base_url, require_api_key, section


def download(url: str, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path


def main() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    with Friday(**kwargs) as client:
        section("1) Generate Image")
        image = client.images.generate(
            prompt=(
                "A realistic red fox wearing glasses, sitting at a laptop, "
                "soft studio lighting, ultra-detailed"
            ),
            size="1024x1024",
        )
        print("Generated URL:", image.image_url)
        saved = download(image.image_url, "image_generated.png")
        print("Saved to:", saved)

        section("2) Edit Existing Image")
        edited = client.images.edit(
            image_url=image.image_url,
            prompt="Keep composition, add rain and neon reflections on the ground",
            size="1024x1024",
        )
        print("Edited URL:", edited.image_url)
        saved_edited = download(edited.image_url, "image_edited.png")
        print("Saved to:", saved_edited)


if __name__ == "__main__":
    main()