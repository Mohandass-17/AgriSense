import time
import uuid
from typing import Dict, Optional

class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "start_time": time.time(),
            "context": [],
            "last_interaction": time.time()
        }
        return session_id

    def ensure_session(self, session_id: Optional[str]) -> str:
        if session_id and session_id in self.sessions:
            return session_id
        return self.create_session()

    def add_to_context(self, session_id: str, interaction: dict):
        if session_id in self.sessions:
            self.sessions[session_id]["context"].append(interaction)
            self.sessions[session_id]["last_interaction"] = time.time()

    def get_context(self, session_id: str):
        return self.sessions.get(session_id, {}).get("context", [])

# Global session instance
session_manager = SessionService()
