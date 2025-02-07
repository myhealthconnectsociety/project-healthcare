from typing import Any, Callable, Dict, Tuple
import dataclasses
from xcov19.services.queue import diagnosis_queue, store_queue_event


@dataclasses.dataclass(order=True, frozen=True)
class StartupServices:
    callback: Callable
    args: Tuple[Any]
    kwargs: Dict[str, Any]


STARTUP_SERVICE_LIST = [
    StartupServices(
        callback=store_queue_event,
        args=(diagnosis_queue,),
        kwargs={},
    ),
]
