"""
This module sets up the GraphQL application and explicitly schedules startup services.

The `on_startup` list includes functions that need to be executed when the application starts.
Explicitly including `task_scheduler.run` ensures that all scheduled tasks are initialized
and run as intended, providing a clear entry point for task management.
"""

import os
import strawberry
from strawberry.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route
from xcov19.app.graphql.resolvers import Query, Mutation
from xcov19.services.queue import diagnosis_queue
from xcov19.services.startup_services import STARTUP_SERVICE_LIST
from xcov19.services.task_scheduler import (
    task_scheduler,
    start_task_scheduler,
    stop_task_scheduler,
)


SCHEDULER_DELAY = 5
DEBUG = bool(os.getenv("DEBUG", True))


async def schedule_startup_services() -> None:
    """Schedule all tasks needed before booting server."""

    # Schedule all startup services in the scheduler
    for startup_service in STARTUP_SERVICE_LIST:
        # Run the scheduler in a separate thread to prevent blocking
        await task_scheduler.add_task_on_startup(
            startup_service.callback,
            *startup_service.args,
            **startup_service.kwargs,
        )

    # Ensure the task scheduler adds None callback to break out of queue
    # See task_scheduler.py::TaskScheduler._run_task
    await task_scheduler.add_task_on_startup()


schema = strawberry.Schema(query=Query, mutation=Mutation)

gql_app = GraphQL(
    schema,
    graphiql=True,
    debug=DEBUG,
)

app = Starlette(
    debug=DEBUG,
    routes=[Route("/graphql", gql_app)],
    on_startup=[
        # Schedule all services that don't require explicit task scheduler call.
        schedule_startup_services,
        # Task scheduler execution is explicit to ensure scheduled tasks run decoupled.
        start_task_scheduler,
        lambda: print("on startup ran"),
    ],
    on_shutdown=[
        diagnosis_queue.clear,
        stop_task_scheduler,
        lambda: print("on shutdown ran"),
    ],
)
