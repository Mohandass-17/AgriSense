import logging
import asyncio
from typing import Dict, List, Callable, Any
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a.protocol")

class Message(BaseModel):
    sender: str
    topic: str
    data: Dict[str, Any]

class AgentBus:
    """The central communication hub for all Agri-Agents."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentBus, cls).__new__(cls)
            cls._instance.subscribers: Dict[str, List[Callable]] = {}
            cls._instance.agents: Dict[str, str] = {}
        return cls._instance

    def register_agent(self, agent_name: str, description: str):
        """Register an agent to the system."""
        self.agents[agent_name] = description
        logger.info(f"Bus: registering agent {agent_name}")

    def subscribe(self, topic: str, callback: Callable):
        """Allow an agent to listen to specific data (e.g., 'sensor_data')."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, sender: str, topic: str, data: Dict[str, Any]):
        """Publish data to the bus for other agents to consume."""
        message = Message(sender=sender, topic=topic, data=data)
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                # Run callbacks asynchronously so the bus doesn't hang
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)

# Global bus instance
bus = AgentBus()
