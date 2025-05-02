# banking_app.py
import mysql.connector
import sys
from mysql.connector import errorcode

# MySQL connection configuration
DB_CONFIG = {
    'host': '127.0.0.1',  # force TCP
    'port': 3306,
    'user': 'root',
    'password': 'zbdsJFBjMhUx4o4shHMR',
    'database': 'banking'
}

ADMIN_DEFAULT_ACCOUNT = '00000000'
ADMIN_DEFAULT_PIN = '0000'

# Embedded SQL schema for table creation
SCHEMA = '''
CREATE TABLE IF NOT EXISTS `accounts` (
    `account_id` INT PRIMARY KEY AUTO_INCREMENT,
    `account_no` VARCHAR(20) UNIQUE NOT NULL,
    `customer_name` VARCHAR(100) NOT NULL,
    `pin_hash` VARCHAR(64) NOT NULL,
    `balance` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `is_admin` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS `transactions` (
    `tx_id` INT PRIMARY KEY AUTO_INCREMENT,
    `account_id` INT NOT NULL,
    `tx_type` VARCHAR(10) NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `tx_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`account_id`) REFERENCES `accounts`(`account_id`) ON DELETE CASCADE
) ENGINE=InnoDB;
'''

def get_db_connection(use_database=True):
    cfg = DB_CONFIG.copy()
    if not use_database:
        cfg.pop('database', None)
    return mysql.connector.connect(**cfg)


