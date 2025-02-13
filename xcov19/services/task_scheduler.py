from typing import Dict
import concurrent.futures as futures
import asyncio
from typing import List
from xcov19.services.event_registry import EventService


# TODO: change prints to logs agnostic to backend logger
class TaskScheduler:
    """
    TaskScheduler is responsible for managing and executing scheduled tasks.

    Attributes:
        __thread_exc (futures.ThreadPoolExecutor | None): Executor for running synchronous tasks in separate threads.
        __loop (asyncio.AbstractEventLoop | None): Event loop for running asynchronous tasks.
        _queue (asyncio.Queue): Thread-safe queue for storing tasks to be executed.
        __tasks (List[Awaitable]): List to store tasks (callback, args, kwargs) to be executed.
        __event_handlers (Dict[str, EventService]): Mapping of event names to their handlers.
        _is_running (bool): Flag indicating if the scheduler is running.
    """

    def __init__(self, /, event_handlers: Dict[str, EventService], maxsize=0) -> None:
        """
        Initializes the TaskScheduler.

        Args:
            event_handlers (Dict[str, EventService]): A mapping of event names to their handlers.
            maxsize (int, optional): Maximum size of the task queue. Defaults to 0 (unlimited).
        """
        # ThreadPoolExecutor for running synchronous tasks in separate threads
        self.__thread_exc: futures.ThreadPoolExecutor | None = None
        # Event loop for running asynchronous tasks
        self.__loop: asyncio.AbstractEventLoop | None = None
        # Thread-safe queue for storing tasks to be executed
        self._task_queue = asyncio.Queue(maxsize=maxsize)
        # List to store tasks (callback, args, kwargs) to be executed.
        self.__tasks: List[asyncio.Task | asyncio.Future] = []
        self.__threadsafe_future: futures.Future | None = None
        self.__event_handlers = event_handlers
        self._is_running = True

    def add_task(self, event_name: str, *args, **kwargs) -> None:
        """
        Adds a new task to the queue for execution.

        Args:
            event_name (str): The name of the event to execute.
            *args: Positional arguments for the event handler.
            **kwargs: Keyword arguments for the event handler.
        """
        # Add the task to the queue for later execution as per queue.
        event_service: EventService = self.__event_handlers["event_name"]
        self._task_queue.put_nowait((event_service.callback, args, kwargs))
        print(f"TaskScheduler: Task added {event_name}.")

    async def run(self) -> None:
        """
        Starts the task scheduler in a non-blocking loop.

        - Initializes the event loop.
        - Sets a custom task factory to run coroutines eagerly.
        - Starts the task execution coroutines.
        """
        # Get the current running event loop
        self.__loop = asyncio.get_running_loop()
        # Set a custom task factory to run coroutines eagerly
        self.__loop.set_task_factory(asyncio.eager_task_factory)
        self.__threadsafe_future = asyncio.run_coroutine_threadsafe(
            self._run(), self.__loop
        )
        print("TaskScheduler: Running thread-safe coroutines")

    # async def _execute_tasks(self) -> None:
    #     """
    #     Executes the scheduled tasks concurrently.

    #     Continuously runs in the background, executing tasks as they are added.
    #     """
    #     while self._is_running:
    #         if self.__tasks:
    #             print("TaskScheduler: Running background tasks")
    #             # Run all tasks concurrently and wait for them to complete
    #             await asyncio.gather(*self.__tasks)
    #             self.__tasks.clear()

    async def _run(self) -> None:
        """
        Main loop that processes tasks from the queue.

        - Fetches tasks from the queue.
        - Determines if tasks are asynchronous or synchronous.
        - Schedules tasks for execution accordingly.
        """
        assert self.__loop

        def future_done_callback(future: asyncio.Future | asyncio.Task) -> None:
            if future in self.__tasks:
                self.__tasks.remove(future)
            asyncio.gather(*self.__tasks, return_exceptions=True)

        print("TaskScheduler: Waiting for items in task queue.")
        while item := await self._task_queue.get():
            # TODO: Upon failure, add back to queue.
            # task_done only when successful. Could be retry logic.
            self._task_queue.task_done()
            callback, args, kwargs = item
            # Continuously fetch tasks from the queue
            if asyncio.iscoroutinefunction(callback):
                # Schedule coroutine tasks on the event loop
                task: asyncio.Task = self.__loop.create_task(callback(*args, **kwargs))
                self.__tasks += [task]
                task.add_done_callback(future_done_callback)
            else:
                # Use ThreadPoolExecutor for synchronous tasks
                self.__thread_exc = futures.ThreadPoolExecutor()
                future = self.__loop.run_in_executor(
                    self.__thread_exc, lambda: callback(*args, **kwargs)
                )
                self.__tasks += [future]
                future.add_done_callback(future_done_callback)
            print("TaskScheduler: Added callback from queue to task.")
        self._task_queue.task_done()
        print("loop exited.")

    async def on_shutdown(self) -> None:
        """
        Shuts down the task scheduler.

        - Clears the task queue.
        - Clears remaining tasks.
        - Shuts down the ThreadPoolExecutor if it exists.
        """
        # Clear the list of tasks
        print("TaskScheduler: shutting down..")
        self._running = False
        print("shutting down synchronous and threadsafe tasks.")
        self._task_queue.put_nowait(None)
        await self._task_queue.join()
        if self.__thread_exc:
            print("TaskScheduler: shutting down thread")
            # Shutdown the ThreadPoolExecutor
            self.__thread_exc.shutdown(cancel_futures=True)
        if self.__threadsafe_future and not self.__threadsafe_future.done():
            self.__threadsafe_future.cancel()
        print("shutting down asynchronous and background tasks.")
        if self.__tasks:
            for awaitables in self.__tasks:
                awaitables.cancel()
        asyncio.gather(*self.__tasks, return_exceptions=True)
        print("TaskScheduler: shutdown")
