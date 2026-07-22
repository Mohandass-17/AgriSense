import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from a2a.protocol import bus
from agents.disease_agent import DiseaseAgent
from agents.irrigation_agent import IrrigationAgent
from agents.llm_agent import LLMAgent
from agents.pest_agent import PestAgent
from agents.yield_agent import YieldAgent
from services.memory_service import memory_bank
from services.session_service import session_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - agri_agent - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agri_agent")

disease_engine = DiseaseAgent()
llm_engine = LLMAgent()
irrigation_engine = IrrigationAgent()
pest_engine = PestAgent()
yield_engine = YieldAgent()

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        "AgriSense System: %s agents initialized on the A2A bus: %s",
        len(bus.agents),
        ", ".join(sorted(bus.agents.keys())),
    )
    yield

app = FastAPI(title="AgriSense AI-Agent System", lifespan=lifespan)

ui_root = Path(__file__).resolve().parents[1] / "ui"
favicon_path = ui_root / "favicon.svg"

# Fixed: Root path now correctly redirects straight to your operational endpoint
@app.get("/")
def read_root():
    return RedirectResponse(url="/ui/agents")

@app.get("/status")
def status_info() -> dict:
    return {
        "message": "AgriSense API is online",
        "agents_registered": len(bus.agents),
        "llm_provider": llm_engine.provider,
        "llm_configured": llm_engine.is_configured,
        "llm_model": llm_engine.model,
    }

# Fixed: Removed the broken /ui page and cleanly mapped the console to /ui/agents
@app.get("/ui/agents")
def serve_agents_console() -> FileResponse:
    return FileResponse(ui_root / "agents.html")

@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "agents_registered": len(bus.agents),
        "memory_bank_status": "ready",
        "llm_configured": llm_engine.is_configured,
    }

@app.get("/agents/status")
def agents_status() -> dict:
    return {
        "total_agents": len(bus.agents),
        "agents": [{"name": name, "description": desc} for name, desc in bus.agents.items()]
    }

@app.get("/favicon.ico")
def favicon() -> FileResponse:
    return FileResponse(favicon_path)

@app.get("/memory/devices")
def get_devices() -> dict:
    return {"devices": memory_bank.get_devices()}

@app.get("/disease/predict")
def predict_info() -> dict:
    return {
        "instruction": "Send POST requests with sensor data. Example fields: moisture, humidity, temperature, leaf_spots."
    }

@app.post("/disease/predict")
async def predict_disease(data: dict) -> dict:
    if not data:
        raise HTTPException(status_code=422, detail="Sensor payload required.")
    logger.info("Disease prediction request received.")
    result = await disease_engine.check_health(data)
    if result.get("status") == "disease_detected":
        disease_name = result.get("disease")
        if disease_name:
            result["remedies"] = llm_engine.remedies.get(disease_name, {})
            logger.info("Remedy lookup supplied for %s", disease_name)
    return result

@app.post("/irrigation/assess")
async def assess_irrigation(data: dict) -> dict:
    if not data:
        raise HTTPException(status_code=422, detail="Sensor payload required.")
    logger.info("Irrigation assessment request received.")
    return await irrigation_engine.assess_moisture(data)

@app.get("/irrigation/targets")
def irrigation_targets() -> dict:
    return {
        "crop_targets": irrigation_engine.crop_moisture_targets,
        "default": irrigation_engine.default_target
    }

@app.post("/pest/recommend")
async def recommend_pests(data: dict) -> dict:
    if not data:
        raise HTTPException(status_code=422, detail="Sensor payload required.")
    logger.info("Pest recommendation request received.")
    return await pest_engine.recommend_pests(data)

@app.post("/yield/project")
async def project_yield(data: dict) -> dict:
    if not data:
        raise HTTPException(status_code=422, detail="Sensor payload required.")
    logger.info("Yield projection request received.")
    return await yield_engine.project_yield(data)

@app.post("/insight/story")
async def insight_story(data: dict) -> dict:
    if not data:
        raise HTTPException(status_code=422, detail="Sensor payload required.")
    
    disease = await disease_engine.check_health(data)
    irrigation = await irrigation_engine.assess_moisture(data)
    pest = await pest_engine.recommend_pests(data)
    yield_result = await yield_engine.project_yield(data)
    
    def disease_line() -> str:
        if disease.get("status") == "disease_detected":
            name = str(disease.get("disease", "a fungus")).replace("_", " ").title()
            vpd = disease.get("vpd_kpa", 0.0)
            return f"  Disease Alert: High risk of {name}. Vapor Pressure Deficit is critically low ({vpd} kPa), causing heavy canopy condensation."
        vpd = disease.get("message", "VPD is safe.")
        return f"  Canopy Health: Leaves are breathing well. {vpd}"
        
    def irrigation_line() -> str:
        action = irrigation.get("action", "monitor")
        paw = irrigation.get("plant_available_water_pct", 100)
        soil = irrigation.get("soil_type", "loam").title()
                 
        if action == "irrigate":
            dur = irrigation.get("recommended_duration_minutes", 0)
            return f"  Irrigation Needed: {soil} soil has only {paw}% plant-available water left. Run the drip line for {dur} mins to restore Field Capacity."
        if action == "reduce_watering":
            return f"  Waterlogged: {soil} soil is over-saturated. Stop watering immediately to prevent root suffocation."
        return f"  Soil Balance: Plant Available Water is stable at {paw}%. No irrigation required."
        
    def pest_line() -> str:
        pests = pest.get("pests", [])
        if pests:
            top = pests[0]
            name = str(top.get("name", "pests")).replace("_", " ").title()
            risk = top.get("risk_severity", 0)
            advice = top.get("advice", "Monitor closely.")
            return f"  Pest Surge Predicted: Weather synergy has created a {risk}% exponential risk for {name}. Action: {advice}"
        return "  Pest Control: Weather synergy is currently unfavorable for pest reproduction."
        
    def yield_line() -> str:
        gap = yield_result.get("yield_gap_tonnes", 0)
        limiting = yield_result.get("limiting_stress_factor", 1.0)
        limiting_pct = int(limiting * 100)
        return (
            f"  Yield Projection: Liebig's Law of the Minimum shows your current worst environmental stress is capping growth at {limiting_pct}% of its potential. "
            f"Fixing the bottlenecks above recovers {gap} tonnes."
        )
        
    return {
        "status": "story_ready",
        "story_lines": [disease_line(), irrigation_line(), pest_line(), yield_line()],
        "details": {
            "disease": disease,
            "irrigation": irrigation,
            "pest": pest,
            "yield": yield_result,
        },
    }

@app.post("/llm/chat")
async def llm_chat(data: dict) -> dict:
    if not data or not data.get("question"):
        raise HTTPException(status_code=422, detail="Question text required.")
    question = str(data.get("question")).strip()
    session_id = session_manager.ensure_session(data.get("session_id"))
    context = list(session_manager.get_context(session_id))
    metadata = {
        key: value
        for key, value in data.items()
        if key not in {"question", "session_id"} and value not in (None, "")
    }
    active_history = context + [{"role": "user", "text": question}]
    answer = await llm_engine.respond_to_query(
        question, metadata=metadata, history=active_history
    )
    session_manager.add_to_context(session_id, {"role": "user", "text": question})
    session_manager.add_to_context(
        session_id, {"role": "assistant", "text": answer["text"]}
    )
    return {
        "session_id": session_id,
        "reply": answer["text"],
        "topic": answer.get("topic", "chat"),
        "details": answer.get("details", {}),
    }

app.mount("/static", StaticFiles(directory=ui_root), name="static")