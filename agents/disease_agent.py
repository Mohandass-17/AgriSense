import math
from typing import Dict, Any
from agents.base_agent import BaseAgent

class DiseaseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DiseaseAgent",
            description="Predicts crop diseases using Vapor Pressure Deficit (VPD) modeling."
        )

    def _calculate_vpd(self, temp_c: float, humidity: float) -> float:
        """Calculates Vapor Pressure Deficit in kPa. Fungi thrive at VPD < 0.4 kPa."""
        # Saturation Vapor Pressure (SVP)
        svp = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
        # Actual Vapor Pressure (AVP)
        avp = svp * (humidity / 100.0)
        return svp - avp

    async def check_health(self, sensor_data: Dict[str, Any]):
        temp = float(sensor_data.get("temperature", 25))
        hum = float(sensor_data.get("humidity", 60))
        crop = str(sensor_data.get("crop_type", "unknown")).lower()
        
        vpd = self._calculate_vpd(temp, hum)
        
        risk_detected = None
        confidence = 0.0

        # High Risk: VPD is very low (heavy condensation/dew on leaves)
        if vpd < 0.4:
            if temp > 20:
                risk_detected = "early_blight"
                confidence = 0.92 - vpd  # Closer to 0 VPD = higher confidence
            else:
                risk_detected = "powdery_mildew"
                confidence = 0.88 - vpd
                
        # Root rot is driven by absolute soil saturation, independent of VPD
        soil_moisture = float(sensor_data.get("moisture", 0) or 0)
        if soil_moisture > 85 and temp > 15:
            risk_detected = "root_rot"
            confidence = (soil_moisture / 100.0)

        if risk_detected:
            alert = {
                "status": "disease_detected",
                "disease": risk_detected,
                "confidence": round(confidence, 2),
                "vpd_kpa": round(vpd, 2),
                "crop_type": crop,
                "location": sensor_data.get("location"),
                "recommendation_needed": True
            }
            await self.publish_event("disease_alerts", alert)
            return alert
        
        return {
            "status": "healthy", 
            "message": f"Environment optimal. VPD is safe at {round(vpd, 2)} kPa."
        }
