import sqlite3
from database import get_connection, create_tables

# Common function to pause the program and wait for user input

def pause():
    input("\nPress Enter to continue...")

# Sign Up function to register a new user and customer

def signup():

    print("\n****************************")
    print("          SIGN UP")
    print("****************************")

    username = input("Enter username: ")
    password = input("Enter password: ")

    if username == "" or password == "":
        print("Username and password cannot be empty.")
        return

    Connection = get_connection()
    cursor = Connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO Users (username, password, role, status)
            VALUES (?, ?, ?, ?)
        """, (username, password, "User", "Active"))

        user_id = cursor.lastrowid

        print("\nEnter customer details")

        first_name = input("First name: ")
        last_name = input("Last name: ")
        phone = input("Phone: ")
        email = input("Email: ")
        address = input("Address: ")

        cursor.execute("""
            INSERT INTO Customers
            (user_id, first_name, last_name, phone, email, address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            first_name,
            last_name,
            phone,
            email,
            address,
            "Active"
        ))

        Connection.commit()

        print("\nSignup successful!")
        print("Please sign in using your username and password.")

    except sqlite3.IntegrityError:
        print("\nUsername already exists.")

    finally:
        Connection.close()

# Sign In function to authenticate user and direct to appropriate menu

def signin():

    print("\n****************************")
    print("          SIGN IN")
    print("****************************")

    username = input("Username: ")
    password = input("Password: ")

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT user_id, username, role, status
        FROM Users
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    Connection.close()

    if user is None:
        print("\nInvalid username or password.")
        return

    user_id = user[0]
    username = user[1]
    role = user[2]
    status = user[3]

    if status != "Active":
        print("\nYour user account is inactive.")
        return

    print("\nLogin successful!")

    if role == "Admin":
        admin_menu(user_id, username)

    else:
        user_menu(user_id, username)

# Create Bank Account function for users to create a new bank account

def create_bank_account(user_id):

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT customer_id, first_name, last_name
        FROM Customers
        WHERE user_id = ?
    """, (user_id,))

    customer = cursor.fetchone()

    if customer is None:
        print("Customer record not found.")
        Connection.close()
        return

    customer_id = customer[0]

    print("\n****************************")
    print("     CREATE BANK ACCOUNT")
    print("****************************")

    print("1. Savings")
    print("2. Current")

    choice = input("Select account type: ")

    if choice == "1":
        account_type = "Savings"

    elif choice == "2":
        account_type = "Current"

    else:
        print("Invalid account type.")
        Connection.close()
        return

    # Generate account number automatically
    cursor.execute("""
        SELECT MAX(account_number)
        FROM BankAccounts
    """)

    result = cursor.fetchone()

    if result[0] is None:
        account_number = 100001
    else:
        account_number = result[0] + 1

    cursor.execute("""
        INSERT INTO BankAccounts
        (customer_id, account_number, account_type, balance, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        account_number,
        account_type,
        0,
        "Active"
    ))

    Connection.commit()
    Connection.close()

    print("\nBank account created successfully.")
    print("Account Number:", account_number)
    print("Account Type:", account_type)

# View My Accounts

def view_my_accounts(user_id):

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT
            b.account_number,
            b.account_type,
            b.balance,
            b.status,
            b.created_at
        FROM BankAccounts b
        JOIN Customers c
            ON b.customer_id = c.customer_id
        WHERE c.user_id = ?
    """, (user_id,))

    accounts = cursor.fetchall()
    Connection.close()

    print("\n****************************")
    print("        MY ACCOUNTS")
    print("****************************")

    if not accounts:
        print("No bank accounts found.")
        return

    for account in accounts:

        print("\nAccount Number :", account[0])
        print("Account Type   :", account[1])
        print("Balance        :", account[2])
        print("Status         :", account[3])
        print("Created Date   :", account[4])
        print("------------------------------")

# Check Balance function to view the balance of a specific bank account

def check_balance(user_id):

    account_number = input("\nEnter account number: ")

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT
            b.account_number,
            b.account_type,
            b.balance,
            b.status
        FROM BankAccounts b
        JOIN Customers c
            ON b.customer_id = c.customer_id
        WHERE c.user_id = ?
        AND b.account_number = ?
    """, (user_id, account_number))

    account = cursor.fetchone()

    Connection.close()

    if account is None:
        print("Account not found.")
        return

    print("\n****************************")
    print("         ACCOUNT BALANCE")
    print("****************************")
    print("Account Number :", account[0])
    print("Account Type   :", account[1])
    print("Balance        :", account[2])
    print("Status         :", account[3])

