import asyncio
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.main import app
from agents.disease_agent import DiseaseAgent

# 1. Test the Disease Logic directly
def test_disease_logic():
    agent = DiseaseAgent()
    
    # Scenario: High humidity and moderate temp (Powdery Mildew conditions)
    data = {"temperature": 22, "humidity": 70, "crop_type": "wheat"}
    result = asyncio.run(agent.check_health(data))
    
    assert result["status"] == "disease_detected"
    assert result["disease"] == "powdery_mildew"

# 2. Test the API Endpoint
def test_predict_endpoint():
    payload = {
        "device_id": "test-device-1",
        "crop_type": "tomato",
        "location": "tropical",
        "temperature": 20,
        "humidity": 95
    }
    with TestClient(app) as client:
        response = client.post("/disease/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disease_detected"
    # High humidity (>90) triggers root_rot in our DiseaseAgent logic
    assert data["disease"] == "root_rot"

# 3. Test Memory Service Integration
def test_memory_endpoint():
    with TestClient(app) as client:
        response = client.get("/memory/devices")
    assert response.status_code == 200
    assert "field-wheat-1" in response.json()["devices"]

# 4. Test the Method Not Allowed Fix
def test_get_on_predict_endpoint():
    with TestClient(app) as client:
        response = client.get("/disease/predict")
    assert response.status_code == 200
    assert "instruction" in response.json()


def test_llm_chat_endpoint():
    payload = {
        "question": "How do I treat powdery mildew on my tomatoes?",
        "crop_type": "tomato",
        "location": "greenhouse",
    }
    with TestClient(app) as client:
        response = client.post("/llm/chat", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "session_id" in body
    assert "reply" in body
    assert body["topic"] == "disease_management"
    assert "🔍 What to check:" in body["reply"]
    assert "⚠️ Problem signs:" in body["reply"]
    assert "✅ What to do:" in body["reply"]
    assert body["details"]["crop"] == "tomato"
    assert body["details"]["problem"] == "powdery mildew"
    assert "Gemini is not configured yet" not in body["reply"]


def test_llm_chat_varies_for_different_queries():
    with TestClient(app) as client:
        disease = client.post(
            "/llm/chat",
            json={
                "question": "How do I treat powdery mildew on tomatoes?",
                "crop_type": "tomato",
                "location": "greenhouse",
            },
        )
        fertilizer = client.post(
            "/llm/chat",
            json={
                "question": "Suggest fertilizer for paddy at tillering stage",
                "crop_type": "paddy",
            },
        )

    assert disease.status_code == 200
    assert fertilizer.status_code == 200
    assert disease.json()["reply"] != fertilizer.json()["reply"]


def test_llm_chat_paddy_fertilizer_response():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={
                "question": "What fertilizer should I use for paddy at tillering stage?",
                "crop_type": "paddy",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "fertilizer"
    assert "tillering" in body["reply"].lower()
    assert "basal dose" in body["reply"].lower()
    assert "panicle initiation" in body["reply"].lower()


def test_llm_chat_cotton_pest_response():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={
                "question": "How to control aphids in cotton?",
                "crop_type": "cotton",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "pest_control"
    assert "neem oil" in body["reply"].lower()
    assert "aphid" in body["reply"].lower()


def test_llm_chat_similar_questions_vary_wording():
    with TestClient(app) as client:
        first = client.post(
            "/llm/chat",
            json={"question": "How to control aphids in cotton?", "crop_type": "cotton"},
        )
        second = client.post(
            "/llm/chat",
            json={"question": "Cotton aphids management advice?", "crop_type": "cotton"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["reply"] != second.json()["reply"]


def test_llm_chat_rice_stem_borer_response():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={
                "question": "How to manage rice stem borer in paddy?",
                "crop_type": "paddy",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "pest_control"
    assert "early larval stage" in body["reply"].lower()
    assert "dead hearts" in body["reply"].lower()


def test_llm_chat_missing_crop_asks_follow_up():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={"question": "Which fertilizer should I apply now?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert "tell me the crop name first" in body["reply"].lower()
    assert "reply with the crop name" in body["reply"].lower()


def test_llm_chat_missing_crop_irrigation_gives_general_rule():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={"question": "How often should I irrigate now?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert "deep watering" in body["reply"].lower() or "water deeply" in body["reply"].lower()
    assert "soil moisture" in body["reply"].lower()
    assert "crop name" in body["reply"].lower()
    assert "drainage" in body["reply"].lower()


def test_llm_chat_crop_planning_has_examples():
    with TestClient(app) as client:
        response = client.post(
            "/llm/chat",
            json={"question": "Suggest a crop for my farm"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "crop_selection"
    assert "millets" in body["reply"].lower()
    assert "pulses" in body["reply"].lower()
    assert "paddy" in body["reply"].lower()


def test_irrigation_logic():
    from agents.irrigation_agent import IrrigationAgent

    agent = IrrigationAgent()
    payload = {"device_id": "test-device-2", "moisture": 20, "crop_type": "corn"}
    result = asyncio.run(agent.assess_moisture(payload))

    assert result["status"] == "irrigation_needed"
    assert result["action"] == "irrigate"
    assert result["crop_type"] == "corn"


def test_irrigation_assess_endpoint():
    payload = {"device_id": "test-device-3", "moisture": 30, "crop_type": "tomato"}
    with TestClient(app) as client:
        response = client.post("/irrigation/assess", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["crop_type"] == "tomato"
    assert "recommended_duration_minutes" in data


def test_irrigation_targets_endpoint():
    with TestClient(app) as client:
        response = client.get("/irrigation/targets")
    assert response.status_code == 200
    body = response.json()
    assert "crop_targets" in body
    assert "default" in body


def test_pest_logic():
    from agents.pest_agent import PestAgent

    agent = PestAgent()
    payload = {"crop_type": "tomato", "land": "greenhouse", "humidity": 78, "weather": "humid and calm"}
    result = asyncio.run(agent.recommend_pests(payload))

    assert result["status"] == "pest_alert"
    assert any(p["name"] == "aphids" for p in result["pests"])


def test_pest_recommend_endpoint():
    payload = {"crop_type": "corn", "land": "field", "humidity": 65, "weather": "overcast humid"}
    with TestClient(app) as client:
        response = client.post("/pest/recommend", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "pests" in body


def test_yield_logic():
    from agents.yield_agent import YieldAgent

    agent = YieldAgent()
    payload = {
        "crop_type": "corn",
        "land": "good",
        "weather": "favorable sunny",
        "humidity": 60,
        "recommendations": ["irrigation_upgrade", "balanced_nutrition"],
        "area_hectares": 2
    }
    result = asyncio.run(agent.project_yield(payload))

    assert result["status"] == "calculated"
    assert result["yield_gap_tonnes"] > 0


def test_yield_endpoint():
    payload = {
        "crop_type": "wheat",
        "land": "average",
        "weather": "cloudy",
        "humidity": 55,
        "recommendations": ["pest_control"],
        "area_hectares": 1.5
    }
    with TestClient(app) as client:
        response = client.post("/yield/project", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "without_recommendations_tonnes" in body
    assert "with_recommendations_tonnes" in body


def test_agent_registry_matches_live_agents():
    with TestClient(app) as client:
        response = client.get("/agents/status")

    assert response.status_code == 200
    body = response.json()
    names = {agent["name"] for agent in body["agents"]}
    assert body["total_agents"] == 5
    assert names == {
        "DiseaseAgent",
        "LLMAgent",
        "IrrigationAgent",
        "PestAgent",
        "YieldAgent",
    }
