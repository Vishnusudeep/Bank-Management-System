import sqlite3

DATABASE_NAME = "bank_management.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # USERS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'User',
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)

    # -------------------------
    # CUSTOMERS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            status TEXT NOT NULL DEFAULT 'Active',

            FOREIGN KEY (user_id)
            REFERENCES Users(user_id)
        )
    """)

    # -------------------------
    # BANK ACCOUNTS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BankAccounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            account_number INTEGER UNIQUE NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (customer_id)
            REFERENCES Customers(customer_id)
        )
    """)

    # -------------------------
    # TRANSACTIONS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,

            FOREIGN KEY (account_id)
            REFERENCES BankAccounts(account_id)
        )
    """)

    conn.commit()
    conn.close()

    print("Database and tables created successfully.")


if __name__ == "__main__":
    create_tables()