# Deposit Money function to deposit funds into a specific bank account

def deposit_money(user_id):

    print("\n****************************")
    print("         DEPOSIT MONEY")
    print("****************************")

    account_number = input("Enter account number: ")

    try:
        amount = float(input("Enter deposit amount: "))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid amount.")
        return

    Connection = get_connection()
    cursor = Connection.cursor()

    # Check account belongs to logged-in user
    cursor.execute("""
        SELECT b.account_id, b.balance, b.status
        FROM BankAccounts b
        JOIN Customers c
            ON b.customer_id = c.customer_id
        WHERE c.user_id = ?
        AND b.account_number = ?
    """, (user_id, account_number))

    account = cursor.fetchone()

    if account is None:
        print("Account not found.")
        Connection.close()
        return

    account_id = account[0]
    current_balance = account[1]
    status = account[2]

    if status != "Active":
        print("This account is inactive.")
        Connection.close()
        return

    new_balance = current_balance + amount

    cursor.execute("""
        UPDATE BankAccounts
        SET balance = ?
        WHERE account_id = ?
    """, (new_balance, account_id))

    cursor.execute("""
        INSERT INTO Transactions
        (account_id, transaction_type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (
        account_id,
        "Deposit",
        amount,
        "Money deposited"
    ))

    Connection.commit()
    Connection.close()

    print("\nDeposit successful.")
    print("Previous Balance:", current_balance)
    print("Deposit Amount  :", amount)
    print("New Balance     :", new_balance)

# Withdraw Money function to withdraw funds from a specific bank account

def withdraw_money(user_id):

    print("\n****************************")
    print("        WITHDRAW MONEY")
    print("****************************")

    account_number = input("Enter account number: ")

    try:
        amount = float(input("Enter withdrawal amount: "))

        if amount <= 0:
            print("Amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid amount.")
        return

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT b.account_id, b.balance, b.status
        FROM BankAccounts b
        JOIN Customers c
            ON b.customer_id = c.customer_id
        WHERE c.user_id = ?
        AND b.account_number = ?
    """, (user_id, account_number))

    account = cursor.fetchone()

    if account is None:
        print("Account not found.")
        Connection.close()
        return

    account_id = account[0]
    current_balance = account[1]
    status = account[2]

    if status != "Active":
        print("This account is inactive.")
        Connection.close()
        return

    if amount > current_balance:
        print("\nInsufficient balance.")
        print("Available Balance:", current_balance)
        Connection.close()
        return

    new_balance = current_balance - amount

    cursor.execute("""
        UPDATE BankAccounts
        SET balance = ?
        WHERE account_id = ?
    """, (new_balance, account_id))

    cursor.execute("""
        INSERT INTO Transactions
        (account_id, transaction_type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (
        account_id,
        "Withdrawal",
        amount,
        "Money withdrawn"
    ))

    Connection.commit()
    Connection.close()

    print("\nWithdrawal successful.")
    print("Previous Balance:", current_balance)
    print("Withdrawal Amount:", amount)
    print("New Balance     :", new_balance)

# View My Transactions function to display all transactions for the logged-in user

def view_my_transactions(user_id):

    Connection = get_connection()
    cursor = Connection.cursor()
    cursor.execute("""
        SELECT
            b.account_number,
            t.transaction_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description
        FROM Transactions t
        JOIN BankAccounts b
            ON t.account_id = b.account_id
        JOIN Customers c
            ON b.customer_id = c.customer_id
        WHERE c.user_id = ?
        ORDER BY t.transaction_date DESC
    """, (user_id,))

    transactions = cursor.fetchall()

    Connection.close()

    print("\n****************************")
    print("       MY TRANSACTIONS")
    print("****************************")

    if not transactions:
        print("No transactions found.")
        return

    for transaction in transactions:
        print("\nAccount Number :", transaction[0])
        print("Transaction ID :", transaction[1])
        print("Type           :", transaction[2])
        print("Amount         :", transaction[3])
        print("Date           :", transaction[4])
        print("Description    :", transaction[5])
        print("------------------------------")

# Update Customer Details admin only

def update_customer():

    print("\n****************************")
    print("     UPDATE CUSTOMER")
    print("****************************")

    try:
        customer_id = int(input("Enter customer ID: "))

    except ValueError:
        print("Invalid customer ID.")
        return

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT customer_id, first_name, last_name,
               phone, email, address
        FROM Customers
        WHERE customer_id = ?
    """, (customer_id,))

    customer = cursor.fetchone()

    if customer is None:
        print("Customer not found.")
        Connection.close()
        return

    print("\nLeave field empty to keep existing value.")

    first_name = input(
        f"First name ({customer[1]}): "
    ).strip()

    last_name = input(
        f"Last name ({customer[2]}): "
    ).strip()

    phone = input(
        f"Phone ({customer[3]}): "
    ).strip()

    email = input(
        f"Email ({customer[4]}): "
    ).strip()

    address = input(
        f"Address ({customer[5]}): "
    ).strip()

    if first_name == "":
        first_name = customer[1]

    if last_name == "":
        last_name = customer[2]

    if phone == "":
        phone = customer[3]

    if email == "":
        email = customer[4]

    if address == "":
        address = customer[5]

    cursor.execute("""
        UPDATE Customers
        SET first_name = ?,
            last_name = ?,
            phone = ?,
            email = ?,
            address = ?
        WHERE customer_id = ?
    """, (
        first_name,
        last_name,
        phone,
        email,
        address,
        customer_id
    ))

    Connection.commit()
    Connection.close()

    print("\nCustomer details updated successfully.")

