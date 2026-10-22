"""Engine-independent game entity data models."""
from dataclasses import dataclass
from math import hypot

@dataclass
class Vec2:
    x: float
    z: float

    def distance_to(self, other: "Vec2") -> float:
        return hypot(self.x - other.x, self.z - other.z)

    def normalized_towards(self, other: "Vec2") -> "Vec2":
        dx, dz = other.x - self.x, other.z - self.z
        length = hypot(dx, dz) or 1.0
        return Vec2(dx / length, dz / length)

@dataclass
class ZombieState:
    entity_id: int
    position: Vec2
    hp: int
    speed: float
    attack_cooldown: float = 0.0
    reward: int = 5
    alive: bool = True

    def take_damage(self, amount: int) -> bool:
        self.hp -= max(0, amount)
        if self.hp <= 0:
            self.alive = False
        return not self.alive

@dataclass
class CoinState:
    entity_id: int
    position: Vec2
    value: int = 5
    collected: bool = False

@dataclass
class PlayerState:
    position: Vec2 = Vec2(0, -45)
    health: int = 100
    max_health: int = 100
    score: int = 0
    alive: bool = True

    def damage(self, amount: int) -> None:
        self.health = max(0, self.health - max(0, amount))
        self.alive = self.health > 0

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + max(0, amount))
