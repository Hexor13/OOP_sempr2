# https://github.com/Hexor13/OOP_sempr2

import pygame
import random
import sys

from parametrs import * 
from resources_f import screen, clock, FPS, background_img, heart_img, obstacle_img, bonus_img,plane_img,gameover_img
from classes import Plane, MeteorCloud 
from functions import show_start_screen, show_pause_screen, show_game_over_screen, level_up, generate_new_obstacles, generate_bonus, pixel_collision

#test only for OOP- sempr(podminka zakladni testy) 
#images test 
assert plane_img is not None
assert obstacle_img is not None
assert background_img is not None
assert heart_img is not None
assert bonus_img is not None
assert gameover_img is not None
print("images - ok")
#start pameters test
test_plane = Plane((100, 100), PLANE_SPEED)
assert test_plane.lives == 3, "max 3 start hearts, don't cheat -_- "
assert test_plane.speed == PLANE_SPEED, "start speed = 5, don't cheat -_- "
assert test_plane.bullet_storage == 10, "start number of bullets = 10 don't cheat -_-"
print("plane - ok")
#collision test
rect1 = pygame.Rect(0, 0, 50, 50)
rect2 = pygame.Rect(100, 100, 50, 50)
try:
    pixel_collision(test_plane.surf, rect1, obstacle_img, rect2)
    print("collision - ok")
except:
    assert False
del test_plane
print("start...")

