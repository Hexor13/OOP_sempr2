#resources

import pygame
import sys
from parametrs import *

#parametrs for game window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceJet Game (Python)")
clock = pygame.time.Clock()

#load and save defin for images from recourses
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