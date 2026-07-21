import math
from typing import Any, Dict, List
from agents.base_agent import BaseAgent

class PestAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PestAgent",
            description="Calculates exponential pest population risks based on climate synergy."
        )
        self.pest_profiles = {
            "aphids": {
                "crops": ["tomato", "corn", "wheat", "cotton"],
                "opt_temp": 22, "opt_hum": 75,
                "advice": "Use neem oil; deploy ladybugs. Monitor for honeydew."
            },
            "whitefly": {
                "crops": ["tomato", "cotton", "okra"],
                "opt_temp": 28, "opt_hum": 60,
                "advice": "Deploy yellow sticky traps; release Encarsia formosa."
            },
            "stem_borer": {
                "crops": ["corn", "rice", "sorghum"],
                "opt_temp": 26, "opt_hum": 85,
                "advice": "Remove egg masses; apply Bacillus thuringiensis (Bt)."
            }
        }

    def _calculate_synergy_risk(self, profile: Dict, temp: float, hum: float) -> float:
        """Uses a Gaussian function to model exponential population explosions near optimal conditions."""
        temp_variance = 25  # Spread of temperature tolerance
        hum_variance = 400  # Spread of humidity tolerance
        
        # Calculate deviation from optimal conditions
        temp_factor = math.exp(-((temp - profile["opt_temp"])**2) / temp_variance)
        hum_factor = math.exp(-((hum - profile["opt_hum"])**2) / hum_variance)
        
        # Synergy: Both must be high for a massive outbreak
        return temp_factor * hum_factor

    async def recommend_pests(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        temp = float(sensor_data.get("temperature", 25))
        hum = float(sensor_data.get("humidity", 60))
        crop = str(sensor_data.get("crop_type", "")).strip().lower()

        pests: List[Dict[str, Any]] = []
        for pest_name, profile in self.pest_profiles.items():
            if crop and crop not in profile["crops"]:
                continue
                
            risk_score = self._calculate_synergy_risk(profile, temp, hum)
            
            if risk_score > 0.60: # 60% exponential risk threshold
                pests.append({
                    "name": pest_name,
                    "risk_severity": round(risk_score * 100, 1),
                    "advice": profile["advice"]
                })

        # Sort by highest risk
        pests.sort(key=lambda x: x["risk_severity"], reverse=True)

        return {
            "status": "pest_alert" if pests else "clear",
            "pests": pests,
            "summary": f"{len(pests)} pest population explosions predicted." if pests else "Low pest pressure."
        }