# View All Customers function to display all customers in the system admin only

def view_all_customers():

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT
            c.customer_id,
            u.username,
            c.first_name,
            c.last_name,
            c.phone,
            c.email,
            c.address,
            c.status
        FROM Customers c
        JOIN Users u
            ON c.user_id = u.user_id
        ORDER BY c.customer_id
    """)

    customers = cursor.fetchall()

    Connection.close()

    print("\n****************************")
    print("        ALL CUSTOMERS")
    print("****************************")

    if not customers:
        print("No customers found.")
        return

    for customer in customers:
        print("\nCustomer ID :", customer[0])
        print("Username    :", customer[1])
        print("First Name  :", customer[2])
        print("Last Name   :", customer[3])
        print("Phone       :", customer[4])
        print("Email       :", customer[5])
        print("Address     :", customer[6])
        print("Status      :", customer[7])
        print("------------------------------")

# View all accounts function to display all bank accounts in the system admin only

def view_all_accounts():

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT
            b.account_id,
            b.account_number,
            c.customer_id,
            c.first_name,
            c.last_name,
            b.account_type,
            b.balance,
            b.status
        FROM BankAccounts b
        JOIN Customers c
            ON b.customer_id = c.customer_id
        ORDER BY b.account_id
    """)

    accounts = cursor.fetchall()

    Connection.close()

    print("\n****************************")
    print("       ALL BANK ACCOUNTS")
    print("****************************")

    if not accounts:
        print("No accounts found.")
        return

    for account in accounts:

        print("\nAccount ID     :", account[0])
        print("Account Number :", account[1])
        print("Customer ID    :", account[2])
        print("Customer Name  :", account[3], account[4])
        print("Account Type   :", account[5])
        print("Balance        :", account[6])
        print("Status         :", account[7])
        print("------------------------------")

# View all transactions function to display all transactions in the system admin only

def view_all_transactions():

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT
            t.transaction_id,
            b.account_number,
            c.first_name,
            c.last_name,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description
        FROM Transactions t
        JOIN BankAccounts b
            ON t.account_id = b.account_id
        JOIN Customers c
            ON b.customer_id = c.customer_id
        ORDER BY t.transaction_date DESC
    """)

    transactions = cursor.fetchall()

    Connection.close()

    print("\n****************************")
    print("       ALL TRANSACTIONS")
    print("****************************")

    if not transactions:
        print("No transactions found.")
        return

    for transaction in transactions:

        print("\nTransaction ID :", transaction[0])
        print("Account Number :", transaction[1])
        print("Customer Name  :", transaction[2], transaction[3])
        print("Type           :", transaction[4])
        print("Amount         :", transaction[5])
        print("Date           :", transaction[6])
        print("Description    :", transaction[7])
        print("------------------------------")

# Activate/Deactivate User function to change the status of a user account

def change_user_status():

    print("\n****************************")
    print("    ACTIVATE / DEACTIVATE USER")
    print("****************************")

    username = input("Enter username: ").strip()

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT user_id, username, role, status
        FROM Users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if user is None:
        print("User not found.")
        Connection.close()
        return

    print("\nUsername :", user[1])
    print("Role     :", user[2])
    print("Status   :", user[3])

    if user[2] == "Admin":
        print("Admin user cannot be deactivated.")
        Connection.close()
        return

    print("\n1. Activate")
    print("2. Deactivate")

    choice = input("Select option: ")

    if choice == "1":
        new_status = "Active"

    elif choice == "2":
        new_status = "Inactive"

    else:
        print("Invalid option.")
        Connection.close()
        return

    cursor.execute("""
        UPDATE Users
        SET status = ?
        WHERE user_id = ?
    """, (new_status, user[0]))

    # Also update customer status
    cursor.execute("""
        UPDATE Customers
        SET status = ?
        WHERE user_id = ?
    """, (new_status, user[0]))

    Connection.commit()
    Connection.close()

    print("\nUser status updated to:", new_status)

# Activate/Deactivate Account function to change the status of a bank account

def change_account_status():

    print("\n****************************")
    print(" ACTIVATE / DEACTIVATE ACCOUNT")
    print("****************************")

    account_number = input("Enter account number: ").strip()

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT account_id, account_number,
               account_type, balance, status
        FROM BankAccounts
        WHERE account_number = ?
    """, (account_number,))

    account = cursor.fetchone()

    if account is None:
        print("Account not found.")
        Connection.close()
        return

    print("\nAccount Number :", account[1])
    print("Account Type   :", account[2])
    print("Balance        :", account[3])
    print("Current Status :", account[4])

    print("\n1. Activate")
    print("2. Deactivate")

    choice = input("Select option: ")

    if choice == "1":
        new_status = "Active"

    elif choice == "2":
        new_status = "Inactive"

    else:
        print("Invalid option.")
        Connection.close()
        return

    cursor.execute("""
        UPDATE BankAccounts
        SET status = ?
        WHERE account_id = ?
    """, (new_status, account[0]))

    Connection.commit()
    Connection.close()

    print("\nAccount status updated to:", new_status)


