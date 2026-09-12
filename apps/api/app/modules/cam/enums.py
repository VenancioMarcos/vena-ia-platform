from enum import StrEnum


class TurningOperationType(StrEnum):
    FACING = "FACING"
    ROUGH_TURNING = "ROUGH_TURNING"
    FINISHING = "FINISHING"
    GROOVING = "GROOVING"


class ToolOrientation(StrEnum):
    RIGHT_HAND = "RIGHT_HAND"
    LEFT_HAND = "LEFT_HAND"
    NEUTRAL = "NEUTRAL"


class CompensationType(StrEnum):
    NONE = "NONE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
