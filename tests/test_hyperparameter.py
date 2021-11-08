from metamaker import hyperparameter


def test_hyperparameter_can_serialize() -> None:
    inputs = {"a": {"b": 1, "c": {"d": [1, 2, 3]}}, "e": 2.718, "f": "foo"}
    output = hyperparameter.serialize(inputs)
    desired = {"a.b": "1", "a.c.d": "[1, 2, 3]", "e": "2.718", "f": '"foo"', "%%serialized%%": "true"}

    assert output == desired


def test_hyperparameter_can_deserialize() -> None:
    inputs = {"a.b": "1", "a.c.d": "[1, 2, 3]", "e": "2.718", "f": '"foo"', "%%serialized%%": "true"}
    output = hyperparameter.deserialize(inputs)
    desired = {"a": {"b": 1, "c": {"d": [1, 2, 3]}}, "e": 2.718, "f": "foo"}

    assert output == desired
