import time
from typing import Dict, Any
from agents.base_agent import BaseAgent
from services.memory_service import memory_bank

class IrrigationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="IrrigationAgent",
            description="Manages irrigation using Field Capacity and Wilting Points."
        )
        # Soil volumetric water content thresholds
        self.soil_profiles = {
            "sand": {"fc": 15, "pwp": 7},    # Field Capacity & Permanent Wilting Point
            "loam": {"fc": 30, "pwp": 15},
            "clay": {"fc": 45, "pwp": 25}
        }
        self.alert_cooldown_seconds = 900
        self.last_irrigation_alert: Dict[str, float] = {}

    def _can_alert(self, device_id: str) -> bool:
        last = self.last_irrigation_alert.get(device_id)
        return True if last is None else (time.time() - last) >= self.alert_cooldown_seconds

    async def assess_moisture(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        device_id = sensor_data.get("device_id", "unknown-device")
        moisture = sensor_data.get("moisture", sensor_data.get("soil_moisture"))
        soil_type = str(sensor_data.get("soil_type", "loam")).lower()
        
        if soil_type not in self.soil_profiles:
            soil_type = "loam" # fallback

        if moisture is None:
            return {"status": "needs_moisture_reading", "device_id": device_id}

        moisture = float(moisture)
        crop = sensor_data.get("crop_type", "generic").lower()
        profile = self.soil_profiles[soil_type]
        
        # Calculate Plant Available Water (PAW) percentage
        paw_total = profile["fc"] - profile["pwp"]
        current_paw = moisture - profile["pwp"]
        paw_percent = (current_paw / paw_total) * 100 if paw_total > 0 else 0

        action = "monitor"
        status = "optimal"
        recommended_duration = 0

        # Trigger irrigation if Plant Available Water drops below 50%
        if paw_percent < 50:
            action = "irrigate"
            status = "irrigation_needed"
            # Calculate mm of water needed to reach Field Capacity
            deficit = profile["fc"] - moisture
            recommended_duration = int(deficit * 2.5) # 2.5 mins per % deficit proxy
        elif moisture > profile["fc"]:
            action = "reduce_watering"
            status = "waterlogged"
            recommended_duration = 0

        result = {
            "device_id": device_id,
            "status": status,
            "action": action,
            "soil_type": soil_type,
            "plant_available_water_pct": round(paw_percent, 1),
            "recommended_duration_minutes": max(0, recommended_duration),
            "confidence": 0.85
        }

        memory_bank.record_reading(device_id, {**sensor_data, "action": action})

        if action == "irrigate" and self._can_alert(device_id):
            self.last_irrigation_alert[device_id] = time.time()
            await self.publish_event("irrigation_alerts", result)

        return result