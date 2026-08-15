"""Xuất FastAPI OpenAPI specification cho frontend code generator."""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
OUTPUT_PATH = PROJECT_ROOT / "frontend" / "openapi.json"


def export_openapi() -> None:
    """Khởi tạo FastAPI app và ghi OpenAPI document ổn định ra frontend."""
    os.environ["DEBUG"] = "false"
    sys.path.insert(0, str(BACKEND_ROOT))

    from main import app

    document = json.dumps(app.openapi(), ensure_ascii=False, indent=2)
    OUTPUT_PATH.write_text(f"{document}\n", encoding="utf-8")


if __name__ == "__main__":
    export_openapi()
