import streamlit as st
import pandas as pd
import random
import datetime

from sklearn.ensemble import RandomForestClassifier

# ---------- PAGE SETUP ---------- #
st.set_page_config(page_title="SparkSpot ⚡", layout="wide", page_icon="🚗")

# ---------- STYLING ---------- #
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to right, #eef2f3, #8e9eab);
        color: #000;
    }
    .title-style {
        font-size: 2.5em;
        font-weight: bold;
        color: #004d7a;
    }
    .subtitle-style {
        font-size: 1.3em;
        color: #006494;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ---------- #
st.sidebar.title("🚗 SparkSpot Navigation")
page = st.sidebar.radio("Go to", ["Home", "Book Slot"])

# ---------- DATA GENERATION ---------- #
def generate_model():
    data = []
    for _ in range(300):
        ports = random.randint(0, 5)
        queue = random.randint(0, 10)
        chosen = 1 if ports > 2 and queue < 5 else 0
        data.append([ports, queue, chosen])
    df = pd.DataFrame(data, columns=["available_ports", "queue_length", "chosen"])
    model = RandomForestClassifier()
    model.fit(df[["available_ports", "queue_length"]], df["chosen"])
    return model

model = generate_model()

# ---------- STATION DATA ---------- #
stations = [
    {"name": "SparkSpot A", "location": "Anna Nagar", "lat": 13.0878, "lon": 80.2072,
     "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
    {"name": "SparkSpot B", "location": "Velachery", "lat": 12.9784, "lon": 80.2215,
     "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
    {"name": "SparkSpot C", "location": "T Nagar", "lat": 13.0425, "lon": 80.2337,
     "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
]

for s in stations:
    s["score"] = model.predict_proba([[s["available_ports"], s["queue_length"]]])[0][1]

df_live = pd.DataFrame(stations)

# ---------- HOME PAGE ---------- #
if page == "Home":
    st.markdown("<h1 class='title-style'>🚗 SparkSpot: Smart EV Charging</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-style'>AI-recommended charging station based on real-time availability and queue length.</p>", unsafe_allow_html=True)

    st.subheader("🔍 Best Station Recommendation")
    recommended = max(stations, key=lambda x: x["score"])
    st.success(f"✅ **{recommended['name']}** at {recommended['location']} is recommended")
    st.write(f"🔌 Available Ports: {recommended['available_ports']} | ⏱ Queue Length: {recommended['queue_length']} | 🧠 AI Score: {recommended['score']:.2f}")

    st.subheader("📍 View Station Locations on Map")
    st.map(df_live[["lat", "lon"]])

# ---------- BOOKING PAGE ---------- #
if page == "Book Slot":
    st.markdown("<h1 class='title-style'>📅 Book a Charging Slot</h1>", unsafe_allow_html=True)

    with st.form("booking_form"):
        selected_station = st.selectbox("Select Station", df_live["name"].tolist())
        name = st.text_input("Your Name")
        vehicle = st.text_input("Vehicle Number")
        submit = st.form_submit_button("🔒 Book Now")

        if submit and name and vehicle:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"✅ Booking Confirmed at {selected_station} for {name} ({vehicle}) on {now}")
