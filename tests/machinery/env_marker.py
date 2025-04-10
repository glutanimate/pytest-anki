import os
from collections import defaultdict
from typing import Dict, Optional

_env_store: Dict[str, Dict[str, Optional[str]]] = defaultdict(dict)


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "env(dict): set environment variables for a specific test"
    )


def pytest_runtest_setup(item):
    marker = item.get_closest_marker("env")
    if marker:
        env_vars = marker.args[0] if marker.args else marker.kwargs
        node_id = item.nodeid

        for key, value in env_vars.items():
            _env_store[node_id][key] = os.environ.get(key)
            os.environ[key] = str(value)


def pytest_runtest_teardown(item):
    marker = item.get_closest_marker("env")
    if marker:
        node_id = item.nodeid
        if node_id in _env_store:
            for key, original_value in _env_store[node_id].items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            del _env_store[node_id]
