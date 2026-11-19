"""Load non-executable interface and protocol facts packaged with the client."""

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=None)
def load(name: str):
    return json.loads(
        files("korail_py_sdk")
        .joinpath(
            "resources",
            "messages" if name in {"messages", "message-provenance"} else "contracts",
            name + ".json",
        )
        .read_text(encoding="utf-8")
    )
