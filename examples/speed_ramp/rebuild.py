"""Synthetic rebuild of a clamped linear speed ramp (teaching fixture)."""

SPEED = 6.0
ACCELERATION = 0.001
MAX_SPEED = 13.0


def apply(ticks: int) -> float:
    speed = SPEED
    for _ in range(int(ticks)):
        if speed < MAX_SPEED:
            speed += ACCELERATION
            if speed > MAX_SPEED:
                speed = MAX_SPEED
    return round(speed, 1)
