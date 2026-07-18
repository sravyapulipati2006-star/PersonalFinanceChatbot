import sqlite3

def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database created successfully!")
def add_user(name):
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
def get_expenses(user_id):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, amount, date FROM expenses WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()
    conn.close()
    return expenses
def add_budget_limit(user_id, category, limit_amount):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO budgets (user_id, category, limit_amount) VALUES (?, ?, ?)', (user_id, category, limit_amount))
    conn.commit()
    budget_id = cursor.lastrowid
    conn.close()
    return budget_id

def get_budget_limit(user_id, category):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT limit_amount FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_total_spent(user_id, category):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ? AND category = ?', (user_id, category))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

def add_expense(user_id, category, amount, date):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)', (user_id, category, amount, date))
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return expense_id

if __name__ == '__main__':
    init_db()
    user_id = add_user("Sravya")
    print("Created user with ID:", user_id)
    expense_id = add_expense(user_id, "Food", 250.0, "2026-07-18")
    print("Created expense with ID:", expense_id)
    expenses = get_expenses(user_id)
    print("Expenses for user:", expenses)
    budget_id = add_budget_limit(user_id, "Food", 500.0)
    print("Created budget limit with ID:", budget_id)