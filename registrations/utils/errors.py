from __future__ import annotations

from typing import Optional
from typing import Type

import pydantic
from pydantic import error_wrappers


class MissingRegistrationFieldError(pydantic.ValidationError):
    def __init__(
        self,
        error_msg: str,
        model: Type[pydantic.BaseModel],
        exc_tb: Optional[str] = None,
    ):
        error_wrapper = error_wrappers.ErrorWrapper(
            Exception(error_msg), exc_tb or error_msg
        )
        super().__init__(errors=[error_wrapper], model=model)


class InvalidRegistrationEntryError(Exception):
    """Raised when invalid hospital registration entry is provided."""

    def __init__(self, error_msg: str):
        super().__init__(error_msg)
