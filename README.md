# Zombie Frontline 3D — expanded starter project

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this folder.
3. Open Command Prompt in this folder.
4. Run `python -m pip install -r requirements.txt`
5. Run `python main.py`

## Controls
- WASD: move, mouse: look
- Left mouse: shoot, R: reload
- 1 pistol, 2 shotgun, 3 rifle, 4 sniper, 5 RPG
- B: merchant info; merchant is active every tenth round
- While the merchant is active: F1 rifle, F2 sniper, F3 RPG, F4 drone, F5 tank
- Esc: quit

## Economy and progression
- Pistol and shotgun are free.
- Rifle costs 100 coins; sniper costs 250 and has one-shot damage.
- RPG unlock costs 500 coins.
- Drone unlock costs 1000 coins.
- Tank unlock becomes available from round 2.
- Coins are worth 5 each. Ten coin spawns are added at the end of each round.
- Round duration is about 25 seconds; zombie count, health and speed scale up.

This is a prototype foundation, not a finished commercial game. Art assets, save/load integration, a real vehicle controller, sound, animations, collision polish, and balancing remain to be implemented. Primitive shapes are used intentionally to avoid external asset downloads.
