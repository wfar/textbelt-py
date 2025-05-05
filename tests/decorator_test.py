import pytest
from pydantic import ValidationError
from requests import Response
from requests.exceptions import HTTPError, JSONDecodeError

from textbelt_py.decorators import exception_handler_decorator
from textbelt_py.exceptions import TextbeltException
from textbelt_py.models import SMSStatusResponse


def test_exception_handler_decorator_handles_textbelt_exception() -> None:
    @exception_handler_decorator
    def textbelt_exception_func() -> None:
        raise TextbeltException("Test Exception")

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_exception_func()

    assert ex_info.value.message == "Test Exception"
    assert ex_info.value.exception is None
    assert ex_info.value.ex_type is None


def test_exception_handler_decorator_handles_requests_http_error() -> None:
    @exception_handler_decorator
    def textbelt_exception_func() -> None:
        raise HTTPError("Test Exception")

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_exception_func()

    assert (
        ex_info.value.message
        == "Requests error occurred (Type = <class 'requests.exceptions.HTTPError'> | Message = Test Exception)"
    )
    assert isinstance(ex_info.value.exception, HTTPError)
    assert ex_info.value.ex_type is HTTPError


def test_exception_handler_decorator_handles_requests_json_decode_error() -> None:
    @exception_handler_decorator
    def textbelt_exception_func() -> None:
        response = Response()
        response.json()

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_exception_func()

    assert (
        ex_info.value.message
        == "Requests error occurred (Type = <class 'requests.exceptions.JSONDecodeError'> | Message = Expecting value: line 1 column 1 (char 0))"
    )
    assert isinstance(ex_info.value.exception, JSONDecodeError)
    assert ex_info.value.ex_type is JSONDecodeError


def test_exception_handler_decorator_handles_pydantic_validation_error() -> None:
    @exception_handler_decorator
    def textbelt_exception_func() -> None:
        SMSStatusResponse.model_validate(None)

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_exception_func()

    assert (
        "Pydantic error occurred (Type = <class 'pydantic_core._pydantic_core.ValidationError'> | Message = 1 validation error for SMSStatusResponse"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, ValidationError)
    assert ex_info.value.ex_type is ValidationError


def test_exception_handler_decorator_handles_unexcpted_exception() -> None:
    @exception_handler_decorator
    def textbelt_exception_func() -> None:
        raise Exception("Text Exception")

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_exception_func()

    assert (
        ex_info.value.message
        == "Unexpected error occurred (Type = <class 'Exception'> | Message = Text Exception)"
    )
    assert isinstance(ex_info.value.exception, Exception)
    assert ex_info.value.ex_type is Exception