def main():
    while True:
        show_start_screen()
        player = Plane((WIDTH//2, HEIGHT//2), PLANE_SPEED)
        #parametrs for game start
        obstacles = generate_new_obstacles(OBSTACLE_SIZE, obstacle_img)
        add_obstacles_now = 0
        bonuses = []  
        add_bonus_now = 0  
        next_bonus_time = random.randint(MIN_BONUS_TIME, MAX_BONUS_TIME)
        invincible_now = 0
        score = 0
        level_thresholds = [100,200,300,400,500,600,700,800,900,1000]
        current_level_index = 0
        obs_speed = min(OBSTACLE_SPEED, MAX_OBSTACLE_SPEED)
        meteor_cloud = MeteorCloud(WIDTH, HEIGHT)
        game_start_time = pygame.time.get_ticks()
        meteors_destroyed = 0
        running = True
        frame_counter = 0
        cloud_spawn_counter = 0
        next_cloud_spawn = random.randint(CLOUD_SPAWN_MIN, CLOUD_SPAWN_MAX)
        
        # game loop
        while running:
            clock.tick(FPS)
            frame_counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        screenshot = screen.copy()
                        show_pause_screen(screenshot)
            
            #shoot button 
            keys = pygame.key.get_pressed()
            player.move(keys, WIDTH, HEIGHT)
            if keys[pygame.K_SPACE]:
                player.shoot()
            if player.fire_cooldown > 0:
                player.fire_cooldown -= 1

            cloud_spawn_counter += 1
            if cloud_spawn_counter >= next_cloud_spawn and not meteor_cloud.active:
                meteor_cloud.activate()
                cloud_spawn_counter = 0
                next_cloud_spawn = random.randint(CLOUD_SPAWN_MIN, CLOUD_SPAWN_MAX)
            meteor_cloud.update()
            
            # obstacle generation
            add_obstacles_now += 1
            if add_obstacles_now >= ADD_OBSTACLES_TIMER:
                add_obstacles_now = 0
                obstacles.extend(generate_new_obstacles(OBSTACLE_SIZE, obstacle_img))
                score += 5  
                obs_speed += 0.2  
            # bonus generation
            add_bonus_now += 1
            if add_bonus_now >= next_bonus_time:
                add_bonus_now = 0
                bonuses.append(generate_bonus(bonus_img))
                next_bonus_time = random.randint(MIN_BONUS_TIME, MAX_BONUS_TIME)
            # check collision
            collided = False
            for i in range(len(obstacles)-1, -1, -1):
                obs = obstacles[i]
                obs["rect"].y += obs_speed
                if obs["rect"].top > HEIGHT:
                    obstacles.pop(i)
                    continue
                if invincible_now >= INVINCIBLE_TIMER:
                    plane_rect = player.rect.inflate(
                        player.rect.width*(1-player.size_factor),
                        player.rect.height*(1-player.size_factor)
                    )
                    if pixel_collision(player.surf, plane_rect, obs["surf"], obs["rect"]):
                        collided = True
            #collision for standart 
            if collided:
                player.lives -= 1
                invincible_now = 0
                player.rect.topleft = (WIDTH//2, HEIGHT//2)
                if player.lives <= 0:
                    running = False
            #collision for cloud
            if meteor_cloud.check_collision(player.rect, player.surf):
                if invincible_now >= INVINCIBLE_TIMER:
                    player.lives -= 1
                    invincible_now = 0
                    player.rect.topleft = (WIDTH//2, HEIGHT//2)
                    if player.lives <= 0:
                        running = False
            
            # invincible timer
            if invincible_now < INVINCIBLE_TIMER:
                invincible_now += 1
            
            #update bullets for stats  
            points_from_bullets, destroyed_count = player.update_bullets(obstacles)
            score += points_from_bullets
            meteors_destroyed += destroyed_count
           
           #level up check
           #level from score
            if current_level_index < len(level_thresholds) and score >= level_thresholds[current_level_index]:
                screenshot = screen.copy() #create screenshot for background
                level_up(player,screenshot)
                current_level_index += 1
            #level from bonus
            for i in range(len(bonuses) - 1, -1, -1):
                bonus = bonuses[i]
                bonus["rect"].y += BONUS_SPEED
                if bonus["rect"].top > HEIGHT:
                    bonuses.pop(i)
                    continue
                if pixel_collision(player.surf, player.rect, bonus["surf"], bonus["rect"]):
                    if bonus["type"] == "level_up":
                        score += 20
                        screenshot = screen.copy()
                        level_up(player,screenshot)  
                    bonuses.pop(i)
           #draw objects and images
            screen.blit(background_img, (0, 0))
            for obs in obstacles:
                screen.blit(obs["surf"], obs["rect"])
            
            meteor_cloud.draw(screen)

            player.draw_bullets(screen)

            for bonus in bonuses:
                screen.blit(bonus["surf"], bonus["rect"])

            heart_w, heart_h = heart_img.get_size()
            hearts_x = WIDTH - (player.lives * (heart_w + 4)) - 4
            hearts_y = 4
            for i in range(max(0, player.lives)):
                screen.blit(heart_img, (hearts_x + i * (heart_w + 4), hearts_y))
            #draw boost battery
            boost_bar_width = 200
            boost_bar_height = 20
            boost_bar_x = 10
            boost_bar_y = HEIGHT - 40
            
            pygame.draw.rect(screen, (50, 50, 50), 
                            (boost_bar_x, boost_bar_y, boost_bar_width, boost_bar_height))
            
            boost_fill_width = (player.boost_amount / player.max_boost) * boost_bar_width
            boost_color = (255, 100, 100) if player.boost_active else (0, 150, 255)
            pygame.draw.rect(screen, boost_color, 
                            (boost_bar_x, boost_bar_y, boost_fill_width, boost_bar_height))

            pygame.draw.rect(screen, (255, 255, 255), 
                            (boost_bar_x, boost_bar_y, boost_bar_width, boost_bar_height), 2)
            
            boost_font = pygame.font.SysFont(None, 24)
            boost_text = boost_font.render("BOOST (SHIFT)", True, (255, 255, 255))
            screen.blit(boost_text, (boost_bar_x + boost_bar_width + 10, boost_bar_y))
            #draw speed now
            speed_font = pygame.font.SysFont(None, 30)
            speed_text = speed_font.render(f"Speed: {player.speed}", True, (255, 255, 255))
            screen.blit(speed_text, (WIDTH - 150, 40))
            #draw score 
            font = pygame.font.SysFont(None, 40)
            score_text = font.render(f"Score: {score}", True, (255,255,255))
            screen.blit(score_text, (10, 10))
            #draw bullet count
            bullets_text = speed_font.render(f"Bullets: {player.bullet_storage}/{player.max_bullet_storage}", True, (255,255,255))
            screen.blit(bullets_text, (WIDTH - 150, 70))

            if invincible_now % 10 < 5:
                screen.blit(player.surf, player.rect)

            pygame.display.flip()
        #stop game timer    
        game_duration = (pygame.time.get_ticks() - game_start_time) // 1000 #1000ms 
        #show gameover screen
        show_game_over_screen(score,meteors_destroyed, game_duration, player)

if __name__ == "__main__":
    main()

# P.S. honestly, my score is 800, try to beat it :D