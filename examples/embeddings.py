"""Real embeddings API examples."""

import os
import sys
from math import sqrt

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if sys.path and os.path.abspath(sys.path[0]) == EXAMPLES_DIR:
    sys.path.append(sys.path.pop(0))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from friday import Friday

from _common import optional_base_url, require_api_key, section


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def main() -> None:
    api_key = require_api_key()
    kwargs = {"api_key": api_key}
    base_url = optional_base_url()
    if base_url:
        kwargs["base_url"] = base_url

    with Friday(**kwargs) as client:
        section("1) Single Embedding")
        emb = client.embeddings.create(input="Python SDK integration smoke test")
        vector = emb.data[0].embedding
        print("Vector length:", len(vector))
        print("First 8 values:", vector[:8])

        section("2) Batch Embeddings + Semantic Similarity")
        docs = [
            "FastAPI framework tutorial",
            "How to cook borshch",
            "Python type hints and pydantic models",
        ]
        doc_vectors = client.embeddings.create(input=docs)
        query = "I need help with Python API schemas"
        query_vector = client.embeddings.create(input=query).data[0].embedding

        scores = []
        for item in doc_vectors.data:
            score = cosine_similarity(query_vector, item.embedding)
            scores.append((item.index, score))
        scores.sort(key=lambda x: x[1], reverse=True)

        for idx, score in scores:
            print(f"[{idx}] score={score:.4f} -> {docs[idx]}")


if __name__ == "__main__":
    main()