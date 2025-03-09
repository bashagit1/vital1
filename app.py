import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ✅ Ensure this is the first Streamlit command
st.set_page_config(page_title="Vital Signs Dashboard", layout="wide")

# Authentication
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "doctor": {"password": "doctor123", "role": "Doctor"},
    "staff": {"password": "staff123", "role": "Staff"}
}

def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["role"] = users[username]["role"]
            st.session_state["username"] = username
            st.sidebar.success(f"Logged in as {users[username]['role']}")
        else:
            st.sidebar.error("Invalid credentials")

if "logged_in" not in st.session_state:
    login()
    if not st.session_state.get("logged_in", False):
        st.stop()

# Predefined patient list with unique IDs
patients = {
    101: "John Doe",
    102: "Jane Smith",
    103: "Alice Johnson",
    104: "Robert Brown",
    105: "Emily Davis",
    106: "Michael Wilson",
    107: "Sarah Miller",
    108: "David Lee",
    109: "Sophia Anderson",
    110: "James Taylor",
    111: "Olivia Martinez",
    112: "William Harris",
    113: "Isabella Clark",
    114: "Benjamin Lewis",
    115: "Charlotte Walker",
    116: "Lucas Hall",
    117: "Amelia Allen",
    118: "Mason Young",
    119: "Harper King",
    120: "Ethan Wright",
    121: "Evelyn Scott",
    122: "Alexander Green",
    123: "Abigail Adams",
    124: "Henry Baker",
    125: "Ella Carter"
}

# Database connection
def init_db():
    conn = sqlite3.connect("vital_signs.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vitals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        patient_name TEXT,
                        bp TEXT,
                        pulse INTEGER,
                        spo2 INTEGER,
                        temperature REAL,
                        glucose REAL,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Insert Data
def insert_vital(patient_id, patient_name, bp, pulse, spo2, temperature, glucose):
    conn = sqlite3.connect("vital_signs.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vitals (patient_id, patient_name, bp, pulse, spo2, temperature, glucose) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (patient_id, patient_name, bp, pulse, spo2, temperature, glucose))
    conn.commit()
    conn.close()

# Fetch Data
def fetch_vitals(month=None, patient_id=None):
    conn = sqlite3.connect("vital_signs.db")
    query = "SELECT * FROM vitals ORDER BY recorded_at DESC"
    if month and patient_id:
        query = f"SELECT * FROM vitals WHERE strftime('%m', recorded_at) = '{month:02d}' AND patient_id={patient_id} ORDER BY recorded_at DESC"
    elif month:
        query = f"SELECT * FROM vitals WHERE strftime('%m', recorded_at) = '{month:02d}' ORDER BY recorded_at DESC"
    elif patient_id:
        query = f"SELECT * FROM vitals WHERE patient_id={patient_id} ORDER BY recorded_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize DB
init_db()

# Streamlit UI
st.title("🩺 Vital Signs Monitoring System")

# Data Entry Form (Only Staff can enter data)
if st.session_state["role"] == "Staff":
    with st.form("vital_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            patient_id = st.selectbox("Select Patient", options=patients.keys(), format_func=lambda x: f"{x} - {patients[x]}")
            patient_name = patients[patient_id]
            bp = st.text_input("Blood Pressure (e.g. 120/80)")
        with col2:
            pulse = st.number_input("Pulse Rate", min_value=30, max_value=200, value=70)
            spo2 = st.number_input("SpO₂ (%)", min_value=50, max_value=100, value=98)
        with col3:
            temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=36.5)
            glucose = st.number_input("Glucose Level (mmol/L, Malaysia Standard)", min_value=2.0, max_value=20.0, value=5.5)
        submit = st.form_submit_button("Submit Vital Signs")

    if submit:
        insert_vital(patient_id, patient_name, bp, pulse, spo2, temperature, glucose)
        st.success(f"Vital signs recorded for {patient_name}!")

# Display Data (Only Admin & Doctor can see charts and reports)
if st.session_state["role"] in ["Admin", "Doctor"]:
    selected_month = st.selectbox("Select Month", list(range(1, 13)), format_func=lambda x: datetime(2025, x, 1).strftime("%B"))
    selected_patient = st.selectbox("Select Patient for Report", options=[None] + list(patients.keys()), format_func=lambda x: "All Patients" if x is None else f"{x} - {patients[x]}")
    df = fetch_vitals(selected_month, selected_patient)
    st.dataframe(df)

st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
