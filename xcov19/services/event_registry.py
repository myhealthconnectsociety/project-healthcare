from __future__ import annotations
from typing import Annotated, Callable, Coroutine, Dict, Optional
import dataclasses
import pydantic

AsyncFunctionT = Callable[..., Coroutine]
CallableFunctionT = AsyncFunctionT | Callable


@dataclasses.dataclass(order=True, frozen=True)
class EventService:
    callback: CallableFunctionT
    callback_description: Optional[str] = None
    priority: Annotated[int, pydantic.Field(default=0, ge=0)] = 0


class EventRegistry:
    def __init__(
        self, available_handlers: Dict[str, CallableFunctionT] | None = None
    ) -> None:
        self._event_handlers = {}
        self._available_handlers = available_handlers or {}

    def create_event_registry(self) -> Dict[str, EventService]:
        for event_name, event_handler_callback in self._available_handlers.items():
            self._create_event_registry(event_name, event_handler_callback)
        return self._event_handlers

    def _create_event_registry(
        self, /, event_name: str, event_callback: CallableFunctionT
    ) -> None:
        if event_name not in self._available_handlers:
            raise ValueError(f"No such event available: {event_name}")
        if event_name in self._event_handlers:
            raise KeyError(f"{event_name} already exists in running event handler")

        event_service = EventService(
            callback=event_callback,
        )
        self._event_handlers.update({event_name: event_service})
