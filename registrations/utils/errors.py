from __future__ import annotations

from typing import Any, Optional, Type, Union

import pydantic
from pydantic import error_wrappers, main

ValidationModelType = Union[main.ModelMetaclass, Type[pydantic.BaseModel], Any]


class MissingRegistrationFieldError(pydantic.ValidationError):
    def __init__(
        self,
        error_msg: str,
        model: ValidationModelType,
        exc_tb: Optional[str] = None,
    ):
        error_wrapper = error_wrappers.ErrorWrapper(
            Exception(error_msg), exc_tb or error_msg
        )
        super().__init__(errors=[error_wrapper], model=model)  # type: ignore[arg-type]


class InvalidRegistrationEntryError(Exception):
    """Raised when invalid hospital registration entry is provided."""

    def __init__(self, error_msg: str):
        super().__init__(error_msg)
