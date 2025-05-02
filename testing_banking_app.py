# test_banking_app.py
import unittest
import mysql.connector
import hashlib
from banking_app import DB_CONFIG, hash_pin, init_db, authenticate, record_transaction

class TestBankingAppMySQL(unittest.TestCase):
    def setUp(self):
        # Use a test database
        self.orig_db = DB_CONFIG['database']
        DB_CONFIG['database'] = 'test_banking'
        init_db()

    def tearDown(self):
        # Drop test database
        conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{DB_CONFIG['database']}`;")
        conn.commit()
        conn.close()
        DB_CONFIG['database'] = self.orig_db

    def test_hash_pin(self):
        pin = '1234'
        self.assertEqual(hash_pin(pin), hashlib.sha256(pin.encode()).hexdigest())

    def test_default_admin_created(self):
        user = authenticate('00000000', '0000')
        self.assertIsNotNone(user)
        self.assertTrue(user['is_admin'])

    def test_authenticate_failure(self):
        self.assertIsNone(authenticate('doesnotexist', '9999'))

    def test_record_transaction(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        pin_h = hash_pin('0000')
        cursor.execute("INSERT INTO `accounts` (account_no, customer_name, pin_hash, balance) VALUES(%s,%s,%s,%s);",
                       ('22222222', 'Tester', pin_h, 100.00))
        conn.commit()
        cursor.execute("SELECT account_id FROM `accounts` WHERE account_no=%s;", ('22222222',))
        account_id = cursor.fetchone()[0]
        conn.close()
        record_transaction(account_id, 'deposit', 25.50)
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT tx_type, amount FROM `transactions` WHERE account_id=%s;", (account_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertEqual(row, ('deposit', 25.50))

if __name__ == '__main__':
    unittest.main()
