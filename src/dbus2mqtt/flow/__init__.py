from abc import ABC, abstractmethod
from typing import Any


class FlowExecutionContext:

    def __init__(self, name: str | None, global_flows_context: dict[str, Any], flow_context: dict[str, Any]):
        self.name = name
        self.global_flows_context = global_flows_context
        self.flow_context = flow_context

        # per flow execution context
        self.context: dict[str, Any] = {}

    def get_aggregated_context(self) -> dict[str, Any]:
        """Get the aggregated context for the flow execution."""
        # Merge global flows context, flow context, and local context
        context = {}
        if self.global_flows_context:
            context.update(self.global_flows_context)
        if self.flow_context:
            context.update(self.flow_context)
        if self.context:
            context.update(self.context)
        return context

class FlowAction(ABC):

    @abstractmethod
    async def execute(self, context: FlowExecutionContext):
        """Execute the action with the given flow execution context."""
        pass
