from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass