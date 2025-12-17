#classes

import pygame
import random
from parametrs import *
from resources_f import *
from functions import pixel_collision

class Plane:
    def __init__(self, pos, speed):
        #parametrs
        self.original_surf = plane_img 
        self.surf = self.original_surf
        self.rect = self.surf.get_rect(topleft=pos)
        self.speed = speed
        self.bullets = []
        self.fire_cooldown = 0
        self.bullet_storage = 10           #<---- TEST PARAMETR(= most changeable)
        self.max_bullet_storage = 25 
        self.lives = 3                    #<---- TEST PARAMETR
        self.size_factor = 1.0
        self.speed = speed 
        self.base_speed = speed
        self.boost_active = False
        self.boost_amount = BOOST_MAX
        self.max_boost = BOOST_MAX
        self.upgrade_count = 0

    #keyboard buttons movement
    def move(self, keys, width, height):
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.boost_amount > 0:
            self.boost_active = True
            self.boost_amount = max(0, self.boost_amount - BOOST_DRAIN_RATE)
        else:
            self.boost_active = False

        if self.boost_active:
            current_speed = self.speed * 2
        else:
            current_speed = self.speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.top > 0:
            self.rect.y -= current_speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.bottom < height:
            self.rect.y += current_speed
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= current_speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < width:
            self.rect.x += current_speed

    def shoot(self):
        
        if self.fire_cooldown == 0 and self.bullet_storage > 0 and len(self.bullets) < self.max_bullet_storage:
            pos = (self.rect.centerx, self.rect.top)
            self.bullets.append(Bullet(pos))
            self.bullet_storage -= 1  
            self.fire_cooldown = 20
    #update bullets and check coliision with meteors(obstacles)+count them 
    def update_bullets(self, obstacles):
        points_bullet = 0
        destroyed_count = 0 
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
                continue
            for obs in obstacles[:]:
                if bullet.rect.colliderect(obs["rect"]):
                    obstacles.remove(obs)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    points_bullet += 10
                    destroyed_count += 1 
                    break
        return points_bullet, destroyed_count
    
    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)
    # for size level up
    def update_size(self):
        new_width = int(self.original_surf.get_width() * self.size_factor)
        new_height = int(self.original_surf.get_height() * self.size_factor)
        self.surf = pygame.transform.scale(self.original_surf, (new_width, new_height))
        
        center = self.rect.center
        self.rect = self.surf.get_rect(center=center)
    # for level up
    def refill_bullets(self, amount):
        self.bullet_storage = min(self.max_bullet_storage, self.bullet_storage + amount)
    # for level up
    def increase_speed(self, amount):
        self.speed = min(self.speed + amount, MAX_PLANE_SPEED)
        self.base_speed = self.speed
    # for level up
    def refill_boost(self):
        self.boost_amount = self.max_boost

class Bullet:
    def __init__(self, pos):
        self.surf = pygame.Surface((5, 15))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect(midbottom=pos)
        self.speed = -15
        
    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

class MeteorCloud:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False
        self.timer = 0
        self.warning = False
        self.meteors = []
        self.warning_sign = None
        self.direction = random.choice(["left", "right"])
        self.generate_warning_sign()
        
    def generate_warning_sign(self):
        font = pygame.font.SysFont(None, 100)
        self.warning_sign = font.render("!", True, (255, 50, 50))
        
    def activate(self):
        if not self.active:
            self.active = True
            self.warning = True
            self.timer = CLOUD_WARNING_TIME
            self.direction = random.choice(["left", "right"])
            self.generate_meteors()
    #generation random number of meteors(and ranodm side)        
    def generate_meteors(self):
        self.meteors = []
        meteor_count = random.randint(25, 50)
        meteor_img_small = pygame.transform.scale(obstacle_img, (20, 20))
        start_y = random.randint(HEIGHT-100, HEIGHT+50)
        
        for _ in range(meteor_count):
            if self.direction == "right":
                x = -50 + random.randint(-30, 30)
            else:
                x = WIDTH + 50 + random.randint(-30, 30)
            y = start_y + random.randint(-40, 40)
            rect = meteor_img_small.get_rect(center=(x, y))
            speed_x = CLOUD_SPEED if self.direction == "right" else -CLOUD_SPEED
            speed_y = random.uniform(-0.5, 0.5)
            self.meteors.append({
                "surf": meteor_img_small,
                "rect": rect,
                "speed": (speed_x, speed_y),
                "direction": self.direction
            })
    
    def update(self):
        if not self.active:
            return
            
        self.timer -= 1
        
        if self.warning:
            if self.timer <= 0:
                self.warning = False
                self.timer = CLOUD_DURATION
        else:
            for meteor in self.meteors:
                meteor["rect"].x += meteor["speed"][0]
                meteor["rect"].y += meteor["speed"][1]
                meteor["rect"].y += random.uniform(-0.3, 1.3)

            if self.timer <= 0:
                self.active = False
            else:
                all_out_of_screen = True
                for meteor in self.meteors:
                    if self.direction == "right" and meteor["rect"].left < WIDTH + 100:
                        all_out_of_screen = False
                        break
                    elif self.direction == "left" and meteor["rect"].right > -100:
                        all_out_of_screen = False
                        break
                
                if all_out_of_screen:
                    self.active = False
    #collision only for cloud
    def check_collision(self, player_rect, player_surf):
        if not self.active or self.warning:
            return False
            
        for meteor in self.meteors:
            if pixel_collision(player_surf, player_rect, meteor["surf"], meteor["rect"]):
                return True
        return False
    #draw warning sign
    def draw(self, screen):
        if not self.active:
            return
            
        if self.warning:
            if self.direction == "right":
                screen.blit(self.warning_sign, (20, HEIGHT - 150))
            else:
                screen.blit(self.warning_sign, (WIDTH - 100, HEIGHT - 150))
                
            if pygame.time.get_ticks() % 400 < 200:
                font = pygame.font.SysFont(None, 36)
                side_text = "LEFT" if self.direction == "right" else "RIGHT"
                warning_text = font.render(f"CLOUD FROM {side_text}!", True, (255, 255, 255))
                screen.blit(warning_text, (WIDTH//2 - 120, HEIGHT - 100))
        else:
            for meteor in self.meteors:
                screen.blit(meteor["surf"], meteor["rect"])