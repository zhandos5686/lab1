import psycopg2
import csv
from db_config import get_db_params # Import config function

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # Read connection parameters
        params = get_db_params()

        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.autocommit = True # Automatically commit changes for simplicity here
                               # For complex transactions, manage commits explicitly

        # Create a cursor
        cur = conn.cursor()

        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)

        # Close the communication with the PostgreSQL
        cur.close()
        return conn # Return the connection object

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error connecting to database:")
        print(error)
        if conn is not None:
            conn.close()
            print('Database connection closed due to error.')
        return None # Indicate connection failure

def create_tables(conn):
    """ Create persons and phone_numbers tables """
    commands = (
        """
        DROP TABLE IF EXISTS phone_numbers;
        """,
        """
        DROP TABLE IF EXISTS persons CASCADE;
        """,
        """
        CREATE TABLE persons (
            person_id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100)
        )
        """,
        """
        CREATE TABLE phone_numbers (
            phone_id SERIAL PRIMARY KEY,
            person_id INTEGER NOT NULL,
            phone_number VARCHAR(25) NOT NULL UNIQUE, -- Make phone numbers unique
            phone_type VARCHAR(50),
            CONSTRAINT fk_person
                FOREIGN KEY(person_id)
                REFERENCES persons(person_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_phone_number ON phone_numbers(phone_number);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_person_name ON persons(first_name, last_name);
        """
    )
    cur = None
    try:
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        print("Tables created successfully (or already exist).")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error creating tables:")
        print(error)
    finally:
        if cur is not None:
            cur.close()

# --- Insertion Functions ---

def insert_contact(conn, first_name, last_name, phone_number, phone_type='Mobile'):
    """ Inserts a new person and their phone number """
    sql_insert_person = """
        INSERT INTO persons(first_name, last_name)
        VALUES(%s, %s) RETURNING person_id;
    """
    sql_insert_phone = """
        INSERT INTO phone_numbers(person_id, phone_number, phone_type)
        VALUES(%s, %s, %s);
    """
    cur = None
    person_id = None
    try:
        cur = conn.cursor()

        # Insert person
        cur.execute(sql_insert_person, (first_name, last_name))
        person_id = cur.fetchone()[0]
        print(f"Inserted person '{first_name} {last_name}' with ID: {person_id}")

        # Insert phone number
        cur.execute(sql_insert_phone, (person_id, phone_number, phone_type))
        print(f"Inserted phone number '{phone_number}' for person ID: {person_id}")

        return person_id

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting contact {first_name} {last_name}:")
        print(error)
        conn.rollback() # Rollback changes on error if autocommit=False
        return None
    finally:
        if cur is not None:
            cur.close()

def insert_from_console(conn):
    """ Get user input from console and insert contact """
    print("\nEnter new contact details:")
    try:
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name (optional): ").strip()
        phone_number = input("Enter phone number: ").strip()
        phone_type = input("Enter phone type (e.g., Mobile, Home, Work - default Mobile): ").strip()

        if not first_name:
            print("First name cannot be empty.")
            return
        if not phone_number:
            print("Phone number cannot be empty.")
            return

        if not phone_type:
            phone_type = 'Mobile' # Default value

        insert_contact(conn, first_name, last_name or None, phone_number, phone_type) # Use None if last_name is empty

    except EOFError:
        print("\nInput cancelled.")
    except Exception as e:
        print(f"An error occurred during input: {e}")


def insert_from_csv(conn, file_path):
    """ Insert contacts from a CSV file """
    print(f"\nAttempting to load contacts from {file_path}...")
    inserted_count = 0
    skipped_count = 0
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) # Skip header row
            print(f"CSV Header: {header}")

            for row in reader:
                try:
                    # Assuming CSV format: first_name,last_name,phone_number,phone_type
                    if len(row) >= 3:
                        first_name = row[0].strip()
                        last_name = row[1].strip() or None
                        phone_number = row[2].strip()
                        phone_type = row[3].strip() if len(row) > 3 and row[3].strip() else 'Mobile'

                        if first_name and phone_number:
                            person_id = insert_contact(conn, first_name, last_name, phone_number, phone_type)
                            if person_id:
                                inserted_count += 1
                            else:
                                print(f"Skipping row due to insertion error: {row}")
                                skipped_count += 1
                        else:
                            print(f"Skipping row due to missing required fields: {row}")
                            skipped_count += 1
                    else:
                         print(f"Skipping row due to insufficient columns: {row}")
                         skipped_count += 1
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    skipped_count += 1

        print(f"\nCSV Upload Summary:")
        print(f"  Successfully inserted: {inserted_count}")
        print(f"  Skipped/Errors:      {skipped_count}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")

# --- Update Functions ---

