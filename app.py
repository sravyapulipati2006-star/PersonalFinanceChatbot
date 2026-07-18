import streamlit as st
from database import init_db, add_user, add_expense, get_expenses, add_budget_limit, get_budget_limit, get_total_spent
from datetime import date
import re
import os

init_db()

def get_or_create_user(name):
    if os.path.exists('user_id.txt'):
        with open('user_id.txt', 'r') as f:
            return int(f.read().strip())
    else:
        user_id = add_user(name)
        with open('user_id.txt', 'w') as f:
            f.write(str(user_id))
        return user_id

def parse_expense(text):
    patterns = [
        r'spent\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:on|for)\s+(\w+)',
        r'paid\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:on|for)\s+(\w+)',
        r'(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:on|for)\s+(\w+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1)), match.group(2).capitalize()
    return None, None

st.title("💰 Personal Finance Chatbot")

with st.sidebar:
    st.header("Options")
    if st.button("Reset (start fresh)"):
        if os.path.exists('user_id.txt'):
            os.remove('user_id.txt')
        if os.path.exists('finance.db'):
            os.remove('finance.db')
        st.session_state.clear()
        st.rerun()

if "user_id" not in st.session_state:
    name = st.text_input("What's your name?")
    if name:
        st.session_state.user_id = get_or_create_user(name)
        st.session_state.name = name
        st.rerun()
else:
    st.write(f"Hi {st.session_state.name}! Type a message below.")
    text = st.text_input("Try: 'I spent 200 on food' or 'set budget 500 for food' or 'summary'")

    if text:
        user_id = st.session_state.user_id
        set_match = re.search(r'set budget\s+(\d+(?:\.\d+)?)\s+for\s+(\w+)', text, re.IGNORECASE)

        if text.lower() == 'summary':
            expenses = get_expenses(user_id)
            if expenses:
                st.write("### Your spending so far:")
                st.table([{"Category": e[1], "Amount": e[2], "Date": e[3]} for e in expenses])
            else:
                st.write("No expenses logged yet.")
        elif set_match:
            limit_amount = float(set_match.group(1))
            category = set_match.group(2).capitalize()
            add_budget_limit(user_id, category, limit_amount)
            st.success(f"Set your {category} budget to {limit_amount}.")
        else:
            amount, category = parse_expense(text)
            if amount:
                today = str(date.today())
                add_expense(user_id, category, amount, today)
                st.success(f"Logged {amount} under {category}.")

                limit = get_budget_limit(user_id, category)
                if limit:
                    total = get_total_spent(user_id, category)
                    progress = min(total / limit, 1.0)
                    st.write(f"**{category} budget:** {total}/{limit}")
                    st.progress(progress)
                    if total > limit:
                        st.warning(f"⚠️ You've gone over your {category} budget!")
                    elif total > limit * 0.8:
                        st.warning(f"⚠️ Close to your {category} budget.")
            else:
                st.error("Sorry, I didn't understand that. Try: 'I spent 200 on food'")