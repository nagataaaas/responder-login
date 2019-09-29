from itertools import chain


def method_decorator(decorator):
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            @decorator
            def bound_func(*args2, **kwargs2):
                return func(self, *args2, **kwargs2)

            return bound_func(*args, **kwargs)

        return _wrapper

    return _dec


def class_decorator(decorator, method=("on_get", "on_post", "on_delete", "on_put", "on_head", "on_request"), extra=()):
    def _dec(cls):
        for attr in chain(method, extra):
            if hasattr(cls, attr) and callable(getattr(cls, attr)):
                setattr(cls, attr, method_decorator(decorator)(getattr(cls, attr)))

        return cls

    return _dec
