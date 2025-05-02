from typing import Callable, Awaitable

from blacksheep import Application, Request, Response, bad_request

from xcov19.app.settings import FromOriginMatchHeader, load_settings


def configure_middleware(app: Application, *middlewares):
    app.middlewares.extend(middlewares)


async def origin_header_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]]
) -> Response:
    api_secret = load_settings().api_secret.encode()
    if not FromOriginMatchHeader.name:
        raise ValueError("FromOriginMatchHeader name is not set.")
    if request.path.startswith("/docs") or request.path.startswith("/openapi"):
        return await handler(request)
    match request.headers.get(FromOriginMatchHeader.name.encode()):
        case x if api_secret in x:
            return await handler(request)
        case _:
            return bad_request("Invalid origin match header value provided.")
