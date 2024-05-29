import os


def check_first_worker() -> bool:
    """
    returns True if the current execution is under gw0 (first worker)
    """
    return (
        "PYTEST_XDIST_WORKER" not in os.environ
        or os.environ.get("PYTEST_XDIST_WORKER") == "gw0"
    )
