import re
from database import init_db, add_user, add_expense, get_expenses, add_budget_limit, get_budget_limit, get_total_spent
from datetime import date

def parse_expense(text):
    # Matches patterns like "I spent 250 on food"
    match = re.search(r'spent\s+(\d+(?:\.\d+)?)\s+on\s+(\w+)', text, re.IGNORECASE)
    if match:
        amount = float(match.group(1))
        category = match.group(2).capitalize()
        return amount, category
    return None, None
import os

def get_or_create_user(name):
    if os.path.exists('user_id.txt'):
        with open('user_id.txt', 'r') as f:
            return int(f.read().strip())
    else:
        user_id = add_user(name)
        with open('user_id.txt', 'w') as f:
            f.write(str(user_id))
        return user_id

def chat():
    print("Welcome to your Personal Finance Chatbot!")
    name = input("What's your name? ")
    user_id = get_or_create_user(name)
    print(f"(Using user ID: {user_id})")
    print(f"Hi {name}, I'm ready to track your expenses. Type 'quit' to exit.")

    while True:
        text = input("> ")
        if text.lower() == 'quit':
            break
        if text.lower() == 'summary':
            expenses = get_expenses(user_id)
            if expenses:
                print("Here's your spending so far:")
                for exp in expenses:
                    print(f"  - {exp[1]}: {exp[2]} on {exp[3]}")
            else:
                print("No expenses logged yet.")
            continue
        if text.lower() == 'quit':
            break

        if text.lower() == 'summary':
            ...
            continue

        set_match = re.search(r'set budget\s+(\d+(?:\.\d+)?)\s+for\s+(\w+)', text, re.IGNORECASE)
        if set_match:
            limit_amount = float(set_match.group(1))
            category = set_match.group(2).capitalize()
            add_budget_limit(user_id, category, limit_amount)
            print(f"Got it — set your {category} budget to {limit_amount}.")
            continue

        
        amount, category = parse_expense(text)
        if amount:
            today = str(date.today())
            add_expense(user_id, category, amount, today)
            print(f"Got it — logged {amount} under {category}.")
            limit = get_budget_limit(user_id, category)
            if limit:
                total = get_total_spent(user_id, category)
                if total > limit:
                    print(f"⚠️ You've gone over your {category} budget! ({total}/{limit})")
                elif total > limit * 0.8:
                    print(f"⚠️ Heads up — you're close to your {category} budget ({total}/{limit}).")
        else:
            print("Sorry, I didn't understand that. Try: 'I spent 200 on food'")

if __name__ == '__main__':
    init_db()
    chat()