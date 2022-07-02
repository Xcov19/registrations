from typing import Optional

import pydantic


class Address(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    street: str
    street2: Optional[str]
    city: str
    state: str
    country: str

    @pydantic.root_validator(pre=True)
    @classmethod
    def _validate_address(cls, values):
        # TODO: use internal library to validate abbreviation ISO codes for:
        # 1. country
        # 2. state
        return values
