import os
from xcov19.services.task_scheduler import TaskScheduler
import grpc
import asyncio
from xcov19.services.diagnosis import enqueue_diagnosis, DiagnosisService
from xcov19.services.event_registry import EventRegistry
import concurrent.futures as futures
from xcov19.proto_definitions.diagnosis_service_pb2_grpc import (
    add_DiagnosisServiceServicer_to_server,
)
import signal

CALLBACK_EVENT_HANDLERS = {"enqueue_diagnosis_query": enqueue_diagnosis}


def add_rpc_calls_to_server(rpc_server: grpc.aio.Server, task_scheduler: TaskScheduler):
    """Adds server side services to rpc server."""
    add_DiagnosisServiceServicer_to_server(
        DiagnosisService(task_scheduler_service=task_scheduler), rpc_server
    )


event_registry = EventRegistry(available_handlers=CALLBACK_EVENT_HANDLERS)
event_handlers = event_registry.create_event_registry()
task_scheduler = TaskScheduler(event_handlers=event_handlers)


async def serve():
    shutdown_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _shutdown_signal() -> None:
        shutdown_event.set()
        print(
            "Termination signal on rpc server received. Shutting down task scheduler."
        )
        asyncio.create_task(task_scheduler.on_shutdown())

    for sig_interrupt in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig_interrupt, _shutdown_signal)

    print("Running task scheduler")
    await task_scheduler.run()

    # TODO: refactor to import from common settings
    rpc_address = os.getenv("RPC_ADDR", "localhost:5051")
    # TODO: Add graceful shutdown logic for task scheduler
    with futures.ThreadPoolExecutor() as exc:
        rpc_server = grpc.aio.server(exc)
        add_rpc_calls_to_server(rpc_server, task_scheduler)
        rpc_server.add_insecure_port(rpc_address)
        await rpc_server.start()
        print("rpc server started")
        try:
            await shutdown_event.wait()
            await rpc_server.wait_for_termination(timeout=5)
        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            print(f"Gracefully shutting down: {e}")
        finally:
            await rpc_server.stop(grace=5)


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
