class TextbeltException(Exception):
    """
    Base exception class used to denote any errors
    that occur when interacting with the Textbelt API.

    Functions as the sole exception class to handle all
    errors to simplify exception handling.

    `TextbeltException` class can be used to denote standalone
    exceptions as well as a wrapper for all other exceptions
    that occur during execution such as `Pydantic`
    and `Requests` errors.

    Attributes:
        message (str): error message to display.
        exception (Exception | None): optional exception that
            occurred and is being wrapped.
        ex_type (type[Exception] | None): optional type for the exception
            that is being wrapped.
    """

    def __init__(
        self,
        message: str,
        exception: Exception | None = None,
    ):
        """
        Initializes the exception class with a required
        error message and optionally, another causal exception
        that occurred to wrap and store for downstream
        processing.

        If exception is provided, the type and message from the
        wrapped exception are added to textbelt exception message.

        Args:
            message (str): error message containing information of issue.
            exception (Exception | None): optional exception being wrapped.
        """

        if exception:
            message = f"{message} (Type = {type(exception)} | Message = {str(exception)})"

        super().__init__(message)
        self.message = message
        self.exception = exception
        self.ex_type = type(exception) if exception else None
