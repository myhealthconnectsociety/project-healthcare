from typing import Callable, Awaitable
import os

from blacksheep import Application, Request, Response, bad_request

from xcov19.app.settings import FromOriginMatchHeader


def configure_middleware(app: Application, *middlewares):
    app.middlewares.extend(middlewares)


async def origin_header_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Allow open endpoints without validation
    if request.path.startswith("/docs") or request.path.startswith("/openapi"):
        return await handler(request)

    # Get expected secret from environment
    expected_secret = os.getenv("FROM_ORIGIN_HEADER_SECRET", "default-dev-secret").encode()

    # Get actual header from request
    actual_header = request.headers.get(FromOriginMatchHeader.name.encode())

    # Compare
    if actual_header == (expected_secret,):
        return await handler(request)
    else:
        return bad_request("Invalid origin match header value provided.")
