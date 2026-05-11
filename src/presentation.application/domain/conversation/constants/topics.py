from enum import Enum


class Topics(Enum):
    ARITHMETIC = 1
    ALGEBRA = 2
    FRACTIONS = 3
    LINEAR_EQUATIONS = 4
    QUADRATIC_EQUATIONS = 5
    GEOMETRY = 6
    TRIGONOMETRY = 7
    LOGARITHM = 8
    PROBABILITY = 9
    STATISTICS = 10
    CALCULUS = 11

    @classmethod
    def list(cls) -> list[str]:
        return [topic.name.title() for topic in cls]