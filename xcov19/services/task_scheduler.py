from typing import Any, Coroutine
import concurrent.futures as futures
import asyncio
from typing import Callable, List, Tuple

AsyncFunctionT = Callable[..., Coroutine]
CallableTupleT = Tuple[Callable | AsyncFunctionT, Any, Any]


# TODO: change prints to logs agnostic to backend logger
class TaskScheduler:
    """
    TaskScheduler is responsible for managing and
    executing scheduled tasks.
    """

    def __init__(self, maxsize=0) -> None:
        """
        Initializes the TaskScheduler.
        """
        # ThreadPoolExecutor for running synchronous tasks in separate threads
        self.__thread_exc: futures.ThreadPoolExecutor | None = None
        # Event loop for running asynchronous tasks
        self.__loop: asyncio.AbstractEventLoop | None = None
        # Thread-safe queue for storing tasks to be executed
        self._queue = asyncio.Queue(maxsize=maxsize)
        # List to store tasks as tuples of (callback, args, kwargs)
        self.__tasks: List[CallableTupleT] = []

    async def add_task_on_startup(
        self, callback: Callable | AsyncFunctionT | None = None, *args, **kwargs
    ) -> None:
        """Adds tasks to be run on startup.

        :param callback: The function or coroutine to be executed.
        :param args: Positional arguments to pass to the callback.
        :param kwargs: Keyword arguments to pass to the callback.
        """
        # Add the task to the queue for later execution
        if callback:
            self._queue.put_nowait((callback, args, kwargs))
        else:
            self._queue.put_nowait(callback)
        print("TaskScheduler: Task added.")

    async def run(self) -> None:
        """Starts task scheduler in a non-blocking loop."""
        # Get the current running event loop
        self.__loop = asyncio.get_running_loop()
        # Set a custom task factory to run coroutines eagerly
        self.__loop.set_task_factory(asyncio.eager_task_factory)
        # Run the _run_task coroutine in a separate thread to avoid blocking
        # asyncio.run_coroutine_threadsafe(self._run_task(), self.__loop)
        await self._run_task()
        print("TaskScheduler: Waiting for tasks to be added..")

    async def _run_task(self) -> None:
        """Executes scheduled tasks.

        Determines if they are coroutines or synchronous
        and running them accordingly.
        """
        awaitable_tasks = []
        # Continuously fetch tasks from the queue
        while True:
            item = await self._queue.get()
            self._queue.task_done()
            if not item:
                break
            # Add the task to the internal list for execution
            self.__tasks += [item]

        # Wait for all tasks in the queue to be processed
        await self._queue.join()
        print("TaskScheduler: all tasks added. running..")

        # Execute tasks from the internal list
        while self.__tasks and self.__loop:
            for callback, args, kwargs in self.__tasks:
                if asyncio.iscoroutinefunction(callback):
                    # Schedule coroutine tasks on the event loop
                    awaitable_tasks += [
                        self.__loop.create_task(callback(*args, **kwargs))
                    ]
                else:
                    # Use ThreadPoolExecutor for synchronous tasks
                    self.__thread_exc = futures.ThreadPoolExecutor()
                    awaitable_tasks += [
                        self.__loop.run_in_executor(
                            self.__thread_exc, lambda: callback(*args, **kwargs)
                        )
                    ]
            print("TaskScheduler: Running background tasks")
            # Run all tasks concurrently and wait for them to complete
            await asyncio.gather(*awaitable_tasks)
            # Sleep for a while before checking for new tasks
            await asyncio.sleep(5)
            # Clear the list of awaitable tasks
            awaitable_tasks.clear()

    def on_shutdown(self) -> None:
        """
        Shuts down the task scheduler, cancelling any remaining tasks.
        """
        # Clear the list of tasks
        self.__tasks.clear()
        if self.__thread_exc:
            print("TaskScheduler: shutting down thread")
            # Shutdown the ThreadPoolExecutor
            self.__thread_exc.shutdown(cancel_futures=True)
        print("TaskScheduler: shutdown")


task_scheduler = TaskScheduler()


async def start_task_scheduler() -> None:
    asyncio.create_task(task_scheduler.run())


def stop_task_scheduler() -> None:
    task_scheduler.on_shutdown()
