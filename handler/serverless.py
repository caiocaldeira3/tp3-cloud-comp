from datetime import datetime, timedelta
import numpy as np

from typing import Any, Final

CPU_IDX_OFFSET: Final = len("cpu_percent-")

def add_cpu_metrics_to_env (
    cpu_key: str, cpu_percent: float, timestamp: datetime, env: dict[str, Any]
) -> None:
    cpu_idx = cpu_key[CPU_IDX_OFFSET:]
    cpu_metric = f"avg-util-cpu{cpu_idx}-60s"

    if cpu_metric not in env:
        env[cpu_metric] = []

    env[cpu_metric].append({
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "cpu_util-percent": cpu_percent
    })

def cleanup_cpu_metrics (env: dict[str, Any], timestamp: datetime) -> None:
    for key in list(env.keys()):
        if not key.startswith("avg-util-cpu"):
            continue

        cpu_metric = env[key]
        while len(cpu_metric) > 0:
            first_timestamp = datetime.strptime(cpu_metric[0]["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if timestamp - first_timestamp < timedelta(seconds=60):
                break

            cpu_metric.pop(0)

        if len(cpu_metric) == 0:
            raise ValueError(f"Empty CPU metric: {key}")

def handler (input: dict[str, Any], context: object) -> dict[str, Any]:
    timestamp = datetime.strptime(input["timestamp"], "%Y-%m-%d %H:%M:%S.%f")

    sent_bytes = input["net_io_counters_eth0-bytes_sent"]
    recv_bytes = input["net_io_counters_eth0-bytes_recv"]

    cached_memory = input["virtual_memory-cached"]
    buffer_memory = input["virtual_memory-buffers"]
    total_memory = input["virtual_memory-total"]

    persistent_env: dict[str, Any] = context.env

    percent_network_egress = (
        sent_bytes / (sent_bytes + recv_bytes)
        if sent_bytes + recv_bytes > 0 else 0
    )
    percent_memory_cached = (
        (cached_memory + buffer_memory) / total_memory
        if total_memory > 0 else 0
    )

    for key in input:
        if not key.startswith("cpu_percent-"):
            continue

        add_cpu_metrics_to_env(key, input[key], timestamp, persistent_env)

    cleanup_cpu_metrics(persistent_env, timestamp)

    moving_average_results = {
        key: np.fromiter(
            map(lambda obj: obj["cpu_util-percent"], persistent_env[key]), dtype=np.float64
        ).mean()
        for key in persistent_env
        if key.startswith("avg-util-cpu")
    }

    return {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "percent-network-egress": percent_network_egress,
        "percent-memory-caching-content": percent_memory_cached,
        **moving_average_results
    }
