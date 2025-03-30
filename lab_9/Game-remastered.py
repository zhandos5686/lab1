import pygame, sys
from pygame.locals import *
import random, time

# Initializing pygame
pygame.init()

# Setting up FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0
COIN_THRESHOLD = 5  # Coins needed to increase enemy speed

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background image
background = pygame.image.load("AnimatedStreet.png")

# Create a screen
display_surface = pygame.display.set_mode((400, 600))
display_surface.fill(WHITE)
pygame.display.set_caption("Racer Game")

# Coin Class
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), random.randint(-600, -50))
        self.value = random.randint(1, 3)  # Each coin has a value of 1 to 3
    
    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()
    
    def reset_position(self):
        self.rect.top = random.randint(-600, -50)
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), self.rect.top)
        self.value = random.randint(1, 3)  # Assign a new random value

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
    
    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.bottom > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
    
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# Setting up Sprites
P1 = Player()
E1 = Enemy()
coins = pygame.sprite.Group()

# Generate multiple coins
for _ in range(3):
    coins.add(Coin())

# Creating Sprite Groups
enemies = pygame.sprite.Group()
enemies.add(E1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, *coins)

# Adding a new User event for speed increase
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
    # Event Handling
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    # Increase speed when collecting enough coins
    if COINS_COLLECTED >= COIN_THRESHOLD:
        SPEED += 1
        COINS_COLLECTED = 0  # Reset the coin counter after speed increase
    
    # Update screen
    display_surface.blit(background, (0, 0))
    scores = font_small.render(str(SCORE), True, BLACK)
    display_surface.blit(scores, (10, 10))
    coin_text = font_small.render(f"Coins: {COINS_COLLECTED}", True, BLACK)
    display_surface.blit(coin_text, (SCREEN_WIDTH - 100, 10))
    
    # Move and redraw all Sprites
    for entity in all_sprites:
        entity.move()
        display_surface.blit(entity.image, entity.rect)
    
    # Check for collision with coins
    collected_coins = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected_coins:
        COINS_COLLECTED += coin.value  # Increase coins based on their value
        coin.reset_position()
    
    # Check for collision with enemies
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(1)
        display_surface.fill(RED)
        display_surface.blit(game_over, (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()
    
    pygame.display.update()
    FramePerSec.tick(FPS)