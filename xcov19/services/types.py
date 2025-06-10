from collections.abc import Callable, Coroutine
from typing import Any, Tuple


AsyncFunctionT = Callable[..., Coroutine]
CallableT = Callable | AsyncFunctionT
CallableTupleT = Tuple[CallableT, Any, Any]
