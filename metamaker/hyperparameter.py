import copy
import json
from typing import Any, Dict, Optional

SERIALIZEDKEY = "%%serialized%%"
SEPARATOR = "."


def serialize(data: Dict[str, Any]) -> Dict[str, str]:
    ret = _serialize(data)
    ret[SERIALIZEDKEY] = "true"
    return ret


def deserialize(data: Dict[str, Any]) -> Dict[str, Any]:
    if SERIALIZEDKEY not in data:
        return data
    data = copy.deepcopy(data)
    data.pop(SERIALIZEDKEY)
    return _deserialize(data)


def _serialize(data: Dict[str, Any], parent_key: str = "") -> Dict[str, str]:
    ret: Dict[str, str] = {}
    for key, value in data.items():
        if SEPARATOR in key:
            raise ValueError(f"'{SEPARATOR}' is unavailable for key name: {key}")
        if key == SERIALIZEDKEY:
            raise ValueError(f"'{SERIALIZEDKEY}' is unavailable for key name: {key}")
        if isinstance(value, dict):
            ret.update(_serialize(value, key))
        else:
            ret[key] = json.dumps(value)

    if parent_key:
        ret = {f"{parent_key}{SEPARATOR}{key}": value for key, value in ret.items()}

    return ret


def _deserialize(data: Dict[str, str]) -> Dict[str, Any]:

    ret: Dict[str, Any] = {}
    for key, value in data.items():

        top_key: str
        child_key: Optional[str]
        if SEPARATOR in key:
            top_key, child_key = key.split(SEPARATOR, 1)
        else:
            top_key, child_key = key, None

        if child_key is None:
            ret[top_key] = value
        else:
            ret[top_key] = ret.get(top_key, {})
            ret[top_key][child_key] = value

    for top_key, inner in ret.items():
        if isinstance(inner, str):
            inner = json.loads(inner)
        elif isinstance(inner, dict):
            inner = _deserialize(inner)

        ret[top_key] = inner

    return ret
