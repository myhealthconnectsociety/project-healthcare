"""
This module sets up the GraphQL application and explicitly schedules startup services.

The `on_startup` list includes functions that need to be executed when the application starts.
Explicitly including `task_scheduler.run` ensures that all scheduled tasks are initialized
and run as intended, providing a clear entry point for task management.
"""

import os
import asyncio
import strawberry
from strawberry.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route
from xcov19.app.graphql.resolvers import Mutation, Query
from xcov19.services.queue import diagnosis_queue
from xcov19.services.startup_services import STARTUP_SERVICE_LIST
from xcov19.services.task_scheduler import task_scheduler, scheduler


SCHEDULER_DELAY = 5
DEBUG = os.getenv("DEBUG", True)


def schedule_startup_services() -> None:
    """Run all tasks needed before booting server."""
    # Schedule all startup services in the scheduler
    for priority, startup_service in enumerate(STARTUP_SERVICE_LIST, start=1):
        scheduler.enter(
            SCHEDULER_DELAY,
            priority,
            task_scheduler.add_task_on_startup,
            (startup_service.callback, *startup_service.args),
            kwargs=startup_service.kwargs,
        )
    # Ensure the task scheduler adds None callback to break out of queue
    # See task_scheduler.py::TaskScheduler._run_task
    scheduler.enter(
        SCHEDULER_DELAY, len(STARTUP_SERVICE_LIST), task_scheduler.add_task_on_startup
    )
    # Get the current event loop
    loop = asyncio.get_running_loop()
    # Run the scheduler in a separate thread to prevent blocking
    loop.run_in_executor(None, lambda: scheduler.run(blocking=True))


schema = strawberry.Schema(query=Query, mutation=Mutation)

gql_app = GraphQL(schema, graphiql=True)

app = Starlette(
    debug=bool(DEBUG),
    routes=[Route("/graphql", gql_app)],
    on_startup=[
        schedule_startup_services,
        # Task scheduler execution is explicit to ensure scheduled tasks run
        task_scheduler.run,
        lambda: print("on startup ran"),
    ],
    on_shutdown=[
        lambda: [scheduler.cancel(event) for event in scheduler.queue],
        diagnosis_queue.clear,
        task_scheduler.on_shutdown,
        lambda: print("on shutdown ran"),
    ],
)
