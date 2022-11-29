import inspect
from enum import Enum
from typing import Callable, List, Dict
from functools import wraps


class HooksStage(str, Enum):
    BEFORE = "before"
    AFTER = "after"


class HooksMixin:
    _original_signature = {}

    def add_pre_hook(self, function, hook):
        setattr(self, function, self._add_hook(getattr(self, function), hook, HooksStage.BEFORE))

    def add_post_hook(self, function, hook):
        setattr(self, function, self._add_hook(getattr(self, function), hook, HooksStage.AFTER))

    def _add_hook(self, func: Callable, hook, stage: HooksStage = HooksStage.BEFORE):
        func_name = func.__qualname__

        if func_name not in self._original_signature:
            self._original_signature[func_name] = [
                param
                for param in inspect.getfullargspec(func).args
                if param not in ['self', 'cls', 'args', 'kwargs']
            ]

        @wraps(func)
        def pre_hooked_func(*args, **kwargs):
            kwargs = self._args_to_kwargs(func, *args, **kwargs)
            args, kwargs = hook(**kwargs)
            return func(*args, **kwargs)

        @wraps(func)
        def post_hooked_func(*args, **kwargs):
            kwargs = self._args_to_kwargs(func, *args, **kwargs)
            result = func(**kwargs)
            return hook(result)
        return pre_hooked_func if stage == HooksStage.BEFORE else post_hooked_func

    def _args_to_kwargs(self, func: Callable, *args, **kwargs) -> Dict:
        if not args:
            return kwargs
        func_params: List = self._original_signature[func.__qualname__]
        new_kwargs: Dict = dict(zip(func_params, args))
        new_kwargs.update(kwargs)

        return new_kwargs
