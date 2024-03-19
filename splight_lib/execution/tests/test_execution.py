from time import sleep

from splight_lib.execution.engine import EngineStatus, ExecutionEngine
from splight_lib.execution.task import PeriodicTask


def test_task_with_error():
    def task_function():
        sleep(1)
        print("This is a function")
        raise ValueError()

    task = PeriodicTask(target=task_function, period=1)

    engine = ExecutionEngine()
    assert engine.state == EngineStatus.UNKNOWN

    engine.add_task(task, in_background=False, exit_on_fail=True)

    engine.start()
    assert engine.state == EngineStatus.FAILED


def test_task_with_error_on_background():
    def task_function():
        sleep(1)
        print("This is a function")
        raise ValueError()

    task = PeriodicTask(target=task_function, period=1)

    engine = ExecutionEngine()
    assert engine.state == EngineStatus.UNKNOWN

    engine.add_task(task, in_background=True, exit_on_fail=True)

    engine.start()
    assert engine.state == EngineStatus.RUNNING

    sleep(2)
    assert engine.state == EngineStatus.FAILED
