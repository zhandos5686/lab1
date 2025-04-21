import psycopg2

# Строка подключения для вашей базы данных Neon
DATABASE_URL = "postgresql://neondb_owner:npg_HxW3O1qkKeSB@ep-sparkling-surf-a2klbu0n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

# Функция для подключения к базе данных
def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Функция для проверки подключения
def check_connection():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Выполнение простого SQL-запроса
        cur.execute("SELECT NOW();")  # Получаем текущее время на сервере
        current_time = cur.fetchone()
        print(f"Подключение успешно! Текущее время на сервере: {current_time[0]}")
        
        # Закрытие соединения
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка подключения: {e}")

# Запуск проверки
if __name__ == "__main__":
    check_connection()
