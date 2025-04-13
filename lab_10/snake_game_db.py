import pygame
import random
import sys
import psycopg2
import json # To serialize/deserialize game state for DB storage
from db_config import get_db_params # Import your DB config function

# --- Database Functions ---

def connect_db():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = get_db_params()
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)
        print("Connection successful.")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to database: {error}")
        return None

def create_db_tables(conn):
    """ Create database tables if they don't exist """
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_scores (
            score_id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL, -- Ensures one saved state per user
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            snake_body TEXT NOT NULL,
            snake_direction TEXT NOT NULL,
            food_position TEXT NOT NULL,
            food_value INTEGER NOT NULL,
            saved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_username ON users(username);
        """
    )
    cur = None
    try:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit() # Commit table creation
        cur.close()
        print("Database tables checked/created successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating tables: {error}")
        conn.rollback() # Rollback on error
        if cur:
            cur.close()

def get_or_create_user(conn, username):
    """ Get user ID if exists, otherwise create new user """
    user_id = None
    sql_find = "SELECT user_id FROM users WHERE username = %s"
    sql_create = "INSERT INTO users(username) VALUES (%s) RETURNING user_id"
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql_find, (username,))
        result = cur.fetchone()
        if result:
            user_id = result[0]
            print(f"Welcome back, {username} (User ID: {user_id})!")
        else:
            cur.execute(sql_create, (username,))
            user_id = cur.fetchone()[0]
            conn.commit() # Commit user creation
            print(f"Created new user: {username} (User ID: {user_id})")
        cur.close()
        return user_id
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error finding/creating user: {error}")
        conn.rollback()
        if cur:
            cur.close()
        return None

def load_game_state(conn, user_id):
    """ Load the last saved game state for the user """
    sql_load = """
        SELECT score, level, speed, snake_body, snake_direction, food_position, food_value
        FROM user_scores
        WHERE user_id = %s
    """
    # ORDER BY saved_at DESC LIMIT 1; -- Use this if you allow multiple saves and want the latest
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql_load, (user_id,))
        state = cur.fetchone()
        cur.close()
        if state:
            print(f"Loading saved game state for User ID: {user_id}...")
            # Deserialize JSON data from TEXT columns
            loaded_snake = [tuple(pos) for pos in json.loads(state[3])] # Convert lists back to tuples
            loaded_direction = tuple(json.loads(state[4]))
            loaded_food = tuple(json.loads(state[5]))
            return {
                'score': state[0],
                'level': state[1],
                'speed': state[2],
                'snake': loaded_snake,
                'direction': loaded_direction,
                'food': loaded_food,
                'food_value': state[6]
            }
        else:
            print(f"No saved game state found for User ID: {user_id}. Starting new game.")
            return None # No saved state
    except (Exception, psycopg2.DatabaseError, json.JSONDecodeError) as error:
        print(f"Error loading game state: {error}")
        if cur:
            cur.close()
        return None # Error loading state

def save_game_state(conn, user_id, score, level, speed, snake, direction, food, food_value):
    """ Save the current game state for the user, overwriting previous save """
    sql_save = """
        INSERT INTO user_scores (user_id, score, level, speed, snake_body, snake_direction, food_position, food_value, saved_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET
            score = EXCLUDED.score,
            level = EXCLUDED.level,
            speed = EXCLUDED.speed,
            snake_body = EXCLUDED.snake_body,
            snake_direction = EXCLUDED.snake_direction,
            food_position = EXCLUDED.food_position,
            food_value = EXCLUDED.food_value,
            saved_at = CURRENT_TIMESTAMP;
    """
    cur = None
    try:
        cur = conn.cursor()
        # Serialize Python lists/tuples to JSON strings for TEXT columns
        snake_json = json.dumps(snake)
        direction_json = json.dumps(direction)
        food_json = json.dumps(food)

        cur.execute(sql_save, (user_id, score, level, speed, snake_json, direction_json, food_json, food_value))
        conn.commit() # Commit the save
        cur.close()
        print("Game state saved successfully.")
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error saving game state: {error}")
        conn.rollback()
        if cur:
            cur.close()
        return False

# --- Game Code ---
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
YELLOW = (255, 255, 0) # Special food color
BLUE = (0, 0, 255) # Pause message color
GREY = (128, 128, 128) # Wall color (example)

# Game variables - Default values
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL_SIZE, 0) # Start moving right
food = None
food_timer = 0
food_value = 1  # Default food weight
score = 0
level = 1
speed = 10 # Initial speed
current_user_id = None
paused = False
message = None # For displaying save/pause messages
message_timer = 0

# Walls - Example for Level 2+ (customize as needed)
walls = []
def setup_level(level_num):
    """ Define walls based on level """
    global walls
    walls = [] # Clear previous walls
    if level_num == 2:
        # Add a simple border inside the screen
        for x in range(CELL_SIZE, SCREEN_WIDTH - CELL_SIZE, CELL_SIZE):
            walls.append((x, CELL_SIZE)) # Top
            walls.append((x, SCREEN_HEIGHT - CELL_SIZE*2)) # Bottom
        for y in range(CELL_SIZE*2, SCREEN_HEIGHT - CELL_SIZE*2, CELL_SIZE):
            walls.append((CELL_SIZE, y)) # Left
            walls.append((SCREEN_WIDTH - CELL_SIZE*2, y)) # Right
    elif level_num >= 3:
         # Level 2 walls plus a center obstacle
        setup_level(2) # Get level 2 walls
        for y in range(SCREEN_HEIGHT // 2 - CELL_SIZE*2, SCREEN_HEIGHT // 2 + CELL_SIZE*2, CELL_SIZE):
             walls.append((SCREEN_WIDTH // 2 - CELL_SIZE // 2, y))
    # Add more levels here...

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game - Database Edition")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Function to generate food in a valid position (avoiding snake and walls)
def generate_food():
    global food_timer, food_value
    food_timer = pygame.time.get_ticks() # Reset timer
    food_value = random.choice([1, 2, 3]) # Assign random weight
    while True:
        new_food = (random.randrange(0, SCREEN_WIDTH // CELL_SIZE) * CELL_SIZE,
                    random.randrange(0, SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE)
        if new_food not in snake and new_food not in walls:
            return new_food

def display_message(text, duration=1500):
    """ Sets a message to be displayed temporarily """
    global message, message_timer
    message = text
    message_timer = pygame.time.get_ticks() + duration

# --- Main Execution ---
if __name__ == '__main__':
    db_conn = connect_db()

    if not db_conn:
        print("Failed to connect to database. Exiting.")
        sys.exit()

    create_db_tables(db_conn)

    # Get username
    while current_user_id is None:
        username = input("Enter your username: ").strip()
        if username:
            current_user_id = get_or_create_user(db_conn, username)
            if current_user_id is None:
                print("Could not get or create user. Try again or check DB connection.")
                # Optional: exit here if user creation fails critically
        else:
            print("Username cannot be empty.")

    # Try to load game state
    loaded_state = load_game_state(db_conn, current_user_id)
    if loaded_state:
        score = loaded_state['score']
        level = loaded_state['level']
        speed = loaded_state['speed']
        snake = loaded_state['snake']
        direction = loaded_state['direction']
        food = loaded_state['food']
        food_value = loaded_state['food_value']
        food_timer = pygame.time.get_ticks() # Reset timer on load
        display_message(f"Loaded state: Level {level}, Score {score}", 2000)
    else:
        # Generate the first food if not loaded
        food = generate_food()
        display_message(f"Level {level}. Good luck!", 2000)

    setup_level(level) # Setup walls for the current level

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Optionally save state on quit? Or just exit?
                # save_game_state(db_conn, current_user_id, score, level, speed, snake, direction, food, food_value)
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: # Pause / Unpause
                    paused = not paused
                    if paused:
                         display_message("Paused. Press P to Resume, S to Save.", 10000) # Longer message
                    else:
                         display_message("Resumed.", 1000)
                elif paused and event.key == pygame.K_s: # Save while paused
                    if save_game_state(db_conn, current_user_id, score, level, speed, snake, direction, food, food_value):
                         display_message("Game Saved!", 1500)
                    else:
                         display_message("Error Saving Game!", 1500)
                    # Keep paused after saving, user must press P to resume

                # Handle movement only if not paused
                elif not paused:
                    if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                        direction = (0, -CELL_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                        direction = (0, CELL_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                        direction = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                        direction = (CELL_SIZE, 0)

        if paused:
            # --- Paused State Drawing ---
            screen.fill(BLACK) # Keep screen clear or show dimmed game?

             # Draw walls
            for wall_segment in walls:
                pygame.draw.rect(screen, GREY, (wall_segment[0], wall_segment[1], CELL_SIZE, CELL_SIZE))

            # Draw food
            if food_value == 1: food_color = RED
            elif food_value == 2: food_color = YELLOW
            else: food_color = WHITE
            pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))

            # Draw snake
            for segment in snake:
                pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

            # Display score and level
            score_text = font.render(f"Score: {score}", True, WHITE)
            level_text = font.render(f"Level: {level}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (10, 40))

            # Display Pause Message centrally
            pause_surf = font.render("PAUSED", True, BLUE)
            pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(pause_surf, pause_rect)

            # Display instructions below pause message
            instr_surf = small_font.render("P: Resume | S: Save", True, WHITE)
            instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(instr_surf, instr_rect)

            pygame.display.flip()
            clock.tick(10) # Lower tick rate when paused
            continue # Skip rest of the loop if paused

        # --- Game Logic (Runs if not paused) ---
        # Move the snake
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Check for collision with screen boundaries, self, or walls
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in snake or
            new_head in walls):
            print("Game Over! Collision detected.")
            # Save final state/score on game over
            save_game_state(db_conn, current_user_id, score, level, speed, snake, direction, food, food_value)
            display_message(f"Game Over! Final Score: {score}", 5000) # Show message longer
            running = False # End game loop
            # Keep showing the screen for a bit after game over message is set
            game_over_wait_start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - game_over_wait_start < 3000: # Wait 3 seconds
                 # Keep drawing the final state + message
                 screen.fill(BLACK)
                 for wall_segment in walls:
                    pygame.draw.rect(screen, GREY, (wall_segment[0], wall_segment[1], CELL_SIZE, CELL_SIZE))
                 if food_value == 1: food_color = RED
                 elif food_value == 2: food_color = YELLOW
                 else: food_color = WHITE
                 pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))
                 for segment in snake:
                    pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
                 score_text = font.render(f"Score: {score}", True, WHITE)
                 level_text = font.render(f"Level: {level}", True, WHITE)
                 screen.blit(score_text, (10, 10))
                 screen.blit(level_text, (10, 40))
                 if message and pygame.time.get_ticks() < message_timer: # Display game over message
                    msg_surf = font.render(message, True, RED) # Red for game over
                    msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    screen.blit(msg_surf, msg_rect)
                 pygame.display.flip()
                 pygame.event.pump() # Process events to prevent freezing
                 clock.tick(10)
            continue # Skip rest of the loop after game over handling


        snake.insert(0, new_head)

        # Check if the food disappears after 5 seconds
        if pygame.time.get_ticks() - food_timer > 5000: # 5 seconds
            food = generate_food()

        # Check for food collision
        if new_head == food:
            score += food_value # Increase score based on food weight
            food = generate_food() # Generate new food

            # Level Up Logic
            # Let's level up every 5 *points* accumulated *within the current level*
            # Or simply use the original logic: level up every 5 total score points
            if score // 5 >= level: # Simpler: if score hits 5, 10, 15 etc.
                level += 1
                speed += 2 # Increase speed
                setup_level(level) # Setup walls for the new level
                display_message(f"Level Up! Level {level}", 1500)
        else:
            snake.pop() # Remove last segment if no food eaten

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw walls
        for wall_segment in walls:
             pygame.draw.rect(screen, GREY, (wall_segment[0], wall_segment[1], CELL_SIZE, CELL_SIZE))

        # Draw food (different colors based on weight)
        if food_value == 1: food_color = RED
        elif food_value == 2: food_color = YELLOW
        else: food_color = WHITE
        pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))

        # Draw snake
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

        # Display score and level
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))

        # Display temporary messages (Save, Load, Level Up, etc.)
        if message and pygame.time.get_ticks() < message_timer:
            msg_surf = small_font.render(message, True, WHITE)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 20))
            screen.blit(msg_surf, msg_rect)
        elif message and pygame.time.get_ticks() >= message_timer:
            message = None # Clear expired message

        pygame.display.flip()
        clock.tick(speed) # Game speed controlled by the speed variable

    # --- Cleanup ---
    if db_conn:
        db_conn.close()
        print("Database connection closed.")

    pygame.quit()
    print("Game exited.")
    sys.exit()