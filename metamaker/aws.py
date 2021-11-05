import os
from typing import Optional

import boto3


def get_profile() -> Optional[str]:
    return os.environ.get("AWS_PROFILE")


def get_session() -> boto3.Session:
    profile = get_profile()
    if profile:
        return boto3.Session(profile_name=profile)
    else:
        return boto3.Session()


def get_account_id(session: boto3.Session) -> str:
    return str(session.client("sts").get_caller_identity()["Account"])


def get_region(session: boto3.Session) -> str:
    return session.region_name


def get_image_uri(
    session: boto3.Session,
    name: str,
    tag: Optional[str] = None,
    account_id: Optional[str] = None,
    region: Optional[str] = None,
) -> str:
    account_id = account_id or get_account_id(session=session)
    region = region or get_region(session=session)
    tag = tag or "latest"
    return f"{account_id}.dkr.ecr.{region}.amazonaws.com/{name}:{tag}"
