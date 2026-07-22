import time
from typing import Any, Dict, List, Optional

class MemoryService:
    def __init__(self):
        # Stores device metadata
        self.device_registry = {
            "field-wheat-1": {"type": "wheat", "location": "temperate", "added": time.time()},
            "field-corn-1": {"type": "corn", "location": "temperate", "added": time.time()},
            "field-tomato-1": {"type": "tomato", "location": "tropical", "added": time.time()}
        }
        # Stores historical readings for trend analysis
        self.history: Dict[str, List[Dict]] = {}

    def register_device(self, device_id: str, metadata: dict):
        self.device_registry[device_id] = {**metadata, "added": time.time()}

    def record_reading(self, device_id: str, data: dict):
        if device_id not in self.history:
            self.history[device_id] = []
        
        # Keep only the last 100 readings to save memory
        self.history[device_id].append({"timestamp": time.time(), **data})
        if len(self.history[device_id]) > 100:
            self.history[device_id].pop(0)

    def get_all_devices(self) -> List[str]:
        return list(self.device_registry.keys())

    def get_device_info(self, device_id: str) -> Optional[Dict]:
        return self.device_registry.get(device_id)

    def get_devices(self) -> List[str]:
        return self.get_all_devices()

# Global memory instance
memory_bank = MemoryService()
