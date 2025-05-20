from typing import Callable, ParamSpec, TypeVar

from pydantic import ValidationError
from requests.exceptions import HTTPError, JSONDecodeError

from .exceptions import TextbeltException

P = ParamSpec("P")
T = TypeVar("T")


def exception_handler_decorator(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)

        except TextbeltException as e:
            raise e

        except ValidationError as e:
            raise TextbeltException(message="Pydantic error occurred", exception=e)

        except (HTTPError, JSONDecodeError) as e:
            raise TextbeltException(message="Requests error occurred", exception=e)

        except Exception as e:
            raise TextbeltException(message="Unexpected error occurred", exception=e)

    return wrapper
