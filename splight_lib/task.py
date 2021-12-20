from typing import List, Callable, Union, Dict, Tuple
from threading import Thread as DefaultThread
from subprocess import Popen as DefaultPopen
from functools import wraps
import atexit
import sys


class Empty(object):
    pass


class Thread(DefaultThread):
    def __init__(self, target, *args, **kwargs) -> None:
        target = self.store_result(target)
        self.result = Empty()
        super().__init__(target=target, *args, **kwargs)

    def store_result(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.result = func(*args, **kwargs)
            return self.result
        return wrapper

    def exit_ok(self) -> bool:
        return not isinstance(self.result, Empty)

    def kill(self) -> None:
        pass

    def terminate(self) -> None:
        pass


class Popen(DefaultPopen):
    def is_alive(self) -> bool:
        return self.poll() is None

    def exit_ok(self) -> bool:
        return self.poll() == 0


class TaskManager:
    def __init__(self):
        self.tasks: List[Union[Thread, Popen]] = []
        self._register_exit_functions()

    def _register_exit_functions(self) -> None:
        excepthook = sys.excepthook

        def wrap_excepthook(type, value, traceback):
            self.terminate_all()
            excepthook(type, value, traceback)

        atexit.register(self.terminate_all)
        sys.excepthook = wrap_excepthook

    def terminate_all(self) -> None:
        for p in self.tasks:
            p.terminate()

    def start_process(self, target: str, args: List[str] = []):
        p: Popen = Popen([target] + args)
        self.tasks.append(p)

    def start_thread(self, target: Callable, args: Tuple = (), kwargs: Dict = {}):
        t: Thread = Thread(target=target, args=args, kwargs=kwargs)
        self.tasks.append(t)
        t.start()

    def healthcheck(self):
        return all([p.is_alive() or p.exit_ok() for p in self.tasks])
