"""Xuat dac ta OpenAPI bang lenh: python -m scripts.export_openapi."""
import json
from pathlib import Path

from app.main import app


def export_openapi() -> Path:
    path = Path(__file__).resolve().parents[1] / "openapi.json"
    path.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    print(f"Da xuat dac ta OpenAPI: {export_openapi()}")
