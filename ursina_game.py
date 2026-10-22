"""Ursina rendering and input layer for Zombie Frontline 3D."""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
from .config import TITLE, WEAPONS, COIN_VALUE, ROUND_RULES, WORLD_HALF_SIZE
from .economy import Economy
from .rounds import RoundDirector

class ZombieFrontlineApp:
    def __init__(self):
        self.app = Ursina()
        window.title = TITLE
        window.borderless = False
        window.fullscreen = False
        window.color = color.rgb(135, 185, 220)
        window.fps_counter.enabled = True
        camera.fov = 95
        self.economy = Economy()
        self.rounds = RoundDirector()
        self.health = 100
        self.score = 0
        self.ammo = {key: spec.magazine for key, spec in WEAPONS.items()}
        self.weapon = "pistol"
        self.cooldown = 0.0
        self.reload_timer = 0.0
        self.game_over = False
        self.zombies = []
        self.coins = []
        self.merchant_active = False
        self.build_world()
        self.build_player()
        self.build_hud()
        self.spawn_coins(40)
        self.spawn_round()
        self.app.run()

    def build_world(self):
        Sky(color=color.rgb(135, 185, 220))
        sun = DirectionalLight()
        sun.rotation = (45, -35, 35)
        AmbientLight(color=color.rgba(145, 145, 155, 255))
        Entity(model="plane", scale=(120, 1, 120), texture="white_cube",
               texture_scale=(60, 60), color=color.rgb(83, 125, 68), collider="box")
        Entity(model="cube", position=(0, .03, 0), scale=(9, .05, 120),
               color=color.rgb(65, 67, 66))
        Entity(model="cube", position=(0, .03, 0), scale=(120, .05, 8),
               color=color.rgb(65, 67, 66))
        for z in range(-55, 60, 10):
            Entity(model="cube", position=(0, .07, z), scale=(.18, .02, 3.5), color=color.yellow)
        for x, z, w, d, h in [
            (-18, 13, 11, 10, 7), (18, 18, 12, 11, 8),
            (-22, -22, 12, 12, 6), (22, -30, 10, 12, 7),
            (-38, -4, 9, 12, 5), (39, 28, 13, 10, 8),
            (4, 42, 12, 9, 6), (-43, 37, 12, 11, 7),
        ]:
            Entity(model="cube", position=(x, h/2, z), scale=(w, h, d),
                   color=color.rgb(135, 120, 105), collider="box")
        random.seed(18)
        for _ in range(65):
            x, z = random.uniform(-55, 55), random.uniform(-55, 55)
            if abs(x) < 8 or abs(z) < 8:
                continue
            Entity(model="cylinder", position=(x, 1.2, z), scale=(.45, 2.4, .45),
                   color=color.rgb(95, 66, 43), collider="box")
            Entity(model="sphere", position=(x, 3, z), scale=(2.6, 3, 2.6),
                   color=color.rgb(45, 110, 45))

    def build_player(self):
        self.player = FirstPersonController(position=(0, 2, -45), speed=7)
        self.player.gravity = .8
        self.player.cursor.visible = False
        self.gun = Entity(parent=camera, model="cube", position=(.48, -.38, .72),
                          scale=(.16, .16, .58), color=color.rgb(48, 52, 55))
        Entity(parent=self.gun, model="cylinder", position=(0, .1, .55),
               rotation=(90, 0, 0), scale=(.055, .55, .055), color=color.dark_gray)

    def build_hud(self):
        self.hud = Text(parent=camera.ui, text="", position=(-.86, .46), scale=.9)
        Text(parent=camera.ui, text="+", origin=(0, 0), scale=1.8)
        Text(parent=camera.ui,
             text="WASD движение | мышь обзор | ЛКМ огонь | R перезарядка | B магазин | 1-5 оружие | Esc выход",
             origin=(0, 0), y=-.47, scale=.7)
        self.notice = Text(parent=camera.ui, text="", origin=(0, 0), y=.32, scale=1.2, color=color.yellow)
        self.update_hud()

    def say(self, text):
        self.notice.text = text
        invoke(setattr, self.notice, "text", "", delay=2.5)

    def update_hud(self):
        self.hud.text = (
            f"Здоровье: {self.health}   Монеты: {self.economy.coins}   "
            f"Раунд: {self.rounds.number}   Убито: {self.score}\\n"
            f"Оружие: {WEAPONS[self.weapon].name}   "
            f"Патроны: {self.ammo[self.weapon]}/{WEAPONS[self.weapon].magazine}"
        )

    def spawn_coins(self, count):
        for _ in range(count):
            x, z = random.uniform(-53, 53), random.uniform(-53, 53)
            coin = Entity(model="cylinder", position=(x, .45, z), scale=(.42, .12, .42),
                          rotation=(90, 0, 0), color=color.gold)
            self.coins.append(coin)

    def spawn_zombie(self):
        for _ in range(50):
            x, z = random.uniform(-53, 53), random.uniform(-53, 53)
            if distance(Vec3(x, 0, z), Vec3(self.player.x, 0, self.player.z)) > 18:
                break
        zombie = Entity(model="cube", position=(x, 1, z), scale=(.85, 1.8, .7),
                        color=color.rgb(95, 145, 78), collider="box")
        zombie.hp = self.rounds.zombie_health()
        zombie.speed = self.rounds.zombie_speed()
        zombie.attack_timer = 0
        self.zombies.append(zombie)

    def spawn_round(self):
        for _ in range(self.rounds.spawn_count):
            self.spawn_zombie()
        self.say(f"Раунд {self.rounds.number} начался!")

    def equip(self, key):
        if key not in self.economy.owned_weapons:
            self.say("Это оружие ещё не куплено")
            return
        self.weapon = key
        self.update_hud()

    def shoot(self):
        if self.game_over or self.reload_timer > 0 or self.cooldown > 0:
            return
        spec = WEAPONS[self.weapon]
        if self.ammo[self.weapon] <= 0:
            self.say("Нет патронов — нажми R")
            return
        self.ammo[self.weapon] -= 1
        self.cooldown = spec.cooldown
        rays = spec.pellets
        targets = set()
        for _ in range(rays):
            direction = camera.forward
            if rays > 1:
                direction = (camera.forward + camera.right * random.uniform(-.08, .08)).normalized()
            hit = raycast(camera.world_position, direction, distance=spec.range_m,
                          ignore=[self.player, self.gun])
            if hit.hit and hit.entity in self.zombies and hit.entity not in targets:
                targets.add(hit.entity)
                hit.entity.hp -= spec.damage
                if hit.entity.hp <= 0:
                    self.zombies.remove(hit.entity)
                    pos = hit.entity.position
                    destroy(hit.entity)
                    self.score += 1
                    if random.random() < ROUND_RULES.coin_drop_chance:
                        coin = Entity(model="cylinder", position=(pos.x, .45, pos.z),
                                      scale=(.42, .12, .42), rotation=(90, 0, 0), color=color.gold)
                        self.coins.append(coin)
        self.update_hud()

    def reload(self):
        if self.reload_timer <= 0 and self.ammo[self.weapon] < WEAPONS[self.weapon].magazine:
            self.reload_timer = WEAPONS[self.weapon].reload_seconds
            self.say("Перезарядка...")

    def open_merchant(self):
        if not self.merchant_active:
            self.say("Торговец появляется на каждом 10-м раунде")
            return
        # A compact keyboard shop keeps the starter build dependency-free.
        self.say("Магазин: F1 автомат, F2 снайпер, F3 РПГ, F4 дрон, F5 танк")

    def buy(self, key):
        if key == "rifle":
            ok, msg = self.economy.buy_weapon("rifle")
        elif key == "sniper":
            ok, msg = self.economy.buy_weapon("sniper")
        elif key == "rpg":
            ok, msg = self.economy.buy_weapon("rpg")
        elif key == "drone":
            ok, msg = self.economy.unlock_drone()
        elif key == "tank":
            ok, msg = self.economy.unlock_tank(self.rounds.number)
        else:
            ok, msg = False, "Неизвестная покупка"
        self.say(msg)
        self.update_hud()

    def input(self, key):
        if key == "escape":
            application.quit()
        elif key == "left mouse down":
            self.shoot()
        elif key == "r":
            self.reload()
        elif key == "b":
            self.open_merchant()
        elif key == "1": self.equip("pistol")
        elif key == "2": self.equip("shotgun")
        elif key == "3": self.equip("rifle")
        elif key == "4": self.equip("sniper")
        elif key == "5": self.equip("rpg")
        elif key == "f1" and self.merchant_active: self.buy("rifle")
        elif key == "f2" and self.merchant_active: self.buy("sniper")
        elif key == "f3" and self.merchant_active: self.buy("rpg")
        elif key == "f4" and self.merchant_active: self.buy("drone")
        elif key == "f5" and self.merchant_active: self.buy("tank")

    def update(self):
        if self.game_over:
            return
        dt = time.dt
        self.cooldown = max(0, self.cooldown - dt)
        if self.reload_timer > 0:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.ammo[self.weapon] = WEAPONS[self.weapon].magazine
                self.say("Перезарядка завершена")
        for coin in self.coins[:]:
            coin.rotation_y += dt * 100
            if distance(self.player.position, coin.position) < 1.7:
                self.economy.earn(COIN_VALUE)
                self.coins.remove(coin)
                destroy(coin)
                self.update_hud()
        for zombie in self.zombies[:]:
            direction = self.player.position - zombie.position
            direction.y = 0
            d = direction.length()
            if d > 1.5:
                zombie.position += direction.normalized() * zombie.speed * dt
                zombie.rotation_y = math.degrees(math.atan2(direction.x, direction.z))
            else:
                zombie.attack_timer -= dt
                if zombie.attack_timer <= 0:
                    self.health = max(0, self.health - min(18, 7 + self.rounds.number))
                    zombie.attack_timer = max(.35, 1.1 - self.rounds.number * .015)
                    self.update_hud()
                    if self.health <= 0:
                        self.game_over = True
                        self.say("Игра окончена — нажми Esc", )
                        self.player.speed = 0
                        return
        if self.rounds.update(dt):
            self.spawn_coins(10)
            self.merchant_active = self.rounds.number % 10 == 0
            if self.merchant_active:
                self.say("Торговец прибыл! B — покупки; F1-F5 — купить")
            self.spawn_round()
        if len(self.coins) < 12 and random.random() < dt * .3:
            self.spawn_coins(1)
        self.update_hud()

