from django.test import TestCase
from splight_lib.task import TaskManager
from pathlib import Path
import time
import os


class TestTaskManager(TestCase):
    def setUp(self) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sleep_time = 0.25
        return super().setUp()

    def aux_exit_ok(self) -> None:
        pass

    def aux_exit_fail(self) -> None:
        raise Exception('Test exception')

    def test_thread_exit_ok(self) -> None:
        task_manager = TaskManager()
        task_manager.start_thread(self.aux_exit_ok)
        time.sleep(self.sleep_time)
        self.assertFalse(task_manager.tasks[0].is_alive())
        self.assertTrue(task_manager.tasks[0].exit_ok())
        self.assertTrue(task_manager.healthcheck())

    def test_thread_exit_fail(self) -> None:
        task_manager = TaskManager()
        task_manager.start_thread(self.aux_exit_fail)
        time.sleep(self.sleep_time)
        self.assertFalse(task_manager.tasks[0].is_alive())
        self.assertFalse(task_manager.tasks[0].exit_ok())
        self.assertFalse(task_manager.healthcheck())

    def test_process_exit_ok(self) -> None:
        task_manager = TaskManager()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        task_manager.start_process("python", [file_path, 'exit_ok'])
        time.sleep(self.sleep_time)
        self.assertFalse(task_manager.tasks[0].is_alive())
        self.assertTrue(task_manager.tasks[0].exit_ok())
        self.assertTrue(task_manager.healthcheck())

    def test_process_exit_fail(self) -> None:
        task_manager = TaskManager()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        task_manager.start_process("python", [file_path, 'exit_fail'])
        time.sleep(self.sleep_time)
        self.assertFalse(task_manager.tasks[0].is_alive())
        self.assertFalse(task_manager.tasks[0].exit_ok())
        self.assertFalse(task_manager.healthcheck())

    def test_process_run_forever(self) -> None:
        task_manager = TaskManager()
        file_path = os.path.join(self.base_dir, 'tests/FakeProc.py')
        task_manager.start_process("python", [file_path, 'run_forever'])
        time.sleep(self.sleep_time)
        self.assertTrue(task_manager.tasks[0].is_alive())
        self.assertFalse(task_manager.tasks[0].exit_ok())
        self.assertTrue(task_manager.healthcheck())
        task_manager.terminate_all()
        time.sleep(self.sleep_time)
        self.assertFalse(task_manager.tasks[0].is_alive())
