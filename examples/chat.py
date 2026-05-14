"""Real chat API examples you can run directly."""

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


def run_basic_chat(client: Friday) -> None:
    section("1) Basic Chat Completion")
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": (
                    "You are being tested from a Python SDK example. "
                    "Reply with: OK CHAT WORKS"
                ),
            }
        ],
        model="friday_big",
    )
    print("Model:", response.model)
    print("Reply:", response.choices[0].message.content)


def run_streaming_chat(client: Friday) -> None:
    section("2) Streaming Chat Completion")
    stream = client.chat.completions.create(
        messages=(
            "Write a short 4-line poem about Kyiv and software engineering. "
            "Return plain text only."
        ),
        model="friday_big",
        stream=True,
    )
    print("Stream output:")
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()


def main() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    with Friday(**kwargs) as client:
        run_basic_chat(client)
        run_streaming_chat(client)


if __name__ == "__main__":
    main()