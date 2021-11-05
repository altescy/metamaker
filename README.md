# metamaker

```metamaker.yaml
metamaker:
  handler: your_module:YourHandler
  dataset_path: s3://your-bucket/path/to/dataset/
  artifact_path: s3://your-bucket/path/to/artifacts/

image:
  name: metamaker
  dependencies:
    - your_module/
    - your_script.py

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
