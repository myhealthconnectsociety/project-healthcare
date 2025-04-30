from typing import Callable, Awaitable

from blacksheep import Application, Request, Response, bad_request

from xcov19.app.settings import FromOriginMatchHeader, ORIGIN_MATCH_SECRET


def configure_middleware(app: Application, *middlewares):
    app.middlewares.extend(middlewares)


async def origin_header_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Allow open endpoints without validation
    if request.path.startswith("/docs") or request.path.startswith("/openapi"):
        return await handler(request)

    # Use centralized secret value from settings
    expected_secret = ORIGIN_MATCH_SECRET.encode()
    actual_header = request.headers.get(FromOriginMatchHeader.name.encode())

    if actual_header == (expected_secret,):
        return await handler(request)
    else:
        return bad_request("Invalid origin match header value provided.")
