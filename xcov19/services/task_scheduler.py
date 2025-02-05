from typing import Any, Coroutine
import concurrent.futures as futures
import asyncio
import sched
import time
from typing import Callable, List, Tuple


AsyncFunctionT = Callable[..., Coroutine]
CallableTupleT = Tuple[Callable | AsyncFunctionT, Any, Any]


# TODO: change prints to logs agnostic to backend logger
class TaskScheduler:
    def __init__(self) -> None:
        self.__thread_exc: futures.ThreadPoolExecutor | None = None
        self.__loop: asyncio.AbstractEventLoop | None = None
        self.__tasks: List[CallableTupleT] = []

    def add_task_on_startup(
        self, callback: Callable | AsyncFunctionT, *args, **kwargs
    ) -> None:
        self.__tasks += [(callback, args, kwargs)]

    async def run(self) -> None:
        self.__loop = asyncio.get_running_loop()
        self.__loop.set_task_factory(asyncio.eager_task_factory)
        asyncio.run_coroutine_threadsafe(self._run_task(), self.__loop)

    async def _run_task(self) -> None:
        awaitable_tasks = []
        while self.__tasks and self.__loop:
            for callback, args, kwargs in self.__tasks:
                if asyncio.iscoroutinefunction(callback):
                    awaitable_tasks += [
                        self.__loop.create_task(callback(*args, **kwargs))
                    ]
                else:
                    self.__thread_exc = futures.ThreadPoolExecutor()
                    awaitable_tasks += [
                        self.__loop.run_in_executor(
                            self.__thread_exc, lambda: callback(*args, **kwargs)
                        )
                    ]
            print("TaskScheduler: Running background tasks")
            await asyncio.gather(*awaitable_tasks)
            await asyncio.sleep(5)
            awaitable_tasks.clear()

    def on_shutdown(self) -> None:
        self.__tasks.clear()
        if self.__thread_exc:
            self.__thread_exc.shutdown(cancel_futures=True)
        print("TaskScheduler: shutdown")


scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)
task_scheduler = TaskScheduler()
