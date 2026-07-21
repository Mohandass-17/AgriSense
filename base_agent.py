from a2a.protocol import bus, Message
import logging

class BaseAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(name)
        # Auto-register upon initialization
        bus.register_agent(name, description)

    async def publish_event(self, topic: str, data: dict):
        """Standard way for agents to send data to the system."""
        self.logger.info(f"Publishing to {topic}: {data}")
        await bus.publish(self.name, topic, data)

    def subscribe_to(self, topic: str, callback):
        """Standard way for agents to listen for data."""
        bus.subscribe(topic, callback)
        self.logger.info(f"Subscribed to topic: {topic}")