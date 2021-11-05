from pathlib import Path
from typing import TypeVar

import fastapi

from metamaker.metamaker import MetaMaker

Model = TypeVar("Model")
Input = TypeVar("Input")
Output = TypeVar("Output")


def create(
    handler: MetaMaker[Model, Input, Output],
    artifact_path: Path,
) -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app.state.handler = handler
    app.state.model = handler.loader(artifact_path)

    def ping() -> str:
        return "pong"

    def invocations(data, request: fastapi.Request):  # type: ignore
        handler = request.app.state.handler
        model = request.app.state.model
        return handler.predict(model, data)

    invocations.__annotations__["data"] = handler.predictor.__annotations__["data"]
    invocations.__annotations__["return"] = handler.predictor.__annotations__["return"]

    app.get("/ping")(ping)
    app.post("/invocations")(invocations)

    return app