# Admin Menu function to display the admin menu and handle admin operations

def admin_menu(user_id, username):

    while True:

        print("\n****************************")
        print("          ADMIN MENU")
        print("****************************")
        print("Logged in as:", username)
        print()
        print("1. View All Customers")
        print("2. View All Bank Accounts")
        print("3. View All Transactions")
        print("4. Update Customer Details")
        print("5. Activate / Deactivate User")
        print("6. Activate / Deactivate Account")
        print("7. Logout")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            view_all_customers()
            pause()

        elif choice == "2":

            view_all_accounts()
            pause()

        elif choice == "3":

            view_all_transactions()
            pause()

        elif choice == "4":

            update_customer()
            pause()

        elif choice == "5":

            change_user_status()
            pause()

        elif choice == "6":

            change_account_status()
            pause()

        elif choice == "7":

            print("\nLogged out successfully.")
            break

        else:

            print("\nInvalid choice.")

# User Menu function to display the user menu and handle user operations

def user_menu(user_id, username):

    while True:

        print("\n****************************")
        print("           USER MENU")
        print("****************************")
        print("Logged in as:", username)
        print()
        print("1. Create Bank Account")
        print("2. View My Accounts")
        print("3. Check Balance")
        print("4. Deposit Money")
        print("5. Withdraw Money")
        print("6. View My Transactions")
        print("7. Logout")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            create_bank_account(user_id)
            pause()

        elif choice == "2":

            view_my_accounts(user_id)
            pause()

        elif choice == "3":

            check_balance(user_id)
            pause()

        elif choice == "4":

            deposit_money(user_id)
            pause()

        elif choice == "5":

            withdraw_money(user_id)
            pause()

        elif choice == "6":

            view_my_transactions(user_id)
            pause()

        elif choice == "7":

            print("\nLogged out successfully.")
            break

        else:

            print("\nInvalid choice.")


# Create Default Admin User function to create an initial admin user if it doesn't exist

def create_default_admin():

    Connection = get_connection()
    cursor = Connection.cursor()

    cursor.execute("""
        SELECT user_id
        FROM Users
        WHERE username = ?
    """, ("admin",))

    admin = cursor.fetchone()

    if admin is None:

        cursor.execute("""
            INSERT INTO Users
            (username, password, role, status)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            "admin123",
            "Admin",
            "Active"
        ))

        Connection.commit()

        print("\nDefault admin created.")
        print("Username: admin")
        print("Password: admin123")

    Connection.close()

# Main Menu function to display the main menu and handle user operations

def main():

    # Create database tables
    create_tables()

    # Create default admin
    create_default_admin()

    while True:

        print("\n****************************")
        print("      BANK MANAGEMENT SYSTEM")
        print("****************************")

        print("\n1. Sign Up")
        print("2. Sign In")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            signup()
            pause()

        elif choice == "2":

            signin()
            pause()

        elif choice == "3":

            print("\nThank you for using Bank Management System.")
            break

        else:

            print("\nInvalid choice.")

#Start Program

if __name__ == "__main__":
    main()