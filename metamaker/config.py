from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel


class MetaMakerConfig(BaseModel):
    handler: str
    dataset_path: str
    artifact_path: str


class ImageConfig(BaseModel):
    name: str
    dockerfile: Optional[str] = None
    dependencies: Optional[List[str]] = None
    setup: Optional[str] = None
    entrypoint: Optional[List[str]] = None


class EC2Config(BaseModel):
    type: str
    count: int = 1


class TrainingConfig(BaseModel):
    instance: EC2Config
    execution_role: str
    params: Optional[Dict[str, Any]] = None


class InferenceConfig(BaseModel):
    instance: EC2Config
    endpoint_name: str


class Config(BaseModel):
    metamaker: MetaMakerConfig
    image: ImageConfig
    training: TrainingConfig
    inference: InferenceConfig

    @classmethod
    def load_yaml(cls, path: Path) -> "Config":
        with path.open() as yamlfile:
            config_dict = yaml.safe_load(yamlfile)
        return cls.parse_obj(config_dict)
