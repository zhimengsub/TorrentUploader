import enum


class PubType(enum.Enum):
    Todo = 0
    Done = 1

    @property
    def value(self) -> int:
        return super().value


class IntroMode(enum.Enum):
    Edit = 0
    Preview = 1