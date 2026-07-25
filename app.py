import streamlit as st
from database import (
    init_db, add_user, add_expense, get_expenses, add_budget_limit,
    get_budget_limit, get_total_spent, get_user_by_name,
    get_categories, delete_expense, get_all_budgets, update_budget_limit,
    add_income, get_income, get_total_income, delete_income
)
from datetime import date
import re
import os
import io
import csv

init_db()

def get_or_create_user(name):
    existing_id = get_user_by_name(name)
    if existing_id:
        return existing_id
    else:
        return add_user(name)

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

def parse_income(text):
    patterns = [
        r'received\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:from|for)\s+(\w+)',
        r'got\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:from|for)\s+(\w+)',
        r'earned\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:from|for)\s+(\w+)',
        r'income\s+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s+(?:rupees\s+)?(?:from|for)\s+(\w+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1)), match.group(2).capitalize()
    return None, None

CATEGORY_ICONS = {
    "Food": "🥘", "Groceries": "🛒", "Rent": "🏠", "Fee": "🧾",
    "Files": "📁", "Bill": "💡", "Transport": "🚗", "Travel": "✈️",
    "Shopping": "🛍️", "Health": "🏥", "Entertainment": "🎬",
    "Education": "📚", "Curdpuri": "🧇", "Panipuri": "🫓", "Fastfood": "🍕",
 }
INCOME_ICONS = {
    "Salary": "💼", "Bonus": "🎁", "Gift": "🎉",
    "Interest": "🏦", "Refund": "↩️",
}

def category_label(category):
    icon = CATEGORY_ICONS.get(category, "💸")
    return f"{icon} {category}"

def income_label(source):
    icon = INCOME_ICONS.get(source, "💰")
    return f"{icon} {source}"

def expenses_to_csv(expenses):
    """expenses: list of (id, category, amount, date) -> csv text.
    Date is wrapped as ="YYYY-MM-DD" so Excel always shows it as plain text
    instead of auto-converting/misreading it as a date and leaving it blank."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Category", "Amount", "Date"])
    for e in expenses:
        writer.writerow([e[1], e[2], f'="{e[3]}"'])
    return buf.getvalue()

def income_to_csv(income_entries):
    """income_entries: list of (id, source, amount, date) -> csv text.
    Date is wrapped as ="YYYY-MM-DD" so Excel always shows it as plain text."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Source", "Amount", "Date"])
    for i in income_entries:
        writer.writerow([i[1], i[2], f'="{i[3]}"'])
    return buf.getvalue()

