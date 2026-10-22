"""Central game configuration and balancing tables."""
from dataclasses import dataclass

TITLE = "Zombie Frontline 3D"
ROUND_SECONDS = 25
COIN_VALUE = 5
STARTING_HEALTH = 100
STARTING_AMMO = 12
DRONE_PRICE = 1000
RIFLE_PRICE = 100
SNIPER_PRICE = 250
RPG_PRICE = 500
MERCHANT_INTERVAL = 10
WORLD_HALF_SIZE = 60

@dataclass(frozen=True)
class WeaponSpec:
    name: str
    price: int
    damage: int
    magazine: int
    cooldown: float
    reload_seconds: float
    range_m: float
    pellets: int = 1
    unlock_purchase: bool = True

WEAPONS = {
    "pistol": WeaponSpec("Пистолет", 0, 1, 12, .35, 1.0, 55, unlock_purchase=False),
    "shotgun": WeaponSpec("Дробовик", 0, 3, 6, .9, 1.5, 20, pellets=5, unlock_purchase=False),
    "rifle": WeaponSpec("Автомат", RIFLE_PRICE, 2, 30, .12, 1.7, 75),
    "sniper": WeaponSpec("Снайперская винтовка", SNIPER_PRICE, 999, 5, 1.7, 2.8, 120),
    "rpg": WeaponSpec("РПГ", RPG_PRICE, 8, 1, 1.5, 2.4, 65),
}

@dataclass(frozen=True)
class RoundRules:
    seconds: int = ROUND_SECONDS
    base_zombies: int = 5
    zombies_per_round: int = 2
    max_zombies_per_round: int = 60
    base_zombie_health: int = 2
    health_per_round: float = .45
    base_zombie_speed: float = 1.2
    speed_per_round: float = .07
    max_zombie_speed: float = 4.2
    coin_drop_chance: float = .65
    end_round_coin_spawns: int = 10

ROUND_RULES = RoundRules()
