import pygame
import random
import sys

#game parametrs
WIDTH, HEIGHT = 1000, 980
FPS = 60
ADD_OBSTACLES_TIMER = 150
INVINCIBLE_TIMER = 100
PLANE_SPEED = 5
OBSTACLE_SPEED = 7
COLUMNS = 10
OBSTACLE_SIZE = 50
MAX_OBSTACLE_SPEED = 25
MIN_BONUS_TIME = 300
MAX_BONUS_TIME = 500
BONUS_SPEED = 5
CLOUD_WARNING_TIME = 90
CLOUD_DURATION = 1000
CLOUD_SPEED = 3
CLOUD_SPAWN_MIN = 100
CLOUD_SPAWN_MAX = 300
MAX_PLANE_SPEED = 10
BOOST_SPEED_MULTIPLIER = 2.0
BOOST_MAX = 500
BOOST_DRAIN_RATE = 1.0

#images 
PLANE_FILE = "resources/pngwing.com.png"
OBSTACLE_FILE = "resources/pngegg.png"
BACKGROUND_FILE = "resources/space2.jpg"
#BACKGROUND_FILE = "resources/start_screen_CZ.png" #EASTER EGG :D
#BACKGROUND_FILE = "resources/start_screen_RUS.png" #EASTER EGG 2 :D
GAMEOVER_FILE = "resources/game_over.png"
HEART_FILE = "resources/heart.png"
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
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
gameover_img = load_image(GAMEOVER_FILE)
heart_img = load_image(HEART_FILE)
bonus_img = load_image(BONUS_FILE)

def generate_new_obstacles(size, texture_surface):
    res = []
    obstacle_num = COLUMNS
    available_positions = list(range(obstacle_num))
    selected_positions = random.sample(available_positions, obstacle_num - 2)
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

