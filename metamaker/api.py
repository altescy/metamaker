from pathlib import Path
from typing import TypeVar

import fastapi

from metamaker.handler import Handler

Model = TypeVar("Model")
Input = TypeVar("Input")
Output = TypeVar("Output")


def create(
    handler: Handler[Model, Input, Output],
    artifact_path: Path,
) -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app.state.handler = handler
    app.state.model = handler.load(artifact_path)

    def ping() -> str:
        return "pong"

    def invocations(data, request: fastapi.Request):  # type: ignore
        handler = request.app.state.handler
        model = request.app.state.model
        return handler.predict(model, data)

    invocations.__annotations__["data"] = handler.predict.__annotations__["data"]
    invocations.__annotations__["return"] = handler.predict.__annotations__["return"]

    app.get("/ping")(ping)
    app.post("/invocations")(invocations)

    return app
