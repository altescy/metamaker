import importlib
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

Model = TypeVar("Model")
Input = TypeVar("Input")
Output = TypeVar("Output")


class MetaMaker(Generic[Model, Input, Output]):
    @classmethod
    def from_path(cls, path: str) -> "MetaMaker[Any, Any, Any]":
        module_name, class_name = path.rsplit(":", 1)
        module = importlib.import_module(module_name)
        handler = getattr(module, class_name)
        assert isinstance(handler, MetaMaker)
        return handler

    def __init__(self) -> None:
        self._trainer: Optional[Callable[[Path, Path, Dict[str, Any]], None]] = None
        self._loader: Optional[Callable[[Path], Model]] = None
        self._predictor: Optional[Callable[[Model, Input], Output]] = None

    @property
    def train(self) -> Callable[[Path, Path, Dict[str, Any]], None]:
        assert self._trainer is not None
        return self._trainer

    @property
    def load(self) -> Callable[[Path], Model]:
        assert self._loader is not None
        return self._loader

    @property
    def predict(self) -> Callable[[Model, Input], Output]:
        assert self._predictor is not None
        return self._predictor

    def trainer(
        self,
        func: Callable[[Path, Path, Dict[str, Any]], None],
    ) -> Callable[[Path, Path, Dict[str, Any]], None]:
        self._trainer = func
        return func

    def loader(
        self,
        func: Callable[[Path], Model],
    ) -> Callable[[Path], Model]:
        self._loader = func
        return func

    def predictor(
        self,
        func: Callable[[Model, Input], Output],
    ) -> Callable[[Model, Input], Output]:
        self._predictor = func
        return func