def launch():
    game = ZombieFrontlineApp()
    # Ursina resolves input/update callbacks on the app object in a simple way.
    # Bind module-level callbacks expected by the engine.
    return game

# Ursina calls module-level callbacks. Keep one active game instance.
_game = None
def input(key):
    if _game:
        _game.input(key)

def update():
    if _game:
        _game.update()

if __name__ == "__main__":
    _game = ZombieFrontlineApp.__new__(ZombieFrontlineApp)
    # Initialise all fields without calling the constructor's app.run().
    _game.app = Ursina()
    window.title = TITLE
    window.borderless = False
    window.fullscreen = False
    window.color = color.rgb(135, 185, 220)
    window.fps_counter.enabled = True
    camera.fov = 95
    _game.economy = Economy()
    _game.rounds = RoundDirector()
    _game.health = 100
    _game.score = 0
    _game.ammo = {key: spec.magazine for key, spec in WEAPONS.items()}
    _game.weapon = "pistol"
    _game.cooldown = 0.0
    _game.reload_timer = 0.0
    _game.game_over = False
    _game.zombies = []
    _game.coins = []
    _game.merchant_active = False
    _game.build_world()
    _game.build_player()
    _game.build_hud()
    _game.spawn_coins(40)
    _game.spawn_round()
    _game.app.run()
