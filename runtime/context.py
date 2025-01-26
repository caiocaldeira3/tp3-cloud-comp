import dataclasses as dc
from datetime import datetime
from typing import Any


@dc.dataclass(kw_only=True)
class Context:
    host: str
    port: int
    input_key: str
    output_key: str
    function_getmtime: datetime
    last_execution: datetime | None
    env: dict[str, Any]
