"""Real text-to-speech API examples."""

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
        section("1) Basic TTS")
        audio = client.audio.speech.create(
            input=(
                "Hello! This is a live Friday API text to speech test from Python."
            ),
            emotion="neutral",
        )
        print("Audio URL:", audio.audio_url)
        saved = download(audio.audio_url, "tts_neutral.mp3")
        print("Saved to:", saved)

        section("2) TTS With Emotion")
        happy_audio = client.audio.speech.create(
            input="Great news! Your API integration works correctly.",
            emotion="happy",
        )
        print("Audio URL:", happy_audio.audio_url)
        saved_happy = download(happy_audio.audio_url, "tts_happy.mp3")
        print("Saved to:", saved_happy)


if __name__ == "__main__":
    main()