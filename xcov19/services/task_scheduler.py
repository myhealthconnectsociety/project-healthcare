from collections.abc import Awaitable
from typing import Dict
import concurrent.futures as futures
import asyncio
from typing import List
from xcov19.services.event_registry import EventService


# TODO: change prints to logs agnostic to backend logger
class TaskScheduler:
    """
    TaskScheduler is responsible for managing and
    executing scheduled tasks.
    """

    def __init__(self, /, event_handlers: Dict[str, EventService], maxsize=0) -> None:
        """
        Initializes the TaskScheduler.
        """
        # ThreadPoolExecutor for running synchronous tasks in separate threads
        self.__thread_exc: futures.ThreadPoolExecutor | None = None
        # Event loop for running asynchronous tasks
        self.__loop: asyncio.AbstractEventLoop | None = None
        # Thread-safe queue for storing tasks to be executed
        self._queue = asyncio.Queue(maxsize=maxsize)
        # List to store tasks (callback, args, kwargs) to be executed.
        self.__tasks: List[Awaitable] = []
        self.__event_handlers = event_handlers
        self._is_running = True

    def add_task(self, event_name: str, *args, **kwargs) -> None:
        """Adds tasks to be run on startup.

        :param str: The event to be executed.
        :param args: Positional arguments to pass to the callback.
        :param kwargs: Keyword arguments to pass to the callback.
        """
        # Add the task to the queue for later execution as per queue.
        event_service: EventService = self.__event_handlers["event_name"]
        self._queue.put_nowait((event_service.callback, args, kwargs))
        print(f"TaskScheduler: Task added {event_name}.")

    async def run(self) -> None:
        """Starts task scheduler in a non-blocking loop."""
        # Get the current running event loop
        self.__loop = asyncio.get_running_loop()
        # Set a custom task factory to run coroutines eagerly
        self.__loop.set_task_factory(asyncio.eager_task_factory)
        asyncio.run_coroutine_threadsafe(self._run(), self.__loop)
        asyncio.run_coroutine_threadsafe(self._execute_tasks(), self.__loop)

    async def _execute_tasks(self) -> None:
        while self._is_running:
            if self.__tasks:
                print("TaskScheduler: Running background tasks")
                # Run all tasks concurrently and wait for them to complete
                await asyncio.gather(*self.__tasks)
                self.__tasks.clear()

    async def _run(self) -> None:
        """Executes scheduled tasks.

        Determines if they are coroutines or synchronous
        and running them accordingly.
        """
        assert self.__loop
        while item := await self._queue.get():
            # TODO: Upon failure, add back to queue.
            # task_done only when successful. Could be retry logic.
            self._queue.task_done()
            callback, args, kwargs = item
            # Continuously fetch tasks from the queue
            if asyncio.iscoroutinefunction(callback):
                # Schedule coroutine tasks on the event loop
                task: asyncio.Task = self.__loop.create_task(callback(*args, **kwargs))
                self.__tasks += [task]
            else:
                # Use ThreadPoolExecutor for synchronous tasks
                self.__thread_exc = futures.ThreadPoolExecutor()
                self.__tasks += [
                    self.__loop.run_in_executor(
                        self.__thread_exc, lambda: callback(*args, **kwargs)
                    )
                ]
            print("TaskScheduler: Added callback from queue to task.")
        self._queue.task_done()

    def on_shutdown(self) -> None:
        """
        Shuts down the task scheduler, cancelling any remaining tasks.
        """
        # Clear the list of tasks
        self._queue.put_nowait(None)
        self._running = False
        self.__tasks.clear()
        if self.__thread_exc:
            print("TaskScheduler: shutting down thread")
            # Shutdown the ThreadPoolExecutor
            self.__thread_exc.shutdown(cancel_futures=True)
        print("TaskScheduler: shutdown")
