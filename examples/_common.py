import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv  # Додаємо імпорт

# Шукає та завантажує файл .env у змінні середовища
load_dotenv()

OUTPUT_DIR = Path(__file__).resolve().parent / "_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def require_api_key() -> str:
    api_key = os.getenv("FRIDAY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set FRIDAY_API_KEY before running examples, "
            "e.g. PowerShell: $env:FRIDAY_API_KEY='sk-...'"
        )
    return api_key


def optional_base_url() -> Optional[str]:
    return os.getenv("FRIDAY_BASE_URL")


def section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)