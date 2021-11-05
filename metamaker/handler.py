import importlib
from pathlib import Path
from typing import Any, Generic, TypeVar

Model = TypeVar("Model")
Input = TypeVar("Input")
Output = TypeVar("Output")


class Handler(Generic[Model, Input, Output]):
    @classmethod
    def from_path(cls, path: str) -> "Handler[Any, Any, Any]":
        module_name, class_name = path.rsplit(":", 1)
        module = importlib.import_module(module_name)
        subclass = getattr(module, class_name)
        return subclass()  # type: ignore

    def train(self, dataset_path: Path, artifact_path: Path) -> None:
        raise NotImplementedError

    def load(self, artifact_path: Path) -> Model:
        raise NotImplementedError

    def predict(self, model: Model, data: Input) -> Output:
        raise NotImplementedError
