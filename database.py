import sqlite3


DATABASE_NAME = "finance.db"


# ---------------- CONNECTION ----------------

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ---------------- CREATE TABLES ----------------

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        limit_amount REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully!")
    # ---------------- USERS ----------------

def add_user(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(name) VALUES(?)",
        (name,)
    )

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return user_id


def get_user_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE name=?",
        (name,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None
# ---------------- EXPENSES ----------------

def add_expense(user_id, category, amount, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses
    (user_id, category, amount, date)
    VALUES (?, ?, ?, ?)
    """,
    (user_id, category, amount, date))

    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()

    return expense_id


def get_expenses(user_id, category=None, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, category, amount, date FROM expenses WHERE user_id=?"
    params = [user_id]

    if category:
        query += " AND category=?"
        params.append(category)
    if start_date:
        query += " AND date>=?"
        params.append(start_date)
    if end_date:
        query += " AND date<=?"
        params.append(end_date)

    query += " ORDER BY date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows


def get_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT category
    FROM expenses
    WHERE user_id=?
    ORDER BY category
    """,
    (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [r[0] for r in rows]


def delete_expense(expense_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM expenses
    WHERE id=? AND user_id=?
    """,
    (expense_id, user_id))

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return deleted > 0


def get_total_spent(user_id, category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id=? AND category=?
    """,
    (user_id, category))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] else 0
# ---------------- INCOME ----------------

def add_income(user_id, source, amount, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO income
    (user_id, source, amount, date)
    VALUES (?, ?, ?, ?)
    """,
    (user_id, source, amount, date))

    conn.commit()
    income_id = cursor.lastrowid
    conn.close()

    return income_id


def get_income(user_id, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, source, amount, date FROM income WHERE user_id=?"
    params = [user_id]

    if start_date:
        query += " AND date>=?"
        params.append(start_date)
    if end_date:
        query += " AND date<=?"
        params.append(end_date)

    query += " ORDER BY date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_income(income_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM income
    WHERE id=? AND user_id=?
    """,
    (income_id, user_id))

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return deleted > 0


def get_total_income(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(amount)
    FROM income
    WHERE user_id=?
    """,
    (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result[0] else 0
# ---------------- BUDGETS ----------------

def get_budget_limit(user_id, category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT limit_amount
    FROM budgets
    WHERE user_id=? AND category=?
    """,
    (user_id, category))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0


def add_budget_limit(user_id, category, limit_amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO budgets
    (user_id, category, limit_amount)
    VALUES (?, ?, ?)
    """,
    (user_id, category, limit_amount))

    conn.commit()
    budget_id = cursor.lastrowid
    conn.close()

    return budget_id


def get_all_budgets(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, limit_amount
    FROM budgets
    WHERE user_id=?
    ORDER BY category
    """,
    (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def update_budget_limit(user_id, category, new_limit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE budgets
    SET limit_amount=?
    WHERE user_id=? AND category=?
    """,
    (new_limit, user_id, category))

    if cursor.rowcount == 0:
        cursor.execute("""
        INSERT INTO budgets
        (user_id, category, limit_amount)
        VALUES(?, ?, ?)
        """,
        (user_id, category, new_limit))

    conn.commit()
    conn.close()


def delete_budget_limit(user_id, category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM budgets
    WHERE user_id=? AND category=?
    """,
    (user_id, category))

    conn.commit()
    conn.close()
    # ---------------- TEST RUN ----------------

if __name__ == "__main__":
    init_db()
    print("Database ready!")