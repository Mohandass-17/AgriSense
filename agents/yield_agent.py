from typing import Any, Dict, List
from agents.base_agent import BaseAgent

class YieldAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="YieldAgent",
            description="Projects yield using Liebig's Law of the Minimum."
        )
        self.base_yield: Dict[str, float] = {
            "wheat": 3.5, "corn": 6.0, "rice": 4.2, 
            "tomato": 70.0, "cotton": 2.0,
        }
        self.practice_uplifts = {
            "balanced_nutrition": 0.15,
            "irrigation_upgrade": 0.20,
            "pest_control": 0.10,
        }

    async def project_yield(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        crop = str(sensor_data.get("crop_type", "wheat")).lower()
        area = float(sensor_data.get("area_hectares", 1) or 1)
        base = self.base_yield.get(crop, 3.0)

        # 1. Calculate Individual Stress Factors (1.0 is perfect, 0.0 is dead)
        stresses = []
        
        # Moisture Stress
        moisture = float(sensor_data.get("moisture", 40) or 40)
        if 25 <= moisture <= 50:
            stresses.append(1.0)
        else:
            deviation = abs(35 - moisture)
            stresses.append(max(0.1, 1.0 - (deviation * 0.02)))
            
        # Temperature Stress
        temp = float(sensor_data.get("temperature", 25) or 25)
        if 18 <= temp <= 30:
            stresses.append(1.0)
        else:
            deviation = abs(24 - temp)
            stresses.append(max(0.2, 1.0 - (deviation * 0.05)))

        # 2. Apply Liebig's Law of the Minimum
        # The crop is only as good as its worst condition
        limiting_factor = min(stresses)
        
        # Calculate baseline potential without human intervention
        without_recs = base * area * limiting_factor

        # 3. Apply Management Uplifts
        recommendations = sensor_data.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = [recommendations]

        management_multiplier = 1.0
        for rec in recommendations:
            management_multiplier += self.practice_uplifts.get(rec.lower(), 0)

        with_recs = without_recs * management_multiplier

        return {
            "status": "calculated",
            "crop_type": crop,
            "limiting_stress_factor": round(limiting_factor, 2),
            "without_recommendations_tonnes": round(without_recs, 2),
            "with_recommendations_tonnes": round(with_recs, 2),
            "yield_gap_tonnes": round(with_recs - without_recs, 2),
            "insight": "Calculated using Liebig's Law of the Minimum based on current environmental bottlenecks."
        }
