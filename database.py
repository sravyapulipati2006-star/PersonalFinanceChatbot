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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source TEXT NOT NULL,
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


def get_user_by_name(name):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_expenses(user_id, category=None, start_date=None, end_date=None):
    """
    Fetch expenses for a user, optionally filtered by category and/or date range.
    category: exact category name (e.g. "Food") or None for all
    start_date / end_date: 'YYYY-MM-DD' strings or None
    """
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    query = 'SELECT id, category, amount, date FROM expenses WHERE user_id = ?'
    params = [user_id]

    if category:
        query += ' AND category = ?'
        params.append(category)
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    query += ' ORDER BY date DESC, id DESC'

    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def get_categories(user_id):
    """Return a sorted list of distinct categories the user has logged expenses under."""
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM expenses WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return sorted(r[0] for r in rows)


def delete_expense(expense_id, user_id):
    """Delete a single expense, scoped to the user for safety."""
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0


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


def get_all_budgets(user_id):
    """Return list of (category, limit_amount) for every budget the user has set."""
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, limit_amount FROM budgets WHERE user_id = ? ORDER BY category', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_budget_limit(user_id, category, new_limit):
    """
    Set a category's budget to new_limit. Updates the existing row if one exists,
    otherwise inserts a new one (upsert behavior).
    """
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('UPDATE budgets SET limit_amount = ? WHERE id = ?', (new_limit, existing[0]))
    else:
        cursor.execute('INSERT INTO budgets (user_id, category, limit_amount) VALUES (?, ?, ?)', (user_id, category, new_limit))

    conn.commit()
    conn.close()


def delete_budget_limit(user_id, category):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0


def get_total_spent(user_id, category):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ? AND category = ?', (user_id, category))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0


def add_income(user_id, source, amount, date):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO income (user_id, source, amount, date) VALUES (?, ?, ?, ?)', (user_id, source, amount, date))
    conn.commit()
    income_id = cursor.lastrowid
    conn.close()
    return income_id


def get_income(user_id, source=None, start_date=None, end_date=None):
    """
    Fetch income entries for a user, optionally filtered by source and/or date range.
    """
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    query = 'SELECT id, source, amount, date FROM income WHERE user_id = ?'
    params = [user_id]

    if source:
        query += ' AND source = ?'
        params.append(source)
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    query += ' ORDER BY date DESC, id DESC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_income_sources(user_id):
    """Return a sorted list of distinct income sources the user has logged."""
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT source FROM income WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return sorted(r[0] for r in rows)


def delete_income(income_id, user_id):
    """Delete a single income entry, scoped to the user for safety."""
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM income WHERE id = ? AND user_id = ?', (income_id, user_id))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0


def get_total_income(user_id, source=None):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    if source:
        cursor.execute('SELECT SUM(amount) FROM income WHERE user_id = ? AND source = ?', (user_id, source))
    else:
        cursor.execute('SELECT SUM(amount) FROM income WHERE user_id = ?', (user_id,))
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