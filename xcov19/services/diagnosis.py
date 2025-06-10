import os
import random
import string
import time
from xcov19.services.task_scheduler import TaskScheduler
from xcov19.proto_definitions.diagnosis_service_pb2_grpc import (
    DiagnosisServiceServicer,
    DiagnosisServiceStub,
)
from xcov19.proto_definitions.diagnosis_service_pb2 import (
    DiagnosisQueryRequest,
    EmptyDiagnosisQueryResponse,
)
import grpc


class DiagnosisService(DiagnosisServiceServicer):
    def __init__(self, task_scheduler_service: TaskScheduler, *args, **kwargs) -> None:
        self._scheduler = task_scheduler_service
        self._event_name = "enqueue_diagnosis_query"
        super().__init__(*args, **kwargs)

    def EnqueueDiagnosisQuery(
        self, request: DiagnosisQueryRequest, context
    ) -> EmptyDiagnosisQueryResponse:
        query_id, query = request.query_id, request.query
        self._scheduler.add_task(self._event_name, query_id, query)
        print("EnqueueDiagnosisQuery: added task")
        context.set_code(grpc.StatusCode.OK)
        return EmptyDiagnosisQueryResponse()


class DiagnosisQueryClient:
    @classmethod
    async def enqueue(cls, query: str) -> str:
        # TODO: refactor to import from common settings
        rpc_address = os.getenv("RPC_ADDR", "localhost:5051")
        query_id = cls._generate_query_id()
        # Call grpc diagnosis query request with query and query_id
        async with grpc.aio.insecure_channel(rpc_address) as channel:
            stub = DiagnosisServiceStub(channel)
            await stub.EnqueueDiagnosisQuery(
                DiagnosisQueryRequest(query_id=query_id, query=query)
            )
        return query_id

    @staticmethod
    def _generate_query_id() -> str:
        timestamp = time.time()
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"{timestamp}-{random_str}"


# TODO: convert print to log and plug to logging backend
async def enqueue_diagnosis(query: str) -> str:
    try:
        return await DiagnosisQueryClient.enqueue(query)
    # TODO: change exception handling
    except (BufferError, OverflowError) as e:
        print("queue error")
        raise (e)
