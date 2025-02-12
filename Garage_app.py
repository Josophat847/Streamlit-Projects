import streamlit as st
import pandas as pd
from datetime import datetime

# ✅ Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title="GO AHEAD MOTORS", page_icon="🔧", layout="wide")

# ✅ Persistent Storage for Authentication & Jobs
@st.cache_data
def load_jobs():
    return pd.DataFrame(columns=["Date", "Time", "Car Type", "Car Owner", "Student", "Price (MWK)", "Commission %", "Student Earnings (MWK)", "Manager Earnings (MWK)"])

if "jobs" not in st.session_state:
    st.session_state.jobs = load_jobs()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "manager_accounts" not in st.session_state:
    st.session_state.manager_accounts = {"admin": "admin123"}  # Default accounts for testing
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "view_records" not in st.session_state:
    st.session_state.view_records = False

# Authentication Functions
def login(username, password):
    if username in st.session_state.manager_accounts and st.session_state.manager_accounts[username] == password:
        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.rerun()
    else:
        st.error("Invalid username or password")

def signup(username, password):
    if username in st.session_state.manager_accounts:
        st.error("Username already exists. Choose another.")
    else:
        st.session_state.manager_accounts[username] = password
        st.success("Account created successfully! Please log in.")

# Login / Signup UI
if not st.session_state.authenticated:
    st.image("https://cdn-icons-png.flaticon.com/512/2203/2203124.png", width=100)
    st.title("GO AHEAD MOTORS")
    st.subheader("🔒 Manager Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)
    
    with tab2:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            signup(new_username, new_password)
    
    st.stop()

# Main Garage Monitoring UI for Mobile
st.image("https://cdn.pixabay.com/photo/2016/03/29/11/15/garage-1282735_1280.jpg", use_column_width=True)
st.title("GO AHEAD MOTORS - Garage Monitoring System")
st.write(f"Welcome, **{st.session_state.current_user}**!")
st.markdown("---")

# Mobile-Friendly Job Entry Form
st.subheader("📝 Job Details")
with st.form("log_job"):
    date = st.date_input("Date", datetime.today())
    time = st.time_input("Time", datetime.now().time())
    car_type = st.text_input("Car Type")
    car_owner = st.text_input("Car Owner Name")
    student = st.text_input("Student Mechanic Name")
    price = st.number_input("Price Charged (MWK)", min_value=0.0, format="%.2f")
    commission = st.selectbox("Commission %", [10, 15, 20, 25, 30, 35, 40])
    submit_button = st.form_submit_button("🔧 Enter Payment")
    
    if submit_button:
        if car_type and car_owner and student and price > 0:
            student_earnings = (commission / 100) * price
            manager_earnings = price - student_earnings
            new_row = pd.DataFrame([{ 
                "Date": date, "Time": time, "Car Type": car_type, "Car Owner": car_owner, 
                "Student": student, "Price (MWK)": price, "Commission %": commission, 
                "Student Earnings (MWK)": student_earnings, "Manager Earnings (MWK)": manager_earnings
            }])
            st.session_state.jobs = pd.concat([st.session_state.jobs, new_row], ignore_index=True)
            st.success(f"✅ Payment added successfully for {student}!")
            st.rerun()
        else:
            st.error("All fields are required, and price must be greater than zero.")

# Toggle View for Job Records
if st.button("📂 View Records"):
    st.session_state.view_records = not st.session_state.view_records
    st.rerun()

# Display & Manage Job Records if toggled
if st.session_state.view_records:
    st.subheader("📋 Garage Records")
    if not st.session_state.jobs.empty:
        st.dataframe(st.session_state.jobs)
        if st.button("🗑 Clear All Records"):
            st.session_state.jobs = load_jobs()
            st.success("All job records have been cleared!")
            st.rerun()
        
        # Export Data Option
        st.download_button("📥 Download CSV", st.session_state.jobs.to_csv(index=False), "garage_records.csv", "text/csv")
    else:
        st.info("No Jobs logged yet.")

# Earnings Chart
if st.session_state.view_records and not st.session_state.jobs.empty:
    earnings_data = pd.DataFrame({
        "Category": ["Manager Earnings", "Student Earnings"],
        "Total Earnings (MWK)": [
            st.session_state.jobs["Manager Earnings (MWK)"].sum(),
            st.session_state.jobs["Student Earnings (MWK)"].sum()
        ]
    })
    chart = alt.Chart(earnings_data).mark_bar(color="#FFD700").encode(
        x=alt.X("Category", sort=None),
        y="Total Earnings (MWK)"
    ).properties(
        title="Earnings Summary"
    )
    st.altair_chart(chart, use_container_width=True)
