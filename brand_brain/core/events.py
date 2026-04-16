import asyncio
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, type: str, data: Dict[str, Any] = None, source: str = "system"):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.type = type
        self.data = data or {}
        self.source = source

class EventBus:
    """The central nervous system for Harp * Star OS v3"""
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.history: List[Event] = []
        self._max_history = 100

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.info(f"👂 New subscriber for {event_type}")

    async def emit(self, event: Event):
        logger.info(f"📡 Event Emitted: [{event.type}] from {event.source}")

        # Record history
        self.history.append(event)
        if len(self.history) > self._max_history:
            self.history.pop(0)

        # Notify listeners
        if event.type in self.listeners:
            tasks = [callback(event) for callback in self.listeners[event.type]]
            await asyncio.gather(*tasks, return_exceptions=True)

        # Global listeners (wildcard)
        if "*" in self.listeners:
            tasks = [callback(event) for callback in self.listeners["*"]]
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_state(self):
        """Returns the current 'Live State' based on the most recent events"""
        return {
            "last_event": self.history[-1].__dict__ if self.history else None,
            "event_count": len(self.history),
            "history_summary": [{"type": e.type, "source": e.source} for e in self.history[-10:]]
        }

# Global singleton
bus = EventBus()
