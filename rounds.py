"""Infinite round progression and spawn scaling."""
from dataclasses import dataclass
from .config import ROUND_RULES

@dataclass
class RoundDirector:
    number: int = 1
    elapsed: float = 0.0
    alive_at_start: int = 0

    @property
    def duration(self) -> float:
        return float(ROUND_RULES.seconds)

    @property
    def spawn_count(self) -> int:
        return min(
            ROUND_RULES.max_zombies_per_round,
            ROUND_RULES.base_zombies + self.number * ROUND_RULES.zombies_per_round,
        )

    def zombie_health(self) -> int:
        return max(1, int(ROUND_RULES.base_zombie_health +
                          (self.number - 1) * ROUND_RULES.health_per_round))

    def zombie_speed(self) -> float:
        return min(ROUND_RULES.max_zombie_speed,
                   ROUND_RULES.base_zombie_speed +
                   (self.number - 1) * ROUND_RULES.speed_per_round)

    def update(self, dt: float) -> bool:
        """Return True when a round ends."""
        self.elapsed += max(0.0, dt)
        if self.elapsed >= self.duration:
            self.elapsed -= self.duration
            self.number += 1
            return True
        return False

    def reset(self) -> None:
        self.number = 1
        self.elapsed = 0.0
        self.alive_at_start = 0