def update_person_name(conn, old_first_name, old_last_name, new_first_name, new_last_name):
    """ Updates a person's name based on their old name """
    sql_update = """
        UPDATE persons
        SET first_name = %s, last_name = %s
        WHERE first_name = %s AND (last_name = %s OR (last_name IS NULL AND %s IS NULL));
    """
    cur = None
    updated_rows = 0
    try:
        cur = conn.cursor()
        cur.execute(sql_update, (new_first_name, new_last_name, old_first_name, old_last_name, old_last_name))
        updated_rows = cur.rowcount
        if updated_rows > 0:
            print(f"Successfully updated {updated_rows} record(s) for '{old_first_name} {old_last_name or ''}' to '{new_first_name} {new_last_name or ''}'.")
        else:
            print(f"No person found matching '{old_first_name} {old_last_name or ''}'. No update performed.")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error updating person name:")
        print(error)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return updated_rows

def update_phone_number(conn, old_phone_number, new_phone_number):
    """ Updates a phone number """
    sql_update = """ UPDATE phone_numbers SET phone_number = %s WHERE phone_number = %s """
    cur = None
    updated_rows = 0
    try:
        cur = conn.cursor()
        cur.execute(sql_update, (new_phone_number, old_phone_number))
        updated_rows = cur.rowcount
        if updated_rows > 0:
            print(f"Successfully updated phone number '{old_phone_number}' to '{new_phone_number}'.")
        else:
             print(f"No phone number found matching '{old_phone_number}'. No update performed.")
    except psycopg2.errors.UniqueViolation:
         print(f"Error: The new phone number '{new_phone_number}' already exists.")
         conn.rollback()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error updating phone number:")
        print(error)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return updated_rows

# --- Query Functions ---

def query_all_contacts(conn):
    """ Query all contacts with their phone numbers """
    sql_query = """
        SELECT p.person_id, p.first_name, p.last_name, ph.phone_number, ph.phone_type
        FROM persons p
        LEFT JOIN phone_numbers ph ON p.person_id = ph.person_id
        ORDER BY p.first_name, p.last_name;
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql_query)
        print(f"\n--- All Contacts ({cur.rowcount} rows) ---")
        if cur.rowcount == 0:
            print("No contacts found.")
            return

        print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone Number':<20} {'Type':<10}")
        print("-" * 70)
        for row in cur.fetchall():
            p_id, f_name, l_name, phone, p_type = row
            print(f"{p_id:<5} {f_name:<15} {l_name if l_name else '':<15} {phone if phone else 'N/A':<20} {p_type if p_type else 'N/A':<10}")
        print("-" * 70)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error querying contacts:")
        print(error)
    finally:
        if cur is not None:
            cur.close()

def query_contacts_by_name(conn, first_name_filter=None, last_name_filter=None):
    """ Query contacts filtering by first name and/or last name (partial match) """
    if not first_name_filter and not last_name_filter:
        print("Please provide at least a first name or last name filter.")
        return

    sql_query = """
        SELECT p.person_id, p.first_name, p.last_name, ph.phone_number, ph.phone_type
        FROM persons p
        LEFT JOIN phone_numbers ph ON p.person_id = ph.person_id
        WHERE 1=1
    """
    params = []
    if first_name_filter:
        sql_query += " AND p.first_name ILIKE %s" # ILIKE for case-insensitive
        params.append(f"%{first_name_filter}%") # % for partial match
    if last_name_filter:
        sql_query += " AND p.last_name ILIKE %s"
        params.append(f"%{last_name_filter}%")

    sql_query += " ORDER BY p.first_name, p.last_name;"

    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql_query, tuple(params))
        print(f"\n--- Contacts Matching Name Filter ({cur.rowcount} rows) ---")
        if cur.rowcount == 0:
            print("No contacts found matching the specified name criteria.")
            return

        print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone Number':<20} {'Type':<10}")
        print("-" * 70)
        for row in cur.fetchall():
            p_id, f_name, l_name, phone, p_type = row
            print(f"{p_id:<5} {f_name:<15} {l_name if l_name else '':<15} {phone if phone else 'N/A':<20} {p_type if p_type else 'N/A':<10}")
        print("-" * 70)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error querying contacts by name:")
        print(error)
    finally:
        if cur is not None:
            cur.close()

def query_contact_by_phone(conn, phone_number_filter):
    """ Query contact details by phone number (exact match) """
    sql_query = """
        SELECT p.person_id, p.first_name, p.last_name, ph.phone_number, ph.phone_type
        FROM persons p
        JOIN phone_numbers ph ON p.person_id = ph.person_id
        WHERE ph.phone_number = %s;
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql_query, (phone_number_filter,))
        print(f"\n--- Contact Matching Phone '{phone_number_filter}' ({cur.rowcount} rows) ---")
        if cur.rowcount == 0:
            print(f"No contact found with phone number '{phone_number_filter}'.")
            return

        print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone Number':<20} {'Type':<10}")
        print("-" * 70)
        for row in cur.fetchall():
            p_id, f_name, l_name, phone, p_type = row
            print(f"{p_id:<5} {f_name:<15} {l_name if l_name else '':<15} {phone:<20} {p_type if p_type else 'N/A':<10}")
        print("-" * 70)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error querying contacts by phone:")
        print(error)
    finally:
        if cur is not None:
            cur.close()


# --- Deletion Functions ---

