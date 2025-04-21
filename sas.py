import psycopg2

# Строка подключения для Neon PostgreSQL
conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_HxW3O1qkKeSB@ep-sparkling-surf-a2klbu0n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"
)
cursor = conn.cursor()

# Вводим шаблон для поиска
pattern = 'John'

# Выполняем запрос с функцией поиска
cursor.execute("SELECT * FROM search_phonebook(%s)", (pattern,))

# Получаем и выводим результаты
rows = cursor.fetchall()
for row in rows:
    print(row)

# Закрываем соединение
cursor.close()
conn.close()
