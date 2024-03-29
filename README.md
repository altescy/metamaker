metamaker
=========

[![Actions Status](https://github.com/altescy/metamaker/workflows/CI/badge.svg)](https://github.com/altescy/metamaker/actions/workflows/main.yaml)
[![License](https://img.shields.io/github/license/altescy/metamaker)](https://github.com/altescy/metamaker/blob/master/LICENSE)
[![Python version](https://img.shields.io/pypi/pyversions/metamaker)](https://github.com/altescy/metamaker)
[![pypi version](https://img.shields.io/pypi/v/metamaker)](https://pypi.org/project/metamaker/)

Simple command line tool to train and deploy your machine learning models with AWS SageMaker

## Features

metamaker enables you to:

- Build a docker image for training and inference with [poetry](https://python-poetry.org/) and [FastAPI](https://fastapi.tiangolo.com/)
- Train your own machine learning model with SageMaker
- Deploy inference endpoint with SageMaker

## Usage

1. Create poetry project and install metamaker

```
❯ poetry new your_module
❯ cd your_module
❯ poetry add metamaker
```

2. Define scripts for traning and inference in `main.py`

```main.py
from pathlib import Path
from typing import Any, Dict

from metamaker import MetaMaker

# Import your model, and input/output data classs:
#
#   Model  ... machine learning model class you want to use
#   Input  ... input data class for inference
#   Output ... ouput data class for inference
#
# Note that the Input and Output are used as type hints to
# create API endpoint with FastAPI like below:
#
#   @fastapi_app.post("/invocations")
#   def predict(data: Input) -> Output:
#       ...
from your_module import Model, Input, Output

app = MetaMaker[Model, Input, Output]()

@app.trainer
def train(
    dataset_path: Path,
    artifact_path: Path,
    hyperparameters: Dict[str, Any],
) -> None:
    model = Model(**hyperparameters)
    model.train(dataset_path / "train.csv")
    model.save(artifact_path / "model.tar.gz")

@app.loader
def load(artifact_path: Path) -> Model:
    return Model.load(artifact_path / "model.tar.gz")

@app.predictor
def predict(model: Model, data: Input) -> Output:
    return model.predict(data)
```

3. Write metamaker configs in `metamaker.yaml`

```metamaker.yaml
# Specify metamaker handler like: `path.to.module:app_name`
handler: main:app

# dataset_path and artifact_path should be directories and end with '/'
dataset_path: s3://your-bucket/path/to/dataset/
artifact_path: s3://your-bucket/path/to/artifacts/

hyperparameter_path: ./hparams.yaml

image:
  name: metamaker
  includes:
    - your_module/
    - main.py
  excludes:
    - __pycache__/
    - '*.py[cod]'

training:
  execution_role: arn:aws:iam::xxxxxxxxxxxx:role/SageMakerExecutionRole
  instance:
    type: ml.m5.large
    count: 1

inference:
  endpoint_name: your_endpoint
  instance:
    type: ml.t2.meduim
    count: 1
```

4. Build docker image and push to ECR

```
metamaker build --deploy .
```

5. Train your model with SageMaker and deploy endpoint

```
metamaker sagemaker train --deploy
```
