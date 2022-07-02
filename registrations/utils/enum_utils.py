import enum


class EnumWithItems(enum.Enum):
    @classmethod
    def items(cls) -> dict[str, str]:
        return {key.name: key.value for key in cls}
