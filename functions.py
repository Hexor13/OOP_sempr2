#fuctions
import pygame
import sys
import random
from parametrs import * 
from resources_f import *
from classes import *


# collisions ang generation

def generate_new_obstacles(size, texture_surface):
    res = []
    obstacle_num = COLUMNS
    available_positions = list(range(obstacle_num))
    selected_positions = random.sample(available_positions, obstacle_num - 2) # -2 to differnet way to avoid obstacle
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
#calculate collisions between 2 rectangles(hitboxes)
def pixel_collision(surf1, rect1, surf2, rect2):
    mask1 = pygame.mask.from_surface(surf1)
    mask2 = pygame.mask.from_surface(surf2)
    offset = (rect2.left - rect1.left, rect2.top - rect1.top)
    return mask1.overlap(mask2, offset) is not None

#screens

def show_pause_screen(screenshot):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(screenshot, (0, 0)) 
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
    #draw plane, name of game, play button 
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
    #draw stats and keys to restart 
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

#level

def level_up(player, screenshot=None):
    font = pygame.font.SysFont(None, 40)
    screen.fill((0, 0, 0))

    if screenshot is not None:
        screen.blit(screenshot, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        screen.blit(overlay, (0, 0))
    #draw menu for updates
    menu_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)
    pygame.draw.rect(screen, (30, 30, 60), menu_rect)
    pygame.draw.rect(screen, (100, 100, 200), menu_rect, 4)
    title_font = pygame.font.SysFont(None, 50)
    title = title_font.render("LEVEL UP!", True, (255, 255, 100))
    screen.blit(title, (WIDTH//2 - 100, HEIGHT//2 - 180))
    #updates
    options = [
        "1) Smaller hitbox",
        "2) +1 life", 
        "3) +5 bullets to storage",
        "4) +1 permanent speed",
        "5) Refill boost"
    ]
    #cyklus to draw updates 
    for i, option in enumerate(options):
        txt = font.render(option, True, (255,255,0))
        screen.blit(txt, (WIDTH//2 - 180, HEIGHT//2 - 100 + i*60))
    
    pygame.display.flip()
    # choose update with buttons 1;2;3;4;5
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