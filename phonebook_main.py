import psycopg2
import csv

DATABASE_URL = "postgresql://neondb_owner:npg_HxW3O1qkKeSB@ep-sparkling-surf-a2klbu0n-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

def connect():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_manual():
    name = input("Введите имя: ")
    phone = input("Введите номер телефона: ")
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("✅ Контакт добавлен.")
    cur.close()
    conn.close()

def insert_from_csv():
    filename = input("Введите имя CSV-файла (например: contacts.csv): ")
    try:
        conn = connect()
        cur = conn.cursor()
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропуск заголовка
            for row in reader:
                if len(row) == 2:
                    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
        conn.commit()
        print("📥 Данные из CSV загружены.")
        cur.close()
        conn.close()
    except FileNotFoundError:
        print("❌ Файл не найден.")

def update_contact():
    name = input("Введите имя контакта для обновления: ")
    new_phone = input("Введите новый номер: ")
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    print("✏️ Контакт обновлён.")
    cur.close()
    conn.close()

def search_contacts():
    print("Фильтры:\n1 - По имени\n2 - По номеру")
    choice = input("Выбор: ")
    conn = connect()
    cur = conn.cursor()
    if choice == "1":
        name = input("Введите имя: ")
        cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + name + '%',))
    elif choice == "2":
        phone = input("Введите часть номера: ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", ('%' + phone + '%',))
    else:
        print("❌ Неверный выбор.")
        return
    rows = cur.fetchall()
    print("🔎 Найденные контакты:")
    for row in rows:
        print(f"ID: {row[0]} | Имя: {row[1]} | Телефон: {row[2]}")
    cur.close()
    conn.close()

def delete_contact():
    print("Удалить по:\n1 - Имени\n2 - Телефону")
    choice = input("Выбор: ")
    conn = connect()
    cur = conn.cursor()
    if choice == "1":
        name = input("Введите имя: ")
        cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
    elif choice == "2":
        phone = input("Введите номер: ")
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
    else:
        print("❌ Неверный выбор.")
        return
    conn.commit()
    print("🗑️ Контакт удалён.")
    cur.close()
    conn.close()

def show_all():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()
    print("📇 Все контакты:")
    for row in rows:
        print(f"ID: {row[0]} | Имя: {row[1]} | Телефон: {row[2]}")
    cur.close()
    conn.close()

def main_menu():
    create_table()
    while True:
        print("\n📱 Меню PhoneBook:")
        print("1 - Добавить контакт вручную")
        print("2 - Загрузить контакты из CSV")
        print("3 - Обновить контакт")
        print("4 - Найти контакты")
        print("5 - Удалить контакт")
        print("6 - Показать все контакты")
        print("0 - Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            insert_manual()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            search_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            show_all()
        elif choice == "0":
            print("👋 Выход из программы.")
            break
        else:
            print("❌ Неверный выбор.")

if __name__ == "__main__":
    main_menu()
