import logging
import time
import uuid

from fastapi import FastAPI, Request

logger = logging.getLogger("taskhub")


def setup_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        logger.info("%s %s %s %.4fs", request.method, request.url.path, response.status_code, process_time)
        return response
