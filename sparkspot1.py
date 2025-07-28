import streamlit as st
import pandas as pd
import random
import datetime
import pydeck as pdk
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="SparkSpot AI", layout="centered")

st.title("⚡ SparkSpot – AI Charging Station Recommender")
st.markdown("🔋 **Smart EV Charging Recommendation + Booking + Analytics**")

# Simulate training data
def generate_training_data():
    data = []
    for _ in range(300):
        ports = random.randint(0, 5)
        queue = random.randint(0, 10)
        chosen = 1 if ports > 2 and queue < 5 else 0
        data.append([ports, queue, chosen])
    return pd.DataFrame(data, columns=["available_ports", "queue_length", "chosen"])

df_train = generate_training_data()
X = df_train[["available_ports", "queue_length"]]
y = df_train["chosen"]
model = RandomForestClassifier()
model.fit(X, y)

# Simulate live stations with locations
def simulate_live_stations():
    return [
        {"name": "SparkSpot A", "location": "Anna Nagar", "lat": 13.0833, "lon": 80.2337, "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
        {"name": "SparkSpot B", "location": "Velachery", "lat": 12.9762, "lon": 80.2218, "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
        {"name": "SparkSpot C", "location": "T Nagar", "lat": 13.0418, "lon": 80.2332, "available_ports": random.randint(0, 5), "queue_length": random.randint(0, 10)},
    ]

stations = simulate_live_stations()

# Predict AI score
for s in stations:
    s["score"] = model.predict_proba([[s["available_ports"], s["queue_length"]]])[0][1]

df_live = pd.DataFrame(stations)

st.subheader("📍 Live Station Info")
st.dataframe(df_live[["name", "location", "available_ports", "queue_length", "score"]].sort_values(by="score", ascending=False))

# 🟢 Recommended Station
recommended = max(stations, key=lambda x: x["score"])
st.success(f"✅ Recommended: **{recommended['name']}** at {recommended['location']}")
st.write(f"🔌 Available Ports: {recommended['available_ports']} | ⏱ Queue Length: {recommended['queue_length']} | 🧠 AI Score: {recommended['score']:.2f}")

# 📌 Google Map View
st.subheader("🗺️ Station Map")
st.map(pd.DataFrame(stations)[["lat", "lon"]])

# 📘 Booking Section
st.subheader("📝 Book Your Charging Slot")
with st.form("booking_form"):
    selected_station = st.selectbox("Select Station", [s["name"] for s in stations])
    name = st.text_input("Your Name")
    vehicle = st.text_input("Vehicle Number")
    book = st.form_submit_button("🔒 Book Now")

    if book and name and vehicle:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"✅ Booking Confirmed at {selected_station} for {name} ({vehicle}) on {now}")

# 📊 Analytics Section
st.subheader("📊 Analytics Dashboard")
st.write("### 🔝 Station AI Scores")
st.bar_chart(df_live.set_index("name")["score"])

st.write("### 🚦 Queue Lengths")
st.line_chart(df_live.set_index("name")["queue_length"])

st.write("### ⚡ Available Ports")
st.area_chart(df_live.set_index("name")["available_ports"])
