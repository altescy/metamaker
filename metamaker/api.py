import typing
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
    app.state.model = handler.load(artifact_path)

    async def ping() -> str:
        return "pong"

    async def invocations(data, request: fastapi.Request):  # type: ignore
        handler = request.app.state.handler
        model = request.app.state.model
        return handler.predict(model, data)

    handler_annotation = getattr(handler, "__orig_class__")  # noqa: B009
    _model_annotation, input_annotation, output_annotation = typing.get_args(handler_annotation)

    invocations.__annotations__["data"] = input_annotation
    invocations.__annotations__["return"] = output_annotation

    app.get("/ping")(ping)
    app.post("/invocations")(invocations)

    return app
