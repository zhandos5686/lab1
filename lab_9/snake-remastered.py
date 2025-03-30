import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)  # Special food color

# Game variables
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL_SIZE, 0)
food = None
food_timer = 0
food_value = 1  # Default food weight
score = 0
level = 1
speed = 10

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Function to generate food in a valid position
def generate_food():
    global food_timer, food_value
    food_timer = pygame.time.get_ticks()  # Set timer for food disappearance
    food_value = random.choice([1, 2, 3])  # Assign random weight to food
    while True:
        new_food = (random.randrange(0, SCREEN_WIDTH, CELL_SIZE), 
                    random.randrange(0, SCREEN_HEIGHT, CELL_SIZE))
        if new_food not in snake:
            return new_food

# Generate the first food
food = generate_food()

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)
    
    # Move the snake
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    
    # Check for collision with walls or itself
    if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or 
        new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or 
        new_head in snake):
        running = False
    
    snake.insert(0, new_head)

    # Check if the food disappears after 5 seconds
    if pygame.time.get_ticks() - food_timer > 5000:  # 5 seconds
        food = generate_food()

    # Check for food collision
    if new_head == food:
        score += food_value  # Increase score based on food weight
        food = generate_food()
        if score % 5 == 0:
            level += 1
            speed += 2  # Increase speed every 5 points
    else:
        snake.pop()  # Remove last segment if no food eaten

    # Draw food (different colors based on weight)
    if food_value == 1:
        food_color = RED
    elif food_value == 2:
        food_color = YELLOW
    else:
        food_color = WHITE

    pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))
    
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
    
    # Display score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
sys.exit()
