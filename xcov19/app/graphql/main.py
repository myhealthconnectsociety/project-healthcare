import os
import asyncio
from typing import Any, Callable, Dict, Tuple

import dataclasses
import strawberry
from strawberry.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route
from xcov19.app.graphql.resolvers import Mutation, Query
from xcov19.services.queue import diagnosis_queue, store_queue_event
from xcov19.services.task_scheduler import task_scheduler


SCHEDULER_DELAY = 0
DEBUG = os.getenv("DEBUG", True)


@dataclasses.dataclass(order=True, frozen=True)
class StartupServices:
    callback: Callable
    args: Tuple[Any]
    kwargs: Dict[str, Any]


STARTUP_SERVICE_LIST = [
    StartupServices(
        callback=store_queue_event,
        args=(diagnosis_queue,),
        kwargs={},
    ),
]


def run_startup_services() -> None:
    """Run all tasks needed before booting server."""
    for startup_service in STARTUP_SERVICE_LIST:
        task_scheduler.add_task_on_startup(
            startup_service.callback, *startup_service.args, **startup_service.kwargs
        )
        loop = asyncio.get_running_loop()
        loop.create_task(task_scheduler.run())


schema = strawberry.Schema(query=Query, mutation=Mutation)

gql_app = GraphQL(schema, graphiql=True)

app = Starlette(
    debug=bool(DEBUG),
    routes=[Route("/graphql", gql_app)],
    on_startup=[
        run_startup_services,
        lambda: print("on startup ran"),
    ],
    on_shutdown=[
        diagnosis_queue.clear,
        task_scheduler.on_shutdown,
        lambda: print("on shutdown ran"),
    ],
)