def show_pause_screen(screen_snapshot):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(screen_snapshot, (0, 0))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont(None, 60)
    pause_text = font.render("PAUSED", True, (255, 255, 100))
    screen.blit(pause_text, (WIDTH//2 - 100, HEIGHT//2 - 100))
    
    font_small = pygame.font.SysFont(None, 36)
    instruction = font_small.render("press esc to continue", True, (200, 200, 200))
    screen.blit(instruction, (WIDTH//2 - 150, HEIGHT//2))
    
    pygame.display.flip()
    
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
        clock.tick(FPS)

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
        self.lives = 1                    #<---- TEST PARAMETR
        self.size_factor = 1.0
        self.speed = speed 
        self.base_speed = speed
        self.boost_active = False
        self.boost_amount = BOOST_MAX
        self.max_boost = BOOST_MAX
        self.upgrade_count = 0

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
    
    def update_size(self):
        new_width = int(self.original_surf.get_width() * self.size_factor)
        new_height = int(self.original_surf.get_height() * self.size_factor)
        self.surf = pygame.transform.scale(self.original_surf, (new_width, new_height))
        
        center = self.rect.center
        self.rect = self.surf.get_rect(center=center)
    
    def refill_bullets(self, amount):
        self.bullet_storage = min(self.max_bullet_storage, self.bullet_storage + amount)

    def increase_speed(self, amount):
        self.speed = min(self.speed + amount, MAX_PLANE_SPEED)
        self.base_speed = self.speed

    def refill_boost(self):
        self.boost_amount = self.max_boost
    
class Bullet:
    def __init__(self, pos):
        self.surf = pygame.Surface((5, 15))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect(midbottom=pos)
        self.speed = -15                #<---- TEST PARAMETR
        
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
    
    def check_collision(self, player_rect, player_surf):
        if not self.active or self.warning:
            return False
            
        for meteor in self.meteors:
            if pixel_collision(player_surf, player_rect, meteor["surf"], meteor["rect"]):
                return True
        return False
    
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

def show_start_screen():
    button_width, button_height = 300, 80 
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2 + 350
    button_color = (50, 150, 255)
    button_hover_color = (80, 180, 255)
    text_color = (255, 255, 255)
    title_font = pygame.font.SysFont(None, 80)
    button_font = pygame.font.SysFont(None, 50)
    plane_on_menu = plane_img
    plane_rect = plane_on_menu.get_rect(center=(WIDTH//2, HEIGHT//2))

    showing = True
    while showing:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    showing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovering = button_rect.collidepoint(mouse_pos)
        screen.blit(background_img, (0, 0))
        title = title_font.render("SPACE JET", True, (255, 255, 100))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        screen.blit(plane_on_menu, plane_rect)
        current_color = button_hover_color if is_hovering else button_color
        pygame.draw.rect(screen, current_color, button_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=15)
        button_text = button_font.render("START GAME", True, text_color)
        screen.blit(button_text, 
                   (button_x + button_width//2 - button_text.get_width()//2,
                    button_y + button_height//2 - button_text.get_height()//2))
        if is_hovering and mouse_clicked:
            showing = False
        
        pygame.display.flip()
        clock.tick(FPS)

def show_game_over_screen(score,meteors_destroyed, game_duration, player):
    showing = True
    font = pygame.font.SysFont(None, 60)
    stat_font = pygame.font.SysFont(None, 40)
    text_surf = font.render(f"Score: {score}", True, (255,255,255))
    wait_time = 2500
    start_time = pygame.time.get_ticks()
    continue_play = False
    actual_level = player.upgrade_count

    while showing:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        if elapsed >= wait_time:
            continue_play = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if continue_play:
                    showing = False
        screen.blit(background_img, (0,0))
        go_rect = gameover_img.get_rect(center=(WIDTH//2, HEIGHT//2 -250  ))
        screen.blit(gameover_img, go_rect)
        screen.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 130)))

        stat1_text = stat_font.render(f"Meteors destroyed: {meteors_destroyed}", True, (255,255,255))
        screen.blit(stat1_text, (WIDTH//2 - stat1_text.get_width()//2, HEIGHT//2 + 170))
        
        stat2_text = stat_font.render(f"Game time: {game_duration} seconds", True, (255,255,255))
        screen.blit(stat2_text, (WIDTH//2 - stat2_text.get_width()//2, HEIGHT//2 + 210))

        stat3_text = stat_font.render(f"Level: {actual_level}", True, (255,255,255))
        screen.blit(stat3_text, (WIDTH//2 - stat3_text.get_width()//2, HEIGHT//2 + 250))

        hint = font.render("Press any key to restart", True, (255, 255, 55))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 100))

        pygame.display.flip()
        clock.tick(FPS)

def level_up(player, screen_snapshot=None):
    font = pygame.font.SysFont(None, 40)
    screen.fill((0, 0, 0))

    if screen_snapshot is not None:
        screen.blit(screen_snapshot, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        screen.blit(overlay, (0, 0))
    

    menu_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)
    pygame.draw.rect(screen, (30, 30, 60), menu_rect)
    pygame.draw.rect(screen, (100, 100, 200), menu_rect, 4)
    title_font = pygame.font.SysFont(None, 50)
    title = title_font.render("LEVEL UP!", True, (255, 255, 100))
    screen.blit(title, (WIDTH//2 - 100, HEIGHT//2 - 180))

    options = [
        "1) Smaller hitbox",
        "2) +1 life", 
        "3) +5 bullets to storage",
        "4) +1 permanent speed",
        "5) Refill boost"
    ]
    
    for i, option in enumerate(options):
        txt = font.render(option, True, (255,255,0))
        screen.blit(txt, (WIDTH//2 - 180, HEIGHT//2 - 100 + i*60))
    
    pygame.display.flip()
    
    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.size_factor *= 0.9
                    player.update_size()
                    player.upgrade_count += 1
                    choosing = False
                elif event.key == pygame.K_2:
                    player.lives += 1
                    player.upgrade_count += 1
                    choosing = False
                elif event.key == pygame.K_3:
                    player.refill_bullets(5)
                    player.upgrade_count += 1
                    choosing = False
                elif event.key == pygame.K_4:
                    player.increase_speed(1)
                    player.upgrade_count += 1
                    choosing = False
                elif event.key == pygame.K_5:
                    player.refill_boost()
                    player.upgrade_count += 1
                    choosing = False
        clock.tick(FPS)

def main():
    while True:
        show_start_screen()
        player = Plane((WIDTH//2, HEIGHT//2), PLANE_SPEED)
        obstacles = generate_new_obstacles(OBSTACLE_SIZE, obstacle_img)
        add_obstacles_now = 0
        bonuses = []  
        add_bonus_now = 0  
        next_bonus_time = random.randint(MIN_BONUS_TIME, MAX_BONUS_TIME)
        invincible_now = 0
        score = 0
        level_thresholds = [100,  200, 300,400,500,600 ]          #<---- TEST PARAMETR
        current_level_index = 0
        obs_speed = min(OBSTACLE_SPEED, MAX_OBSTACLE_SPEED)
        meteor_cloud = MeteorCloud(WIDTH, HEIGHT)
        game_start_time = pygame.time.get_ticks()
        meteors_destroyed = 0

        running = True
        frame_counter = 0
        cloud_spawn_counter = 0
        next_cloud_spawn = random.randint(CLOUD_SPAWN_MIN, CLOUD_SPAWN_MAX)
        
        while running:
            clock.tick(FPS)
            frame_counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        screen_snapshot = screen.copy()
                        show_pause_screen(screen_snapshot)

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

            cloud_spawn_counter += 1
            if cloud_spawn_counter >= next_cloud_spawn and not meteor_cloud.active:
                meteor_cloud.activate()
                cloud_spawn_counter = 0
                next_cloud_spawn = random.randint(CLOUD_SPAWN_MIN, CLOUD_SPAWN_MAX)
            meteor_cloud.update()
            
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
                player.rect.topleft = (WIDTH//2, HEIGHT//2)
                if player.lives <= 0:
                    running = False
            
            if meteor_cloud.check_collision(player.rect, player.surf):
                if invincible_now >= INVINCIBLE_TIMER:
                    player.lives -= 1
                    invincible_now = 0
                    player.rect.topleft = (WIDTH//2, HEIGHT//2)
                    if player.lives <= 0:
                        running = False

            if invincible_now < INVINCIBLE_TIMER:
                invincible_now += 1

            points_from_bullets, destroyed_count = player.update_bullets(obstacles)
            score += points_from_bullets
            meteors_destroyed += destroyed_count
           
            if current_level_index < len(level_thresholds) and score >= level_thresholds[current_level_index]:
                screen_snapshot = screen.copy()
                level_up(player,screen_snapshot)
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
                        screen_snapshot = screen.copy()
                        level_up(player,screen_snapshot)  
                    bonuses.pop(i)
           
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

            speed_font = pygame.font.SysFont(None, 30)
            speed_text = speed_font.render(f"Speed: {player.speed}", True, (255, 255, 255))
            screen.blit(speed_text, (WIDTH - 150, 40))
            

            if invincible_now % 10 < 5:
                screen.blit(player.surf, player.rect)

            font = pygame.font.SysFont(None, 40)
            score_text = font.render(f"Score: {score}", True, (255,255,255))
            screen.blit(score_text, (10, 10))

            bullets_text = speed_font.render(f"Bullets: {player.bullet_storage}/{player.max_bullet_storage}", True, (255,255,255))
            screen.blit(bullets_text, (WIDTH - 150, 70))

            pygame.display.flip()
        game_duration = (pygame.time.get_ticks() - game_start_time) // 1000
        show_game_over_screen(score,meteors_destroyed, game_duration, player)

if __name__ == "__main__":
    main()