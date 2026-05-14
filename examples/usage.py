"""Real usage and limits API examples."""

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
        section("1) Usage Status")
        status = client.usage.retrieve()
        print(f"Token: {status.token_hash}")
        print(
            f"Chat: {status.usage.chat}/{status.limits.chat} "
            f"(remaining {status.remaining.chat})"
        )
        print(
            f"Image: {status.usage.image}/{status.limits.image} "
            f"(remaining {status.remaining.image})"
        )
        print(
            f"Voice: {status.usage.voice}/{status.limits.voice} "
            f"(remaining {status.remaining.voice})"
        )

        section("2) Recent Chat Logs")
        logs = client.usage.logs.list(limit=5)
        print("Logs count:", len(logs.items))
        for item in logs.items[:3]:
            preview = item.response[:90].replace("\n", " ")
            print(f"- {item.id} | {item.model} | {preview}")

        section("3) User Profile Info")
        info = client.usage.users.retrieve()
        print("Current user info:", info.info)


if __name__ == "__main__":
    main()