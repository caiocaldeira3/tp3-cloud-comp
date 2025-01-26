import os
import sys
import json
import time
import redis
import base64
import zipfile
import importlib
from typing import Callable, Final
from datetime import datetime

from context import Context

sys.path.append("/opt/")

module_loader = importlib.util.find_spec("usermodule")

import usermodule


ENTRYPOINT_MODULE, ENTRYPOINT_METHOD = (
    ("usermodule", "handler")
    if os.environ.get("ENTRYPOINT", "usermodule.handler") == "usermodule.handler"
    else os.environ["ENTRYPOINT"].rsplit(".", 1)
)

handler_module = usermodule
if os.path.isfile("/opt/modules64") and os.path.getsize("/opt/modules64") > 0:
    with open("/opt/modules64", "r") as encoded_file:
        base64_content = encoded_file.read()

    with open("/opt/modules.zip", "wb") as decoded_file:
        decoded_file.write(base64.b64decode(base64_content))

    with zipfile.ZipFile("/opt/modules.zip", "r") as zip_ref:
        zip_ref.extractall("/opt/")

    sys.path.append("/opt/")

    if ENTRYPOINT_MODULE != "usermodule":
        handler_module = importlib.import_module(ENTRYPOINT_MODULE)

else:
    print("No modules64 found")


redis_client = redis.StrictRedis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    decode_responses=True
)

INTERVAL: Final = float(os.environ["INTERVAL_KEY"])
REDIS_INPUT_KEY: Final = os.environ["REDIS_INPUT_KEY"]
REDIS_OUTPUT_KEY: Final = os.environ["REDIS_OUTPUT_KEY"]

handler_method: Callable
if hasattr(handler_module, ENTRYPOINT_METHOD):
    handler_method = getattr(handler_module, ENTRYPOINT_METHOD)

else:
    raise ValueError(f"Entrypoint method {ENTRYPOINT_MODULE}.{ENTRYPOINT_METHOD} not found")

ctx = Context(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    input_key=REDIS_INPUT_KEY,
    output_key=REDIS_OUTPUT_KEY,
    function_getmtime=datetime.now(),
    last_execution=None,
    env={},
)

while True:
    raw_metrics = redis_client.get(REDIS_INPUT_KEY)
    ctx.last_execution = datetime.now()

    if raw_metrics:
        metrics = json.loads(raw_metrics)

        output = handler_method(metrics, ctx)

        redis_client.set(REDIS_OUTPUT_KEY, json.dumps(output))

        ctx.last_execution = datetime.now()

    time.sleep(INTERVAL)
