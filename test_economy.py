import unittest
from zombiefrontline.economy import Economy

class EconomyTests(unittest.TestCase):
    def test_free_weapons_are_owned(self):
        e = Economy()
        self.assertIn("pistol", e.owned_weapons)
        self.assertIn("shotgun", e.owned_weapons)

    def test_rifle_purchase(self):
        e = Economy(coins=100)
        ok, _ = e.buy_weapon("rifle")
        self.assertTrue(ok)
        self.assertEqual(e.coins, 0)
        self.assertIn("rifle", e.owned_weapons)

    def test_drone_cost(self):
        e = Economy(coins=999)
        ok, _ = e.unlock_drone()
        self.assertFalse(ok)
        e.earn(1)
        ok, _ = e.unlock_drone()
        self.assertTrue(ok)
        self.assertTrue(e.drone_unlocked)

    def test_tank_level_gate(self):
        e = Economy()
        self.assertFalse(e.unlock_tank(1)[0])
        self.assertTrue(e.unlock_tank(2)[0])

    def test_merchant_interval(self):
        self.assertFalse(Economy.merchant_appears(9))
        self.assertTrue(Economy.merchant_appears(10))

if __name__ == "__main__":
    unittest.main()
