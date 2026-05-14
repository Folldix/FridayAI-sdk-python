"""Collections API example (experimental in current SDK state)."""

import os
import sys
import time

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

    collection_name = f"sdk_example_{int(time.time())}"

    with Friday(**kwargs) as client:
        section("1) List Collections")
        names = client.collections.list()
        print("Existing collections:", names)

        section("2) Create Collection")
        create_result = client.collections.create(collection_name)
        print(create_result)

        section("3) Upsert + Search")
        texts = [
            "Kyiv is the capital of Ukraine",
            "Python is great for scripting",
            "Embeddings are useful for semantic search",
        ]
        embs = client.embeddings.create(input=texts)
        points = [
            {"id": f"p{i}", "vector": item.embedding, "payload": {"text": texts[i]}}
            for i, item in enumerate(embs.data)
        ]
        upsert = client.collections.upsert(name=collection_name, points=points)
        print("Upsert operation:", upsert.operation_id)

        query_vec = client.embeddings.create(input="Tell me about Python").data[0].embedding
        result = client.collections.search(name=collection_name, query=query_vec, limit=3)
        for p in result.points:
            print(f"- {p.id} ({p.score:.4f}) => {p.payload.get('text')}")

        section("4) Cleanup")
        delete_result = client.collections.delete(collection_name)
        print(delete_result)


if __name__ == "__main__":
    main()