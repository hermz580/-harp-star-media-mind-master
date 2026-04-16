from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """Interface for specialist agent plugins"""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
