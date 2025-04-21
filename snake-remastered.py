import pygame
import random
import sys
import psycopg2

# Инициализация Pygame
pygame.init()

# Параметры экрана
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20

# Цвета
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Строка подключения к базе данных Neon
def connect_to_db():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_HxW3O1qkKeSB@ep-sparkling-surf-a2klbu0n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    )

# Функция для создания таблиц в базе данных, если их нет
def create_tables():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Создаем таблицу пользователей, если она не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            current_level INT DEFAULT 1,
            current_score INT DEFAULT 0
        );
    """)

    # Создаем таблицу с историей очков, если она не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_scores (
            user_id INT REFERENCES users(id),
            score INT,
            level INT,
            score_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, score_date)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Функция для сохранения данных в базе данных
def save_game_state(username, score, level):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:  # Если пользователя нет, создаем нового
        cursor.execute("INSERT INTO users (username, current_level, current_score) VALUES (%s, %s, %s) RETURNING id",
                       (username, level, score))
        user_id = cursor.fetchone()[0]
    else:
        user_id = user[0]
        cursor.execute("UPDATE users SET current_level = %s, current_score = %s WHERE id = %s", 
                       (level, score, user_id))
    
    cursor.execute("INSERT INTO user_scores (user_id, score, level) VALUES (%s, %s, %s)",
                   (user_id, score, level))
    
    conn.commit()
    cursor.close()
    conn.close()

# Функция для загрузки данных пользователя из базы данных
def load_user_data(username):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT current_level, current_score FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user_data:
        return user_data  # Возвращает (уровень, очки)
    return None  # Пользователь не найден

# Функция для получения имени пользователя
def get_username():
    input_box = pygame.Rect(200, 150, 140, 32)  # Поле ввода
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font(None, 32)
    txt_surface = font.render(text, True, color)
    prompt_text = font.render("Enter your username:", True, WHITE)

    while True:
        screen.fill(BLACK)
        screen.blit(prompt_text, (200, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text, 1, 0  # Пример возврата с начальными значениями
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                    txt_surface = font.render(text, True, color)

        # Рисуем поле ввода
        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))

        pygame.display.flip()
        clock.tick(30)

# Функция для генерации пищи в случайном месте
def generate_food(snake):
    while True:
        food = (random.randrange(0, SCREEN_WIDTH, CELL_SIZE), random.randrange(0, SCREEN_HEIGHT, CELL_SIZE))
        if food not in snake:
            return food

# Главный цикл игры
def run_game():
    # Создание таблиц, если их нет
    create_tables()

    # Получение имени пользователя и загрузка данных
    username, level, score = get_username()

    # Инициализация переменной скорости
    speed = 10  # Начальная скорость игры

    # Начальная змейка
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = (CELL_SIZE, 0)
    food = generate_food(snake)
    food_timer = pygame.time.get_ticks()
    food_value = random.choice([1, 2, 3])
    
    running = True
    while running:
        screen.fill(BLACK)

        # Обработка событий
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
                elif event.key == pygame.K_p:  # Паузить игру и сохранить прогресс
                    save_game_state(username, score, level)
                    print(f"Game saved! Score: {score}, Level: {level}")

        # Перемещение змеи
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        
        # Проверка столкновений со стенами или самой собой
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or 
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or 
            new_head in snake):
            running = False
        
        snake.insert(0, new_head)

        # Генерация новой пищи, но только если она съедена
        if new_head == food:
            score += food_value
            food = generate_food(snake)
            if score % 5 == 0:
                level += 1
                speed = 10 + level  # Увеличение скорости с каждым уровнем
        else:
            snake.pop()  # Убираем хвост змеи

        # Рисуем пищу
        if food_value == 1:
            food_color = RED
        elif food_value == 2:
            food_color = YELLOW
        else:
            food_color = WHITE
        pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))

        # Рисуем змейку
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

        # Отображаем очки и уровень
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))

        pygame.display.flip()
        clock.tick(speed)  # Скорость игры зависит от уровня

    # Сохранение состояния игры при выходе
    save_game_state(username, score, level)
    print(f"Game saved! Final Score: {score}, Level: {level}")

    pygame.quit()
    sys.exit()

# Запуск игры
run_game()
