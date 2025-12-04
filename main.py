import pygame
import random
import sys

#game parametrs
WIDTH, HEIGHT = 500, 980
FPS = 60
ADD_OBSTACLES_TIMER = 80
INVINCIBLE_TIMER = 120
PLANE_SPEED = 5
OBSTACLE_SPEED = 10
COLUMNS = 5
OBSTACLE_SIZE = 50
MIN_BONUS_TIME = 300
MAX_BONUS_TIME = 500
BONUS_SPEED = 5

#images 
PLANE_FILE = "resources/pngwing.com.png"
OBSTACLE_FILE = "resources/pngegg.png"
BACKGROUND_FILE = "resources/space.jpg"
GAMEOVER_FILE = "resources/game_over.jpg"
HEART_FILE = "resources/heart.png"
START_FILE = "resources/start_screen_real.png"
#START_FILE = "resources/start_screen_CZ.png" #EASTER EGG :D
#START_FILE = "resources/start_screen_RUS.png #EASTER EGG2 :D
BONUS_FILE = "resources/bonus.png"


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceJet Game (Python)")
clock = pygame.time.Clock()

def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"no {path}: {e}")
        pygame.quit()
        sys.exit(1)

plane_img = load_image(PLANE_FILE)
obstacle_img = load_image(OBSTACLE_FILE)
background_img = load_image(BACKGROUND_FILE)
gameover_img = load_image(GAMEOVER_FILE)
heart_img = load_image(HEART_FILE)
start_img = load_image(START_FILE)
bonus_img = load_image(BONUS_FILE)

def generate_new_obstacles(size, texture_surface):
    res = []
    obstacle_num = COLUMNS
    available_positions = list(range(obstacle_num))
    selected_positions = random.sample(available_positions, obstacle_num - 1)
    for obstacle_pos in selected_positions:
        x = obstacle_pos * size * 2
        y = -2 * size
        rect = texture_surface.get_rect(topleft=(x, y))
        res.append({"surf": texture_surface, "rect": rect})
    return res

def generate_bonus(texture_surface):
    small_bonus = pygame.transform.scale(texture_surface, (40, 40))
    x = random.randint(0, WIDTH - 40)  
    y = -40 
    rect = small_bonus.get_rect(topleft=(x, y))
    return {"surf": small_bonus, "rect": rect, "type": "level_up"}

def pixel_collision(surf1, rect1, surf2, rect2):
    mask1 = pygame.mask.from_surface(surf1)
    mask2 = pygame.mask.from_surface(surf2)
    offset = (rect2.left - rect1.left, rect2.top - rect1.top)
    return mask1.overlap(mask2, offset) is not None


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

class Plane:
    def __init__(self, pos, speed):
        self.original_surf = plane_img 
        self.surf = self.original_surf
        self.rect = self.surf.get_rect(topleft=pos)
        self.speed = speed
        self.bullets = []
        self.fire_cooldown = 0
        self.bullet_storage = 100           #<---- TEST PARAMETR
        self.max_bullet_storage = 25 
        self.lives = 300                    #<---- TEST PARAMETR
        self.size_factor = 1.0  

    def move(self, keys, width, height):
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.top > 0:
            self.rect.y -= self.speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.bottom < height:
            self.rect.y += self.speed
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < width:
            self.rect.x += self.speed

    def shoot(self):
        
        if self.fire_cooldown == 0 and self.bullet_storage > 0 and len(self.bullets) < self.max_bullet_storage:
           
            pos = (self.rect.centerx, self.rect.top)
            self.bullets.append(Bullet(pos))
            self.bullet_storage -= 1  
            self.fire_cooldown = 20

    def update_bullets(self, obstacles, score_ref):
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
                    score_ref[0] += 1  
                    break

    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def update_size(self):
        new_width = int(self.original_surf.get_width() * self.size_factor)
        new_height = int(self.original_surf.get_height() * self.size_factor)
        self.surf = pygame.transform.scale(self.original_surf, (new_width, new_height))
        
        center = self.rect.center
        self.rect = self.surf.get_rect(center=center)
    
    def refill_bullets(self, amount):
        self.bullet_storage = min(self.max_bullet_storage, self.bullet_storage + amount)

def show_start_screen():
    showing = True
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                showing = False
        screen.fill((0,0,0))
        start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(start_img, start_rect)
        pygame.display.flip()
        clock.tick(FPS)


