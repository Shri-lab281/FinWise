import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import hashlib
import re
from config import get_gemini_response   # Import Gemini helper

# --------------------------- DATABASE SETUP ---------------------------
conn = sqlite3.connect('finwise.db', check_same_thread=False)
c = conn.cursor()

# Create table for users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create table for expenses
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT,
    category TEXT,
    amount REAL NOT NULL,
    description TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')
conn.commit()

# --------------------------- SESSION INIT ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "email" not in st.session_state:
    st.session_state.email = None
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# --------------------------- AUTH FUNCTIONS ---------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    """Password must have 8+ chars, 1 upper, 1 lower, 1 number, 1 special char"""
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern, password)

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    return c.fetchone()

def register_user(username, email, password):
    if not validate_password(password):
        return "invalid"
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    
def reset_password(email, new_password):
    if not validate_password(new_password):
        return "invalid"
    c.execute("UPDATE users SET password=? WHERE email=?", (hash_password(new_password), email))
    conn.commit()
    return True

# --------------------------- PAGE CONFIG ---------------------------
st.set_page_config(page_title="FinWise", layout="wide", page_icon="💰")

# --------------------------- CSS STYLING ---------------------------
st.markdown("""
<style>
    .stButton>button {border-radius: 10px; background-color:#4CAF50; color:white; font-size:16px; padding:8px 20px;}
    .stButton>button:hover {background-color:#45a049; color:white;}
    .login-box {background-color:#f7f9fc; padding:40px; border-radius:15px; box-shadow:2px 2px 12px rgba(0,0,0,0.1);}
    .title {font-size:36px; font-weight:bold; color:#2E86C1; text-align:center;}
    .subtitle {font-size:16px; color:#555; text-align:center; margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2E86C1;'>💰 FinWise: AI-Powered Financial Literacy Tool</h1>", unsafe_allow_html=True)


# --------------------------- APP LOGIC ---------------------------
if not st.session_state.logged_in:
    
    st.markdown("<h4 style='text-align: center; color: #555;'>Track your expenses, get personalized investment advice, and improve your financial literacy!</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])  # center inputs using middle column
    with col2:
        auth_choice = st.radio("", ["Login", "Register", "Forgot Password"], horizontal=True, index=0, key="auth_choice")
        if auth_choice == "Login":
            email = st.text_input("email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[1]
                    st.session_state.email = user[2]  # email
                    st.success(f"Welcome back, {st.session_state.username} 🎉")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        elif auth_choice == "Register":
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Register"):
                if not username or not email or not password:
                    st.warning("⚠️ Please fill all fields")
                elif not validate_password(password):
                    st.warning("⚠️ Password must be 8+ chars, include uppercase, lowercase, number, special char")
                else:
                    if register_user(username, email, password):
                        st.success("✅ Registration successful! Please login now.")
                    else:
                        st.error("⚠️ Username or Email already exists.")

     # --------------------------- FORGOT PASSWORD ---------------------------
        elif auth_choice == "Forgot Password":
            email = st.text_input("Enter your registered Email")
            new_password = st.text_input("Enter new Password", type="password")
            if st.button("Reset Password"):
                if not email or not new_password:
                    st.warning("⚠️ Please fill all fields")
                elif not validate_password(new_password):
                    st.warning("⚠️ Password must be 8+ chars, include uppercase, lowercase, number, special char")
                else:
                    if reset_password(email, new_password):
                        st.success("✅ Password reset successful! You can login now.")
                    else:
                        st.error("⚠️ Email not found.")                   
    # --------------------------- SIDEBAR ---------------------------
else:  

    st.sidebar.success(f"Welcome {st.session_state.username}")

    # Logout button at top of sidebar
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    menu = ["🏠 Home", "➕ Add Expense", "📊 Dashboard", "📈 Investment Advice", "🤖 Chatbot"]
    choice = st.sidebar.radio("Go to", menu)

# --------------------------- HOME ---------------------------
    if choice == "🏠 Home":
        st.subheader("Welcome to FinWise!")
        st.write("""
            FinWise helps you track expenses, manage savings, and get personalized investment advice.  
        It also includes an AI chatbot for financial literacy in multiple languages. 
            """)
        col1, col2 = st.columns(2)
        with col1:
            st.info("✅ Track & categorize your expenses automatically")
            st.info("✅ Get monthly trends and saving suggestions")
        with col2:
            st.success("🚀 Personalized investment advice with AI")
            st.success("🌍 Multilingual chatbot for financial literacy")

    # --------------------------- ADD EXPENSE ---------------------------
    elif choice == "➕ Add Expense":
        st.subheader("➕ Add a New Expense")
        with st.form("expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", datetime.today())
                amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            with col2:
                description = st.text_input("Description (e.g., Uber ride, Grocery shopping)")

            submitted = st.form_submit_button("Add Expense")
            if submitted:
                with st.spinner("Categorizing your expense..."):
                # AI auto-categorization
                    prompt = f"Categorize this expense into one word (Food, Transport, Bills, Entertainment, Other): {description}"
                    category = get_gemini_response(prompt).strip().split()[0]

                c.execute(
                        "INSERT INTO expenses (user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                        (st.session_state.username, str(date), category, amount, description)
                )
                conn.commit()
                st.success(f"✅ Expense added successfully! Auto-categorized as **{category}**")

    # --------------------------- DASHBOARD ---------------------------
    elif choice == "📊 Dashboard":
        st.subheader("📊 Expense Dashboard")
        df = pd.read_sql("SELECT * FROM expenses WHERE user_id=?", conn, params=(st.session_state.username,))

        if df.empty:
            st.warning("⚠️ No expenses added yet.")
        else:
            st.dataframe(df, use_container_width=True)

            col1, col2 = st.columns(2)

            # Pie chart by category
            with col1:
                category_summary = df.groupby("category")["amount"].sum().reset_index()
                fig1 = px.pie(category_summary, values="amount", names="category",
                            title="Expenses by Category", color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig1, use_container_width=True)

            # Line chart for monthly trend
            with col2:
                df['date'] = pd.to_datetime(df['date'])
                monthly = df.groupby(df['date'].dt.to_period("M"))['amount'].sum().reset_index()
                monthly['date'] = monthly['date'].astype(str)
                fig2 = px.line(monthly, x="date", y="amount",
                            title="Monthly Expense Trend", markers=True,
                            line_shape="spline", color_discrete_sequence=["#2E86C1"])
                st.plotly_chart(fig2, use_container_width=True)

            # Savings suggestion
            st.subheader("💡 Savings Suggestion")
            total_expense = df['amount'].sum()
            st.metric("Total Expenses", f"₹{total_expense:.2f}")

            income = st.number_input("Enter your monthly income (₹)", min_value=0.0, step=1000.0)
            if income > 0:
                with st.spinner("Calculating smart saving suggestions..."):
                    prompt = f"My monthly income is {income}, my total expenses are {total_expense}. Suggest smart saving strategies."
                    advice = get_gemini_response(prompt)
                st.success(advice)

    # --------------------------- INVESTMENT ADVICE ---------------------------
    elif choice == "📈 Investment Advice":
        st.subheader("📈 Personalized Investment Advice")
        col1, col2 = st.columns(2)
        with col1:
            income = st.number_input("Monthly Income (₹)", min_value=0.0, step=1000.0)
            savings = st.number_input("Current Savings (₹)", min_value=0.0, step=1000.0)
        with col2:
            risk = st.selectbox("Risk Profile", ["Low", "Medium", "High"])
            goals = st.text_area("Your Financial Goals (e.g., buy a house, retire early, kids education)")

        if st.button("🔮 Get AI-Powered Advice"):
            prompt = f"""
            I have a monthly income of {income}, current savings of {savings}, and my risk profile is {risk}.
            My financial goals are: {goals}.
            Please suggest personalized investment strategies in simple, actionable steps.
            """
            advice = get_gemini_response(prompt)
            st.success(advice)

    # --------------------------- CHATBOT ---------------------------
    elif choice == "🤖 Chatbot":
        st.subheader("💬 Financial Literacy Chatbot")
        user_input = st.text_area("Ask your financial questions here (any language)")

        if st.button("Get Answer") and user_input.strip():
            with st.spinner("Thinking..."):
                answer = get_gemini_response(user_input)
                st.info(answer)
