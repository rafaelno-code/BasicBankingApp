# Basic Banking App

## Overview

This is a simple command-line banking application written in Python, backed by a MySQL database. Users can create accounts, log in with an account number and PIN, check balances, deposit, withdraw, view transaction history, and (if an administrator) manage accounts.

## Features

- **User Authentication**: Secure login via account number and PIN (hashed with SHA-256).
- **Account Operations**:
  - Create new account with initial deposit.
  - Check current balance.
  - Deposit and withdraw funds (updates persisted in MySQL).
  - View full transaction history, with timestamps.
  - Modify account details (name or PIN).
- **Admin Functions**:
  - Create, close, and modify any account.
  - Default administrator account auto-created on first run (`00000000` / PIN `0000`).
- **Data Persistence**: All data stored in MySQL tables (`accounts` and `transactions`).
- **Automated Tests**: Python `unittest` suite to verify hashing, authentication, and transaction logic.

## Prerequisites

- Python 3.7 or higher
- MySQL server instance
- Pip package: `mysql-connector-python`

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/basic-banking-app.git
   cd basic-banking-app
   ```

2. **Install dependencies**
   ```bash
   pip install mysql-connector-python
   ```

3. **Configure database credentials**
   - Open `banking_app.py` and update `DB_CONFIG` with your MySQL `host`, `user`, `password`, and `database` name.

4. **Initialize the database**
   On first run, the application will create the database and required tables:
   ```bash
   python banking_app.py
   ```
   - A default admin account (`00000000`, PIN `0000`) will be created automatically.

## Usage

Launch the app:
```bash
python banking_app.py
```

You will see a menu:
```
1. Login
2. Exit
```

- **Login**: Enter your account number and PIN.
- **Customer Menu**:
  1. Check Balance
  2. Deposit
  3. Withdraw
  4. View Transaction History
  5. Modify Account
  6. Logout
- **Admin Menu** (if logged in as admin):
  1. Create Account
  2. Close Account
  3. Modify Account
  4. Logout

Follow prompts to perform operations. All changes are saved to MySQL.

## Running Tests

The test suite uses `unittest` to validate core functionality:

```bash
python -m unittest testing_banking_app.py
```

Tests cover:
- PIN hashing consistency and format.
- Default admin creation.
- Authentication success and failure cases.
- Recording and retrieval of transactions.

## Database Schema

- **accounts** table:
  - `account_id` (INT, PK)
  - `account_no` (VARCHAR)
  - `customer_name` (VARCHAR)
  - `pin_hash` (VARCHAR)
  - `balance` (DECIMAL)
  - `is_active`, `is_admin` (TINYINT)
  - `created_at` (DATETIME)

- **transactions** table:
  - `tx_id` (INT, PK)
  - `account_id` (FK)
  - `tx_type` (VARCHAR)
  - `amount` (DECIMAL)
  - `tx_date` (DATETIME)

## License

This project is licensed under the MIT License. Feel free to adapt and extend for your own learning and use.
