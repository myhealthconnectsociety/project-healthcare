from __future__ import annotations
from typing import Protocol, Tuple
import abc
import asyncio
import random
import time
import string

type DiagnosisQueryTuple = Tuple[str, str]


class QueueServiceInterface[T: DiagnosisQueryTuple](Protocol):
    @abc.abstractmethod
    async def enqueue(self, query: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def dequeue(self) -> T | None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def is_full(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(self) -> None:
        raise NotImplementedError


class ThreadSafeQueue(QueueServiceInterface[DiagnosisQueryTuple]):
    def __init__(self, maxsize=0):
        self.__queue = asyncio.Queue(maxsize=maxsize)

    async def _generate_query_id(self) -> str:
        timestamp = int(time.time())
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"{timestamp}-{random_str}"

    async def enqueue(self, query: str) -> str:
        if self.is_full():
            raise OverflowError("Queue is full.")
        query_id = await self._generate_query_id()
        await self.put((query_id, query))
        return query_id

    async def dequeue(self) -> DiagnosisQueryTuple | None:
        if not self.is_empty():
            return await self.get()
        return None

    async def get(self) -> DiagnosisQueryTuple | None:
        try:
            item = self.__queue.get_nowait()
            self.__queue.task_done()
            return item
        except asyncio.QueueEmpty as e:
            print(f"diagnosis queue empty when fetching {e}")
            return None

    async def put(self, item: DiagnosisQueryTuple) -> None:
        try:
            self.__queue.put_nowait(item)
        except asyncio.QueueFull as e:
            print(f"queue is full for immediate use in non-blocking mode {e}")
            raise BufferError(e)

    def is_empty(self) -> bool:
        return self.__queue.empty()

    def is_full(self) -> bool:
        return self.__queue.full()

    async def clear(self) -> None:
        print(f"emptying queue of queries size {self.__queue.qsize()}")
        while not self.is_empty():
            await self.dequeue()


async def store_queue_event(queue_service: QueueServiceInterface[DiagnosisQueryTuple]):
    print("executing store_queue_event")
    if not queue_service.is_empty() and (queue_item := await queue_service.dequeue()):
        # TODO: call external query diagnosis service to evaluate
        # for this query_id the specialties required and store in db
        print(f"stored queue item {queue_item} somewhere far away")


def fetch_queue_result(): ...


diagnosis_queue = ThreadSafeQueue()
