from abc import ABC, abstractmethod
from typing import Any


class FlowExecutionContext:

    def __init__(self, name: str, global_flow_context: dict[str, Any]):
        self.name = name
        self.global_flow_context = global_flow_context
        self.context: dict[str, Any] = {}

    def get_aggregated_context(self):
        context = {}
        if self.global_flow_context:
            context.update(self.global_flow_context)
        if self.context:
            context.update(self.context)
        return context


class FlowAction(ABC):

    @abstractmethod
    async def execute(self, context: FlowExecutionContext):
        """Execute the action with the given flow execution context."""
        pass
