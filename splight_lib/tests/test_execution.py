import os
import time
from pathlib import Path

import pytest

from splight_lib.execution import ExecutionClient, Popen, Task, Thread


@pytest.fixture
def base_dir():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sleep_time():
    return 0.25


@pytest.fixture
def python_path():
    import subprocess

    python_path = subprocess.check_output("which python", shell=True).strip()
    python_path = python_path.decode("utf-8")
    return python_path


def test_thread_healthcheck_ok(sleep_time) -> None:
    def function_ok() -> None:
        pass

    client = ExecutionClient()
    client.start(Thread(function_ok))
    time.sleep(sleep_time)
    is_alive, status = client.healthcheck()
    assert not is_alive
    assert status == "Succeeded"


def test_thread_healthcheck_fail(sleep_time) -> None:
    def function_nok() -> None:
        raise Exception("Test exception")

    client = ExecutionClient()
    client.start(Thread(function_nok))
    time.sleep(sleep_time)
    exc = client.get_last_exception()
    assert exc is not None
    client.terminate_all()


# TODO: Support for processes in execution client
# def test_process_healthcheck_ok(base_dir, sleep_time, python_path) -> None:
#     client = ExecutionClient()
#     file_path = os.path.join(base_dir, "tests/FakeProc.py")
#     client.start(Popen([python_path, file_path, "exit_ok"]))
#     time.sleep(sleep_time)
#     assert client.healthcheck()[0]


# def test_process_healthcheck_fail(base_dir, sleep_time, python_path) -> None:
#     client = ExecutionClient()
#     file_path = os.path.join(base_dir, "tests/FakeProc.py")
#     client.start(Popen([python_path, file_path, "exit_fail"]))
#     time.sleep(sleep_time)
#     exc = client.get_last_exception()
#     assert exc is not None


def test_terminate_all(base_dir, sleep_time, python_path) -> None:
    client = ExecutionClient()
    file_path = os.path.join(base_dir, "tests/FakeProc.py")
    client.start(Popen([python_path, file_path, "run_forever"]))
    time.sleep(sleep_time)
    assert client.healthcheck()[0]

    client.terminate_all()
    time.sleep(sleep_time)
    assert not client.processes[0].is_alive()


def test_scheduled_task() -> None:
    executions = []

    def function_to_schedule(arg1, arg2) -> None:
        executions.append(("function_to_schedule", arg1, arg2))

    client = ExecutionClient()
    task = Task(
        handler=function_to_schedule,
        args=("arg1", 2),
        period=5,  # 5seconds
        hash="WTF",
    )
    assert len(executions) == 0
    # Start task
    client.start(task)

    # Check 1 more execution in a period after start
    prev_count = len(executions)
    time.sleep(4.8)
    assert len(executions) == prev_count + 1
    assert executions[-1] == ("function_to_schedule", "arg1", 2)

    # Stop task
    client.stop(task)
    client._scheduler.stop()
    time.sleep(0.5)

    # Check no more executions after stop
    prev_count = len(executions)
    time.sleep(3)
    assert len(executions) == prev_count
