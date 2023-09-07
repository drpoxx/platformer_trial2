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

def flip(sprites):
    """Function to flip the sprite images.

    Args:
        sprites (list): List of sprite.Sprite objects containing the images.

    Returns:
        List: Returns a list of flipped sprites.
    """
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(name1, name2, width, height, direction=False):
    # Set the path and files for all images.
    path = pathlib.Path.cwd().joinpath("assets", name1, name2).glob('**/*')
    images = [f for f in path if f.is_file()]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(image).convert_alpha()
        # Split the iamges into the animations.
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            # Drawing (blit) sprite sheet based on the location and the rect (desired frame).
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface=surface))
        
        # Handle the direction of the image based on condition (e.g., moving character left and right).
        if direction:
            all_sprites[image.stem + "_right"] = sprites
            all_sprites[image.stem + "_left"] = flip(sprites)
        else:
            all_sprites[image.stem] = sprites

    return all_sprites

def load_block(size, distance_selector_x=96, distance_selector_y=0):
    """
    Function to load the block 

    Args:
        size (int): Size of the block in the image (around 64)
        distance_selector_x (int, optional): Distance in the terrain image on the x axis (selector). Defaults to 96.
        distance_selector_y (int, optional): Distance in the terrain image on the y axis (selector). Defaults to 0.

    Returns:
        pygame.object: The image is scaled two times (larger)
    """
    path = pathlib.Path.cwd().joinpath("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # NOTE: This depends on the image field and here we can play with the input. We can adjust the x and y point through the function
    rect = pygame.Rect(distance_selector_x, distance_selector_y, size, size)
    surface.blit(image, (0, 0), rect)
    # Returns a scaled image (enlarged x2)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        # Configure the rect.
        self.rect = pygame.Rect(x, y, width, height)
        # Configure the velocities.
        self.x_velocity = 0
        self.y_velocity = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        # Reverts the gravity to jump up - jump up and gravity goes down.
        self.y_velocity = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            # Remove gravity that was accumulated.
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
        # Handles things that need to be done constantly for the character. Start falling slow and increase pace.
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)
        # Increase the speed falling.
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_velocity = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        # Reverse the upwards movement to get the most natural effect.
        self.y_velocity *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.y_velocity < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_velocity != 0:
            sprite_sheet = "run"
        
        # if sprite_sheet == "jump" or sprite_sheet == "double_jump" or sprite_sheet == "fall":
        #     sprite_sheet_name = sprite_sheet
        # else:
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        # Show a different animation every ANIMATION_DELAY seconds (e.g., 5 seconds)
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # Pixel mapping of all the pixels in the sprite. Super relevant for pixel pefect collision.
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

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

def draw(window, background, bg_image, player, objects, offset_x):
    """Function to draw the game objects.

    Args:
        window (pygame.display): Window pygame display object.
        background (image): The index of the respected background that is to be selected from the bg_image.
        bg_image (image): background image.
        player (gygame.sprite.Sprite): Player sprite object.
        objects (pygame.sprite.Sprite): Objects sprite object.
    """
    for tile in background:
        window.blit(bg_image, tile)

    for object in objects:
        object.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0:
                player.rect.bottom = object.rect.top
                # Function to handle landing.
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                # Function to handle hit head.
                player.hit_head()

        collided_objects.append(object)
    return collided_objects

def collide(player, objects, dx):

    # Always handle the horizontal collision first. Vertical collision is handled second.
    # Check if the player were to move to the left or to the right - will that cause a collision.
    player.move(dx, 0)
    player.update()
    collide_object = None
    for obj in objects :
        if pygame.sprite.collide_mask(player, obj):
            collide_object = obj
            break
    # After the collision check the player is moved back since the player hasn't actually moved.
    player.move(-dx, 0)
    player.update()
    return collide_object


def handle_move(player, objects):
    """Function to handle the player movement of the player object.

    Args:
        player (pygame.sprite.Sprite): Pygame player sprite object.
    """
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    # Check for the horizontal collisions (set a little space to the block since sprite are slightly shifting).
    collide_left = collide(player, objects, -PLAYER_VELOCITY * 2 )
    collide_right = collide(player, objects, PLAYER_VELOCITY * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VELOCITY)

    # Handle the vertiical colisions
    handle_vertical_collision(player, objects, player.y_velocity)

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    # Introduce floor left and right of the map.
    floor =[Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    # *floor breaks floor down in it's individual elements being passed into the list below.
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size)]

    # Scrolling offset
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        # Regulate the framerate across different devices.
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            # Handle jumping here and not in handle movement since the event loop will avoid that the play can keep the jump key pressed to fly up.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # Screen scrolling
        if (((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_velocity > 0) or (
                (player.rect.left - offset_x <= WIDTH - scroll_area_width) and player.x_velocity < 0)):
            offset_x += player.x_velocity
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)