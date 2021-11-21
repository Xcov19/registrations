from fastapi import HTTPException
from fastapi import status


class DuplicateEntryException(HTTPException):
    """Raises for a duplicate entry exception."""

    def __init__(self, *args, **kwargs):
        self.status_code = status.HTTP_409_CONFLICT
        super().__init__(*args, **kwargs)


class InvalidEntryException(HTTPException):
    """Invalid entry exception."""

    def __init__(self, *args, **kwargs):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        super().__init__(*args, **kwargs)
