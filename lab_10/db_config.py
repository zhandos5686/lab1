# db_config.py
# IMPORTANT: Avoid hardcoding credentials directly in scripts for production.
# Consider environment variables or a more secure configuration management system.
def get_db_params():
    """ Returns database connection parameters """
    return {
        'database': 'phonebook_db', # Replace with your database name
        'user': 'your_username',    # Replace with your PostgreSQL username
        'password': 'your_password', # Replace with your PostgreSQL password
        'host': 'localhost',       # Replace with your host if not local
        'port': '5432'             # Default PostgreSQL port
    }