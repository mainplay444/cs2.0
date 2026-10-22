"""Currency, purchase validation and unlock rules."""
from dataclasses import dataclass, field
from .config import WEAPONS, DRONE_PRICE, RPG_PRICE, MERCHANT_INTERVAL

@dataclass
class Economy:
    coins: int = 0
    owned_weapons: set[str] = field(default_factory=lambda: {"pistol", "shotgun"})
    drone_unlocked: bool = False
    tank_unlocked: bool = False
    rpg_unlocked: bool = False

    def earn(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("Cannot award a negative coin amount")
        self.coins += amount
        return self.coins

    def can_afford(self, price: int) -> bool:
        return price >= 0 and self.coins >= price

    def _charge(self, price: int) -> bool:
        if not self.can_afford(price):
            return False
        self.coins -= price
        return True

    def buy_weapon(self, weapon_key: str) -> tuple[bool, str]:
        if weapon_key not in WEAPONS:
            return False, "Неизвестное оружие"
        if weapon_key in self.owned_weapons:
            return False, "Оружие уже куплено"
        if weapon_key == "rpg":
            return self.unlock_rpg()
        price = WEAPONS[weapon_key].price
        if not self._charge(price):
            return False, "Недостаточно монет"
        self.owned_weapons.add(weapon_key)
        return True, "Оружие куплено"

    def unlock_rpg(self) -> tuple[bool, str]:
        if self.rpg_unlocked:
            return False, "РПГ уже разблокирована"
        if not self._charge(RPG_PRICE):
            return False, "Для разблокировки РПГ нужно 500 монет"
        self.rpg_unlocked = True
        self.owned_weapons.add("rpg")
        return True, "РПГ разблокирована"

    def unlock_drone(self) -> tuple[bool, str]:
        if self.drone_unlocked:
            return False, "Дрон уже разблокирован"
        if not self._charge(DRONE_PRICE):
            return False, "Для дрона нужно 1000 монет"
        self.drone_unlocked = True
        return True, "Дрон разблокирован"

    def unlock_tank(self, round_number: int) -> tuple[bool, str]:
        if round_number < 2:
            return False, "Танк доступен со второго раунда"
        self.tank_unlocked = True
        return True, "Танк разблокирован"

    @staticmethod
    def merchant_appears(round_number: int) -> bool:
        return round_number > 0 and round_number % MERCHANT_INTERVAL == 0
