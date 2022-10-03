from typing import Callable, List, Dict
from functools import wraps
import inspect


class PreHookMixin:
    _original_signature = {}

    def add_pre_hook(self, function, hook):
        setattr(self, function, self._add_pre_hook(getattr(self, function), hook))

    def _add_pre_hook(self, func, hook):
        if func.__name__ not in self._original_signature:
            self._original_signature[func.__name__] = [
                param
                for param in inspect.getfullargspec(func).args
                if param not in ['self', 'cls', 'args', 'kwargs']
            ]

        @wraps(func)
        def hooked_func(*args, **kwargs):
            kwargs = self._args_to_kwargs(func, *args, **kwargs)
            args, kwargs = hook(**kwargs)
            return func(*args, **kwargs)

        return hooked_func

    def _args_to_kwargs(self, func: Callable, *args, **kwargs) -> Dict:
        if not args:
            return kwargs

        func_params: List = self._original_signature[func.__name__]
        new_kwargs: Dict = dict(zip(func_params, args))
        new_kwargs.update(kwargs)

        return new_kwargs
