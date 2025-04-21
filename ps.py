import psycopg2

# Строка подключения для Neon PostgreSQL
conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_HxW3O1qkKeSB@ep-sparkling-surf-a2klbu0n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"
)
cursor = conn.cursor()

# SQL код для создания функции
cursor.execute("""
    CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
    RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone_number VARCHAR) AS
    $$
    BEGIN
        RETURN QUERY
        SELECT id, first_name, last_name, phone_number
        FROM phonebook
        WHERE first_name ILIKE '%' || pattern || '%'
           OR last_name ILIKE '%' || pattern || '%'
           OR phone_number ILIKE '%' || pattern || '%';
    END;
    $$ LANGUAGE plpgsql;
""")

# Подтверждаем изменения в базе данных
conn.commit()

# Закрываем соединение
cursor.close()
conn.close()

print("Function 'search_phonebook' created successfully!")
