from unittest import TestCase
from splight_lib.execution import ExecutionClient, Task, Thread, Popen
from pathlib import Path
import time
import os


class TestExecutionClient(TestCase):
    def setUp(self) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sleep_time = 0.25
        self.executions = []
        return super().setUp()

    @staticmethod
    def function_ok() -> None:
        pass

    @staticmethod
    def function_nok() -> None:
        raise Exception('Test exception')

    def function_to_schedule(self, arg1, arg2) -> None:
        self.executions.append(('function_to_schedule', arg1, arg2))

    def test_thread_healthcheck_ok(self) -> None:
        client = ExecutionClient()
        client.start(Thread(self.function_ok))
        time.sleep(self.sleep_time)
        self.assertTrue(client.healthcheck())

    def test_thread_healthcheck_fail(self) -> None:
        client = ExecutionClient()
        client.start(Thread(self.function_nok))
        time.sleep(self.sleep_time)
        self.assertFalse(client.healthcheck())

    def test_process_healthcheck_ok(self) -> None:
        client = ExecutionClient()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        client.start(Popen(["python", file_path, 'exit_ok']))
        time.sleep(self.sleep_time)
        self.assertTrue(client.healthcheck())

    def test_process_healthcheck_fail(self) -> None:
        client = ExecutionClient()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        client.start(Popen(["python", file_path, 'exit_fail']))
        time.sleep(self.sleep_time)
        self.assertFalse(client.healthcheck())

    def test_terminate_all(self) -> None:
        client = ExecutionClient()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        client.start(Popen(["python", file_path, 'run_forever']))
        time.sleep(self.sleep_time)
        self.assertTrue(client.healthcheck())
        client.terminate_all()
        time.sleep(self.sleep_time)
        self.assertFalse(client.processes[0].is_alive())

    def test_scheduled_task(self) -> None:
        client = ExecutionClient()
        task = Task(handler=self.function_to_schedule, args=("arg1", 2), period=1, hash="WTF")
        self.assertEqual(len(self.executions), 0)
        # Start task
        client.start(task)

        # Check 1 more execution in a period after start
        prev_count = len(self.executions)
        time.sleep(0.99)
        self.assertEqual(len(self.executions), prev_count + 1)
        self.assertEqual(self.executions[-1], ("function_to_schedule", "arg1", 2))

        # Stop task
        client.stop(task)
        client._scheduler.stop()
        time.sleep(0.5)

        # Check no more executions after stop
        prev_count = len(self.executions)
        time.sleep(3)
        self.assertEqual(len(self.executions), prev_count)
