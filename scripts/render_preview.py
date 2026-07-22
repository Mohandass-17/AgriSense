from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.main import app


def run_demo():
    client = TestClient(app)
    examples = [
        ("GET", "/", {}),
        ("GET", "/health", {}),
        ("GET", "/agents/status", {}),
        ("GET", "/memory/devices", {}),
        ("GET", "/disease/predict", {}),
        (
            "POST",
            "/disease/predict",
            {"leaf_spots": 40, "humidity": 80, "moisture": 50, "temperature": 25},
        ),
        ("POST", "/disease/predict", {"moisture": 80}),
    ]

    for method, path, payload in examples:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json=payload)
        print(f"{method} {path} -> {response.status_code}")
        print(response.json())
        print("-" * 74)


if __name__ == "__main__":
    run_demo()
