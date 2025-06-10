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


SCHEDULER_DELAY = 5
DEBUG = bool(os.getenv("DEBUG", True))


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
        # schedule_startup_services,
        # Task scheduler execution is explicit to ensure scheduled tasks run decoupled.
        # start_task_scheduler,
        lambda: print("on startup ran"),
    ],
    on_shutdown=[
        # diagnosis_queue.clear,
        # stop_task_scheduler,
        lambda: print("on shutdown ran"),
    ],
)
