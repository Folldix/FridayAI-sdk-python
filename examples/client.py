"""Low-level HTTP client examples with real API requests."""

import os
import sys

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import asyncio

from friday._client import AsyncClient, BaseClient

from _common import optional_base_url, require_api_key, section


def sync_example() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    section("1) BaseClient direct request")
    with BaseClient(**kwargs) as client:
        response = client._make_request(  # pylint: disable=protected-access
            "POST",
            "/chat/completions",
            json={
                "conversation": [
                    {"role": "user", "content": "Reply exactly: LOW_LEVEL_OK"}
                ],
                "model": "friday_big",
                "stream": False,
            },
        )
        print(response)


async def async_example() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    section("2) AsyncClient direct request")
    client = AsyncClient(**kwargs)
    try:
        response = await client._make_request(  # pylint: disable=protected-access
            "POST",
            "/chat/completions",
            json={
                "conversation": [
                    {"role": "user", "content": "Reply exactly: ASYNC_LOW_LEVEL_OK"}
                ],
                "model": "friday_big",
                "stream": False,
            },
        )
        print(response)
    finally:
        await client.aclose()


def main() -> None:
    sync_example()
    asyncio.run(async_example())


if __name__ == "__main__":
    main()