def init_db():
    # Initialize database and tables
    try:
        conn = get_db_connection(use_database=False)
    except mysql.connector.errors.ProgrammingError as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Check DB credentials.")
            sys.exit(1)
        else:
            raise
    # Create database
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`;")
    conn.commit()
    conn.close()
    # Apply schema
    conn = get_db_connection()
    cursor = conn.cursor()
    for stmt in filter(None, (s.strip() for s in SCHEMA.split(';'))):
        cursor.execute(stmt)
    conn.commit()
    # Ensure admin
    cursor.execute("SELECT COUNT(*) FROM `accounts` WHERE `is_admin`=1;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO `accounts` (account_no, customer_name, pin_hash, balance, is_active, is_admin) VALUES (%s, %s, %s, 0, 1, 1)",
            (ADMIN_DEFAULT_ACCOUNT, 'Administrator', hash_pin(ADMIN_DEFAULT_PIN))
        )
        conn.commit()
        print(f"Default admin created: account_no={ADMIN_DEFAULT_ACCOUNT}, PIN={ADMIN_DEFAULT_PIN}")
    conn.close()


def hash_pin(pin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SHA2(%s, 256);", (pin,))
    hashed = cursor.fetchone()[0]
    conn.close()
    return hashed


def authenticate(account_no, pin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT account_id, customer_name, balance, is_active, is_admin, pin_hash FROM `accounts` WHERE account_no=%s;",
        (account_no,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row or not row[3]:
        return None
    if hash_pin(pin) != row[5]:
        return None
    return {'account_id': row[0], 'customer_name': row[1], 'balance': float(row[2]), 'is_admin': bool(row[4])}


def create_account():
    name = input('Enter customer name: ')
    while True:
        pin = input('Set a 4-digit PIN: ')
        if pin.isdigit() and len(pin) == 4:
            break
        print('Invalid PIN. Try again.')
    account_no = input('Choose an account number: ')
    initial = float(input('Initial deposit amount: '))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO `accounts` (account_no, customer_name, pin_hash, balance) VALUES (%s, %s, %s, %s);",
            (account_no, name, hash_pin(pin), initial)
        )
        conn.commit()
        print('Account created successfully.')
    except mysql.connector.IntegrityError:
        print('Account number already exists.')
    conn.close()


def close_account():
    acct = input('Enter account number to close: ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE `accounts` SET is_active=0 WHERE account_no=%s;", (acct,))
    conn.commit()
    print('Account closed.' if cursor.rowcount else 'No such active account.')
    conn.close()


def modify_account():
    acct = input('Enter account number to modify: ')
    pin = input('Enter current PIN: ')
    user = authenticate(acct, pin)
    if not user:
        print('Authentication failed.')
        return
    print('1. Change name')
    print('2. Change PIN')
    choice = input('Select option: ')
    conn = get_db_connection()
    cursor = conn.cursor()
    if choice == '1':
        new_name = input('Enter new name: ')
        cursor.execute("UPDATE `accounts` SET customer_name=%s WHERE account_no=%s;", (new_name, acct))
    elif choice == '2':
        while True:
            new_pin = input('Enter new 4-digit PIN: ')
            if new_pin.isdigit() and len(new_pin) == 4:
                break
            print('Invalid PIN.')
        cursor.execute("UPDATE `accounts` SET pin_hash=%s WHERE account_no=%s;", (hash_pin(new_pin), acct))
    else:
        print('Invalid option.')
        conn.close()
        return
    conn.commit()
    conn.close()
    print('Account updated.')


def record_transaction(account_id, tx_type, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO `transactions` (account_id, tx_type, amount) VALUES (%s, %s, %s);",
        (account_id, tx_type, amount)
    )
    conn.commit()
    conn.close()


def check_balance(user):
    print(f"Current balance: ${user['balance']:.2f}")


def deposit(user):
    amt = float(input('Enter deposit amount: '))
    new_bal = user['balance'] + amt
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE `accounts` SET balance=%s WHERE account_id=%s;", (new_bal, user['account_id']))
    conn.commit()
    conn.close()
    record_transaction(user['account_id'], 'deposit', amt)
    user['balance'] = new_bal
    print(f"Deposited ${amt:.2f} successfully. New balance: ${new_bal:.2f}")


def withdraw(user):
    amt = float(input('Enter withdrawal amount: '))
    if amt > user['balance']:
        print('Insufficient funds.')
        return
    new_bal = user['balance'] - amt
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE `accounts` SET balance=%s WHERE account_id=%s;", (new_bal, user['account_id']))
    conn.commit()
    conn.close()
    record_transaction(user['account_id'], 'withdraw', amt)
    user['balance'] = new_bal
    print(f"Withdrew ${amt:.2f} successfully. New balance: ${new_bal:.2f}")


def get_transaction_history(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tx_id, tx_type, amount, tx_date FROM `transactions` WHERE account_id=%s ORDER BY tx_date;",
        (account_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def view_transaction_history(user):
    history = get_transaction_history(user['account_id'])
    if not history:
        print('No transactions found.')
        return
    print("\n--- Transaction History ---")
    print(f"{'ID':<5} {'Type':<10} {'Amount':<10} {'Date'}")
    for tx_id, tx_type, amount, tx_date in history:
        print(f"{tx_id:<5} {tx_type:<10} ${amount:<10.2f} {tx_date}")


def user_menu(user):
    while True:
        print("\n--- Customer Menu ---")
        print('1. Check Balance')
        print('2. Deposit')
        print('3. Withdraw')
        print('4. View Transaction History')
        print('5. Modify Account')
        print('6. Logout')
        choice = input('Choose an option: ')
        if choice == '1':
            check_balance(user)
        elif choice == '2':
            deposit(user)
        elif choice == '3':
            withdraw(user)
        elif choice == '4':
            view_transaction_history(user)
        elif choice == '5':
            modify_account()
        elif choice == '6':
            break
        else:
            print('Invalid option.')


def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print('1. Create Account')
        print('2. Close Account')
        print('3. Modify Account')
        print('4. Logout')
        choice = input('Choose an option: ')
        if choice == '1':
            create_account()
        elif choice == '2':
            close_account()
        elif choice == '3':
            modify_account()
        elif choice == '4':
            break
        else:
            print('Invalid option.')


def main():
    init_db()
    print('Welcome to the Online Banking System')
    while True:
        print("\n1. Login")
        print('2. Exit')
        choice = input('Choose an option: ')
        if choice == '1':
            acct = input('Account No: ')
            pin = input('PIN: ')
            user = authenticate(acct, pin)
            if not user:
                print('Login failed.')
                continue
            if user['is_admin']:
                admin_menu()
            else:
                user_menu(user)
        elif choice == '2':
            print('Goodbye!')
            sys.exit()
        else:
            print('Invalid option.')


if __name__ == '__main__':
    main()