def delete_person_by_name(conn, first_name, last_name=None):
    """ Deletes a person (and their associated phone numbers via CASCADE) by name """
    # First, find the person(s) to confirm (optional but safer)
    find_sql = """SELECT person_id, first_name, last_name FROM persons
                  WHERE first_name = %s AND (last_name = %s OR (last_name IS NULL AND %s IS NULL));"""
    delete_sql = """DELETE FROM persons
                    WHERE first_name = %s AND (last_name = %s OR (last_name IS NULL AND %s IS NULL));"""

    cur = None
    deleted_rows = 0
    try:
        cur = conn.cursor()
        # Optional: Find and confirm - for simplicity, we delete directly here.
        # Add confirmation logic if dealing with potentially duplicate names is critical.
        cur.execute(delete_sql, (first_name, last_name, last_name))
        deleted_rows = cur.rowcount
        if deleted_rows > 0:
            print(f"Successfully deleted {deleted_rows} person record(s) (and associated phone numbers) for '{first_name} {last_name or ''}'.")
        else:
            print(f"No person found matching '{first_name} {last_name or ''}'. No deletion performed.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error deleting person by name:")
        print(error)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return deleted_rows

def delete_phone_number(conn, phone_number):
    """ Deletes a specific phone number entry """
    sql_delete = """ DELETE FROM phone_numbers WHERE phone_number = %s """
    cur = None
    deleted_rows = 0
    try:
        cur = conn.cursor()
        cur.execute(sql_delete, (phone_number,))
        deleted_rows = cur.rowcount
        if deleted_rows > 0:
            print(f"Successfully deleted phone number '{phone_number}'.")
        else:
             print(f"No phone number found matching '{phone_number}'. No deletion performed.")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error deleting phone number:")
        print(error)
        conn.rollback()
    finally:
        if cur is not None:
            cur.close()
    return deleted_rows


# --- Main Execution ---
if __name__ == '__main__':
    db_conn = connect()

    if db_conn:
        # Ensure tables exist
        create_tables(db_conn)

        # --- Example Usage ---

        # 1. Insertion from Console
        print("\n--- Inserting from Console ---")
        # insert_from_console(db_conn) # Uncomment to run interactively

        # Example direct insertion (if not using console)
        insert_contact(db_conn, 'Alice', 'Smith', '555-1234', 'Mobile')
        insert_contact(db_conn, 'Bob', 'Jones', '555-5678', 'Home')
        insert_contact(db_conn, 'Charlie', None, '555-9999', 'Work') # No last name

        # 2. Insertion from CSV
        # Create a dummy CSV file: contacts.csv
        # first_name,last_name,phone_number,phone_type
        # David,Lee,555-1111,Mobile
        # Eve,Adams,555-2222,
        # Frank,,555-3333,Work
        print("\n--- Inserting from CSV ---")
        # Create dummy csv for testing
        with open('contacts.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['first_name','last_name','phone_number','phone_type'])
            writer.writerow(['David','Lee','555-1111','Mobile'])
            writer.writerow(['Eve','Adams','555-2222', None]) # Test missing type
            writer.writerow(['Frank','','555-3333','Work']) # Test missing last name
            writer.writerow(['Grace','Hopper','555-4444','Mobile'])
        insert_from_csv(db_conn, 'contacts.csv')

        # 3. Querying Data
        print("\n--- Querying Data ---")
        query_all_contacts(db_conn)
        query_contacts_by_name(db_conn, first_name_filter='aLiCe') # Case-insensitive partial
        query_contacts_by_name(db_conn, last_name_filter='Lee')
        query_contacts_by_name(db_conn, first_name_filter='frank') # Test no last name
        query_contact_by_phone(db_conn, '555-5678')
        query_contact_by_phone(db_conn, '555-0000') # Non-existent

        # 4. Updating Data
        print("\n--- Updating Data ---")
        update_person_name(db_conn, 'Alice', 'Smith', 'Alice', 'Williams') # Update last name
        update_person_name(db_conn, 'Charlie', None, 'Charles', None) # Update first name (no last name)
        update_phone_number(db_conn, '555-9999', '555-8888') # Update Charlie/Charles' phone
        update_phone_number(db_conn, '555-1111', '555-1111-NEW') # Update David's phone
        update_phone_number(db_conn, '555-0000', '555-7777') # Try updating non-existent
        query_all_contacts(db_conn) # Show results after update

        # 5. Deleting Data
        print("\n--- Deleting Data ---")
        delete_phone_number(db_conn, '555-2222') # Delete Eve's phone number (Eve remains)
        query_all_contacts(db_conn) # Show Eve without a number now (or removed if no other numbers)

        delete_person_by_name(db_conn, 'Bob', 'Jones') # Delete Bob (and his number 555-5678)
        delete_person_by_name(db_conn, 'Frank') # Delete Frank by first name only
        delete_person_by_name(db_conn, 'NonExistent') # Try deleting someone not there

        query_all_contacts(db_conn) # Show final state

        # Close the database connection
        db_conn.close()
        print('\nDatabase connection closed.')