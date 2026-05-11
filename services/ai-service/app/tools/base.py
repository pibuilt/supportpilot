from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(
        self,
        **kwargs,
    ) -> Dict[str, Any]:
        pass