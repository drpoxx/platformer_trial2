import pathlib
import random
import math
import pygame

pygame.init()

pygame.display.set_caption("Platformer")

# Set basic game configuration
BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VELOCITY = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1

    def __init__(self, x, y, width, height):
        # Configure the rect.
        self.rect = pygame.Rect(x, y, width, height)
        # Configure the velocities.
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, velocity):
        self.x_velocity = -velocity
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.x_velocity = velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
        # Handles things that need to be done constantly for the character.
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        self.fall_count += 1


    def draw(self, window):
        pygame.draw.rect(window, self.COLOR, self.rect)

def get_background(name):
    """
    Function to get the background based on the background types available in the assets folder.

    Args:
        name (str): File name as a string (i.e. *.png, *.jpg) needs to be in the assets/Background folder.

    Returns:
        list: Returns the tiles and the background image.
    """
    image = pygame.image.load(pathlib.Path.cwd().joinpath("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height +1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)

    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VELOCITY)
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    player = Player(100, 100, 50, 50)

    run = True
    while run:
        # Regulate the framerate across different devices.
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_image, player)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)