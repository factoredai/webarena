import asyncio
import inspect
from functools import wraps
from typing import Any, Generic, Iterable, TypeVar, Union

T = TypeVar("T")  # Represents the wrapped object's type

class AsyncWrapper(Generic[T]):
    def __init__(self, obj: T):
        self._obj: T = obj

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._obj, name)

        if callable(attr):
            if inspect.iscoroutinefunction(attr):
                # If it's an async function, wrap it to run in the event loop
                @wraps(attr)
                def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    loop = asyncio._get_running_loop()
                    if loop:
                        return loop.run_until_complete(attr(*args, **kwargs))
                    else:
                        return asyncio.run(attr(*args, **kwargs))
                return async_wrapper
            else:
                # If it's a sync function, return it as-is
                return attr

        elif isinstance(attr, (int, float, str, bool, type(None))):
            # Primitive types don't need wrapping
            return attr

        elif isinstance(attr, list):
            # Wrap list elements
            return [AsyncWrapper(item) if isinstance(item, object) else item for item in attr]

        elif isinstance(attr, tuple):
            # Wrap tuple elements
            return tuple(AsyncWrapper(item) if isinstance(item, object) else item for item in attr)

        elif isinstance(attr, set):
            # Wrap set elements
            return {AsyncWrapper(item) if isinstance(item, object) else item for item in attr}

        elif isinstance(attr, dict):
            # Wrap dictionary values (keys remain unchanged)
            return {key: AsyncWrapper(value) if isinstance(value, object) else value for key, value in attr.items()}

        else:
            # Recursively wrap objects for deeper attributes
            return AsyncWrapper(attr)

    def unwrap(self) -> T:
        """Return the original wrapped object."""
        return self._obj