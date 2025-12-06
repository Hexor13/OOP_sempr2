# SpaceJet Game
## Description
"SpaceJet" is a simple 2D arcade-style game made using Pygame. In this game, you control a spaceship and must avoid obstacles that fall from the top of the screen. The objective is to survive as long as possible without colliding with obstacles. The game features: progressive difficulty, upgrade systems, and special abilities to enhance your gameplay experience. The game includes a life counter, and when the spaceship collides with obstacles, it loses a life. After losing all lives, the game ends.
## How to Run
Follow the steps below to compile and run the project on your local machine.

1. Clone the repository:

2. Open a terminal and navigate to the folder where the project is located.

3. Dowmload Pygame

- Use the following command to instal Pygame:
```
pip install pygame-ce
```

4. Run the game:

- You can run the game from the build directory:

```
python main.py
```

## Game Controls
- W or Up Arrow: Move the spaceship up
- S or Down Arrow: Move the spaceship down
- A or Left Arrow: Move the spaceship left
- D or Right Arrow: Move the spaceship right
- Space: Bullets
- Shift: Speed boost
- Esc: Pause game / Resume

The spaceship has a speed limit for movement, and the screen boundary prevents the spaceship from moving out of bounds.

## Scoring System 
+5 points - For each wave of obstacles avoided 

+10 points - For each obstacle destroyed with bullets 

## Upgrade Options (Level Up) 
1. Smaller Hitbox - Reduces collision size by 20% 

2. +1 Life - Adds an extra life 

3. +5 Bullet Storage - Increases maximum bullet capacity 

4. +1 Permanent Speed - Permanently increases ship speed 

5. Refill Boost - Completely restores boost meter