st.set_page_config(page_title="Personal Finance Chatbot", page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4b0.png", layout="centered")

st.markdown("""
<style>
/* Ensure all text stays readable on the dark background - labels, captions, body text */
label, .stMarkdown, .stMarkdown p, .stMarkdown li, p, span, div {
    color: #F3F1FA;
}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
    color: #D8D2EC !important;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {
    color: #D8D2EC !important;
}
/* Placeholder text inside inputs */
.stTextInput input::placeholder {
    color: #8A8299 !important;
    opacity: 1;
}
/* Selectbox dropdown text and options - boosted specificity to beat the widget's own built-in styling */
div[data-baseweb="select"] * {
    color: #F3F1FA !important;
}
div[data-baseweb="popover"]:not(#___boost___) {
    background-color: #1C1826 !important;
}
div[data-baseweb="popover"] *:not(#___boost___) {
    background-color: #1C1826 !important;
    color: #F3F1FA !important;
}
[data-testid="stSelectboxVirtualDropdown"]:not(#___boost___),
[data-testid="stSelectboxVirtualDropdown"] *:not(#___boost___) {
    background-color: #1C1826 !important;
    color: #F3F1FA !important;
}
div[data-baseweb="popover"] li:hover:not(#___boost___),
div[data-baseweb="popover"] [role="option"]:hover:not(#___boost___),
[data-testid="stSelectboxVirtualDropdown"] li:hover:not(#___boost___) {
    background-color: #2C2536 !important;
}
/* Success/warning/error message boxes - colored tint background, light readable text */
[data-testid="stAlert"] {
    border-radius: 10px;
}
[data-testid="stAlert"] p {
    color: #F3F1FA !important;
    font-weight: 500;
}
div[data-testid="stAlertContentSuccess"] {
    background-color: rgba(34, 197, 94, 0.18) !important;
    border: 1px solid rgba(34, 197, 94, 0.4) !important;
}
div[data-testid="stAlertContentError"] {
    background-color: rgba(239, 68, 68, 0.18) !important;
    border: 1px solid rgba(239, 68, 68, 0.4) !important;
}
div[data-testid="stAlertContentWarning"] {
    background-color: rgba(245, 158, 11, 0.18) !important;
    border: 1px solid rgba(245, 158, 11, 0.4) !important;
}
div[data-testid="stAlertContentInfo"] {
    background-color: rgba(59, 130, 246, 0.18) !important;
    border: 1px solid rgba(59, 130, 246, 0.4) !important;
}

/* Hide Streamlit's built-in "Press Enter to submit form" hint text */
[data-testid="InputInstructions"] {
    display: none;
}

/* Overall app background - deep, subtle depth */
.stApp {
    background: radial-gradient(circle at 20% 0%, #241B33 0%, #12101A 55%);
}

/* Title - pink to purple gradient, only on the headline */
h1 {
    background: linear-gradient(90deg, #EC4899, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    margin-bottom: 0.2rem !important;
}

/* Section headers */
h2, h3 {
    color: #E9E4FA !important;
    margin-top: 1.8rem !important;
}

/* Sidebar - dark card panel */
[data-testid="stSidebar"] {
    background: #171320;
    border-right: 1px solid #2A2438;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #E9E4FA !important;
}

/* Buttons - gradient accent, used deliberately (not everywhere) */
.stButton>button, .stFormSubmitButton>button {
    background: linear-gradient(90deg, #EC4899, #A78BFA);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 2px 12px rgba(236, 72, 153, 0.25);
}
.stButton>button:hover, .stFormSubmitButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.35);
    color: white;
}

/* Sidebar buttons - subtle outline, not competing with main CTAs */
[data-testid="stSidebar"] .stButton>button {
    background: #241F30;
    color: #E9E4FA !important;
    box-shadow: none;
    border: 1px solid #33293F;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: #2C2536;
}

/* Form containers -> dark card, subtle border, no heavy shadow */
div[data-testid="stForm"] {
    background: #1C1826;
    border-radius: 16px;
    padding: 1.8rem;
    border: 1px solid #2E2740;
    margin-bottom: 1rem;
}

/* Metric cards - dark, gradient number for net/highlight feel */
div[data-testid="stMetric"] {
    background: #1C1826;
    border-radius: 14px;
    padding: 1.1rem;
    border: 1px solid #2E2740;
}
div[data-testid="stMetric"] label {
    color: #9C93B5 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #F3F1FA !important;
}

/* Expanders in sidebar */
[data-testid="stSidebar"] div[data-testid="stExpander"] {
    background: #1C1826;
    border-radius: 10px;
    border: 1px solid #2E2740;
    margin-bottom: 0.7rem;
}

/* Text inputs / selects / number inputs - dark fields */
.stTextInput input, .stNumberInput input, div[data-baseweb="select"] {
    background-color: #241F30 !important;
    color: #F3F1FA !important;
    border-color: #33293F !important;
}

/* Tables - dark rows, soft rounded corners */
.stTable, [data-testid="stTable"] {
    border-radius: 12px;
    overflow: hidden;
}
.stTable table, [data-testid="stTable"] table {
    background: #1C1826;
    color: #F3F1FA;
}
.stTable td, [data-testid="stTable"] td, .stTable th, [data-testid="stTable"] th {
    padding: 0.6rem 0.8rem !important;
    border-color: #2E2740 !important;
}
/* Top header bar (Deploy button / menu area) - match dark theme instead of white */
[data-testid="stHeader"] {
    background: #12101A !important;
}
[data-testid="stToolbar"] {
    background: transparent !important;
}
[data-testid="stHeader"] button, [data-testid="stHeader"] svg {
    color: #F3F1FA !important;
    fill: #F3F1FA !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.2rem;">
    <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4b0.png" width="42" height="42">
    <h1 style="margin:0; padding:0;">Personal Finance Chatbot</h1>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Options")

    if st.button("Reset (start fresh)"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # Everything below needs a logged-in user
    if "user_id" in st.session_state:
        user_id = st.session_state.user_id

        # ---------- Filter / Search ----------
        with st.expander("🔍 Filter expenses"):
            categories = get_categories(user_id)
            filter_category = st.selectbox(
                "Category", options=["All"] + categories, key="filter_category"
            )
            col_a, col_b = st.columns(2)
            with col_a:
                filter_start = st.date_input("From", value=None, key="filter_start")
            with col_b:
                filter_end = st.date_input("To", value=None, key="filter_end")

        # ---------- Edit budget limits ----------
        with st.expander("🎯 Edit budget limits"):
            budgets = get_all_budgets(user_id)
            budget_categories = [b[0] for b in budgets]

            edit_choice = st.selectbox(
                "Category to set/update",
                options=budget_categories + ["+ New category"],
                key="budget_edit_choice"
            )
            if edit_choice == "+ New category":
                edit_category = st.text_input("New category name", key="budget_new_category")
            else:
                edit_category = edit_choice

            current_limit = get_budget_limit(user_id, edit_category) if edit_category else None
            new_limit = st.number_input(
                "Limit amount",
                min_value=0.0,
                value=float(current_limit) if current_limit else 0.0,
                step=50.0,
                key="budget_new_limit"
            )
            if st.button("Save budget limit"):
                if edit_category:
                    update_budget_limit(user_id, edit_category, new_limit)
                    st.success(f"{edit_category} budget set to {new_limit}.")
                    st.rerun()
                else:
                    st.error("Enter a category name first.")

        # ---------- Delete individual expenses ----------
        with st.expander("🗑️ Delete an expense"):
            all_expenses = get_expenses(user_id)
            if all_expenses:
                options = {
                    f"#{e[0]} — {e[1]} — {e[2]} on {e[3]}": e[0] for e in all_expenses
                }
                choice = st.selectbox("Select expense", options=list(options.keys()), key="delete_choice")
                if st.button("Delete selected expense"):
                    expense_id = options[choice]
                    if delete_expense(expense_id, user_id):
                        st.success("Expense deleted.")
                        st.rerun()
                    else:
                        st.error("Could not delete that expense.")
            else:
                st.write("No expenses to delete yet.")

        # ---------- Delete individual income entries ----------
        with st.expander("🗑️ Delete an income entry"):
            all_income = get_income(user_id)
            if all_income:
                income_options = {
                    f"#{i[0]} — {i[1]} — {i[2]} on {i[3]}": i[0] for i in all_income
                }
                income_choice = st.selectbox("Select income entry", options=list(income_options.keys()), key="delete_income_choice")
                if st.button("Delete selected income entry"):
                    income_id = income_options[income_choice]
                    if delete_income(income_id, user_id):
                        st.success("Income entry deleted.")
                        st.rerun()
                    else:
                        st.error("Could not delete that income entry.")
            else:
                st.write("No income entries to delete yet.")

        # ---------- Export CSV ----------
        with st.expander("📤 Export data"):
            export_expenses = get_expenses(user_id)
            if export_expenses:
                csv_data = expenses_to_csv(export_expenses)
                st.download_button(
                    label="Download expenses as CSV",
                    data=csv_data,
                    file_name=f"{st.session_state.name}_expenses.csv",
                    mime="text/csv"
                )
            else:
                st.write("No expenses to export yet.")

            export_income = get_income(user_id)
            if export_income:
                income_csv_data = income_to_csv(export_income)
                st.download_button(
                    label="Download income as CSV",
                    data=income_csv_data,
                    file_name=f"{st.session_state.name}_income.csv",
                    mime="text/csv"
                )
            else:
                st.write("No income to export yet.")

if "user_id" not in st.session_state:
    with st.form("name_form"):
        name = st.text_input("What's your name?")
        _, mid_col, _ = st.columns([1, 1, 1])
        with mid_col:
            submitted = st.form_submit_button("Enter", use_container_width=True)
    if submitted and name:
        st.session_state.user_id = get_or_create_user(name)
        st.session_state.name = name
        st.rerun()
else:
    st.write(f"Hi {st.session_state.name}! Type a message below.")
    user_id = st.session_state.user_id

    with st.form("message_form"):
        text = st.text_input(
            "Log expense",
            placeholder="200 on food, or set budget 2000 for food"
        )
        _, mid_col, _ = st.columns([1, 1, 1])
        with mid_col:
            send = st.form_submit_button("Enter", use_container_width=True)

    if send and text:
        set_match = re.search(r'set budget\s+(\d+(?:\.\d+)?)\s+for\s+(\w+)', text, re.IGNORECASE)

        if set_match:
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

    st.markdown("---")
    st.subheader("💵 Log Income")
    with st.form("income_form"):
        income_col1, income_col2 = st.columns(2)
        with income_col1:
            income_source = st.text_input("Source (e.g. Salary, Freelance)")
        with income_col2:
            income_amount = st.number_input("Amount received", min_value=0.0, step=50.0)
        _, income_mid_col, _ = st.columns([1, 1, 1])
        with income_mid_col:
            income_submit = st.form_submit_button("Enter", use_container_width=True)

    if income_submit:
        if income_source and income_amount > 0:
            today = str(date.today())
            add_income(user_id, income_source.strip().capitalize(), income_amount, today)
            st.success(f"💵 Logged {income_amount} received from {income_source.strip().capitalize()}.")
        else:
            st.error("Please enter both a source and an amount greater than 0.")

    st.markdown("---")
    st.subheader("📊 View Summary")
    if st.button("Show My Summary"):
        filter_category = st.session_state.get("filter_category", "All")
        filter_start = st.session_state.get("filter_start")
        filter_end = st.session_state.get("filter_end")

        category_arg = None if filter_category in (None, "All") else filter_category
        start_arg = str(filter_start) if filter_start else None
        end_arg = str(filter_end) if filter_end else None

        expenses = get_expenses(user_id, category=category_arg, start_date=start_arg, end_date=end_arg)
        total_expenses = 0
        if expenses:
            st.write("### 🧾 Your spending so far:")
            st.table([{"Category": category_label(e[1]), "Amount": e[2], "Date": e[3]} for e in expenses])
            total_expenses = sum(e[2] for e in expenses)
        else:
            st.write("No expenses logged yet.")

        income_entries = get_income(user_id, start_date=start_arg, end_date=end_arg)
        total_income = 0
        if income_entries:
            st.write("### 💵 Money received:")
            st.table([{"Source": income_label(i[1]), "Amount": i[2], "Date": i[3]} for i in income_entries])
            total_income = sum(i[2] for i in income_entries)
        else:
            st.write("No income logged yet.")

        st.markdown("---")
        net = total_income - total_expenses
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("💵 Total received", f"{total_income:.2f}")
        with m2:
            st.metric("🧾 Total spent", f"{total_expenses:.2f}")
        with m3:
            st.metric("📈 Net", f"{net:.2f}", delta=f"{net:.2f}")

    st.markdown("---")
    _, back_mid_col, _ = st.columns([1, 1, 1])
    with back_mid_col:
        if st.button("Back", use_container_width=True):
            st.session_state.clear()
            st.rerun()