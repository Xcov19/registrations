import enum


def enum_value_of(enum_class: enum.Enum) -> str:
    if not isinstance(enum_class, enum.Enum):
        raise AssertionError
    return str(enum_class.value)


class EnumWithItems(enum.Enum):
    @classmethod
    def items(cls) -> dict[str, str]:
        return {key.name: key.value for key in cls}

    @classmethod
    def values(cls) -> list[str]:
        return [key.value for key in cls]