def show_game_over_screen(score):
    showing = True
    font = pygame.font.SysFont(None, 60)
    text_surf = font.render(f"Score: {score}", True, (255,255,255))
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                showing = False
        screen.blit(background_img, (0,0))
        go_rect = gameover_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
        screen.blit(gameover_img, go_rect)
        screen.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
        pygame.display.flip()
        clock.tick(FPS)


def level_up(player):
    font = pygame.font.SysFont(None, 40)

    options = [
        "1) Smaller hitbox",
        "2) +1 life", 
        "3) +5 bullets to storage"
    ]
    choosing = True
    while choosing:
        screen.fill((0,0,0))
        for i, option in enumerate(options):
            txt = font.render(option, True, (255,255,0))
            screen.blit(txt, (50, 100 + i*60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.size_factor *= 0.8
                    player.update_size()
                    choosing = False
                elif event.key == pygame.K_2:
                    player.lives += 1
                    choosing = False
                elif event.key == pygame.K_3:
                   
                    player.refill_bullets(5)
                    choosing = False


def main():
    while True:
        show_start_screen()
        player = Plane((200, 500), PLANE_SPEED)
        obstacles = generate_new_obstacles(OBSTACLE_SIZE, obstacle_img)
        add_obstacles_now = 0
        bonuses = []  
        add_bonus_now = 0  
        next_bonus_time = random.randint(MIN_BONUS_TIME, MAX_BONUS_TIME)
        invincible_now = 0
        score = 0
        level_thresholds = [50, 120,  170, ]          #<---- TEST PARAMETR
        current_level_index = 0
        obs_speed = OBSTACLE_SPEED

        running = True
        frame_counter = 0
        while running:
            clock.tick(FPS)
            frame_counter += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            keys = pygame.key.get_pressed()
            player.move(keys, WIDTH, HEIGHT)
            if keys[pygame.K_SPACE]:
                player.shoot()
            if player.fire_cooldown > 0:
                player.fire_cooldown -= 1

            
            add_obstacles_now += 1
            if add_obstacles_now >= ADD_OBSTACLES_TIMER:
                add_obstacles_now = 0
                obstacles.extend(generate_new_obstacles(OBSTACLE_SIZE, obstacle_img))
                score += 5  
                obs_speed += 0.2  

            add_bonus_now += 1
            if add_bonus_now >= next_bonus_time:
                add_bonus_now = 0
                bonuses.append(generate_bonus(bonus_img))
                next_bonus_time = random.randint(MIN_BONUS_TIME, MAX_BONUS_TIME)
            
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

            if collided:
                player.lives -= 1
                invincible_now = 0
                player.rect.topleft = (200, 500)
                if player.lives <= 0:
                    running = False

            if invincible_now < INVINCIBLE_TIMER:
                invincible_now += 1

            player.update_bullets(obstacles, [score])
           
            if current_level_index < len(level_thresholds) and score >= level_thresholds[current_level_index]:
                level_up(player)
                current_level_index += 1

            for i in range(len(bonuses) - 1, -1, -1):
                bonus = bonuses[i]
                bonus["rect"].y += BONUS_SPEED
                if bonus["rect"].top > HEIGHT:
                    bonuses.pop(i)
                    continue
                if pixel_collision(player.surf, player.rect, bonus["surf"], bonus["rect"]):
                    if bonus["type"] == "level_up":
                        score += 20  
                        level_up(player)  
                    bonuses.pop(i)
           
            screen.blit(background_img, (0, 0))
            for obs in obstacles:
                screen.blit(obs["surf"], obs["rect"])
            player.draw_bullets(screen)

            for bonus in bonuses:
                screen.blit(bonus["surf"], bonus["rect"])

            heart_w, heart_h = heart_img.get_size()
            hearts_x = WIDTH - (player.lives * (heart_w + 4)) - 4
            hearts_y = 4
            for i in range(max(0, player.lives)):
                screen.blit(heart_img, (hearts_x + i * (heart_w + 4), hearts_y))


            if invincible_now % 10 < 5:
                screen.blit(player.surf, player.rect)

            font = pygame.font.SysFont(None, 40)
            score_text = font.render(f"Score: {score}", True, (255,255,255))
            screen.blit(score_text, (10, 10))

            bullets_text = font.render(f"Bullets: {player.bullet_storage}/{player.max_bullet_storage}", True, (255,255,255))
            screen.blit(bullets_text, (10, 50))

            pygame.display.flip()

        show_game_over_screen(score)

if __name__ == "__main__":
    main()