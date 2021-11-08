from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel


class ImageConfig(BaseModel):
    name: str
    includes: Optional[List[str]] = None
    excludes: Optional[List[str]] = None
    setup: Optional[str] = None
    entrypoint: Optional[List[str]] = None


class InstanceConfig(BaseModel):
    type: str
    count: int = 1


class TrainingConfig(BaseModel):
    instance: InstanceConfig
    execution_role: str


class InferenceConfig(BaseModel):
    instance: InstanceConfig
    endpoint_name: str


class Config(BaseModel):
    handler: str
    artifact_path: str
    image: ImageConfig
    training: TrainingConfig
    inference: InferenceConfig
    dataset_path: Optional[str] = None
    hyperparameter_path: Optional[str] = None

    @classmethod
    def load_yaml(cls, path: Path) -> "Config":
        with path.open() as yamlfile:
            config_dict = yaml.safe_load(yamlfile)
        return cls.parse_obj(config_dict)
