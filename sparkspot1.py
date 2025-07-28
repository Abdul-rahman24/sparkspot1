import streamlit as st
import pandas as pd
import random
import datetime
import pydeck as pdk
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
page = st.sidebar.radio("Go to", ["Home", "Book Slot", "Booking Confirmed"])

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
    s["waiting_time"] = s["queue_length"] * 5  # 5 mins per vehicle

df_live = pd.DataFrame(stations)
recommended = max(stations, key=lambda x: x["score"])

# ---------- HOME PAGE ---------- #
if page == "Home":
    st.markdown("<h1 class='title-style'>🚗 SparkSpot: Smart EV Charging</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-style'>AI-powered recommendations for EV charging stations in Chennai.</p>", unsafe_allow_html=True)

    # 📊 All Station Table
    st.subheader("📊 All Station Status")
    df_display = df_live[["name", "location", "available_ports", "queue_length", "score"]]
    df_display.columns = ["Station", "Location", "Available Ports", "Queue Length", "AI Score"]
    st.dataframe(df_display.style.format({"AI Score": "{:.2f}"}), use_container_width=True)

    # 🔍 Recommendation
    st.subheader("✅ Recommended Station")
    st.success(f"**{recommended['name']}** at {recommended['location']} is the best option!")
    st.write(f"🔌 Available Ports: {recommended['available_ports']}, ⏱ Queue Length: {recommended['queue_length']}, 🤖 AI Score: {recommended['score']:.2f}")

    # 🗺️ Custom Map with Colors
    st.subheader("📍 Station Map")
    color_map = {recommended['name']: [0, 255, 0]}  # green
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_live,
        get_position='[lon, lat]',
        get_color="[0, 255, 0] if name == '" + recommended['name'] + "' else [255, 0, 0]",
        get_radius=100,
    )
    view_state = pdk.ViewState(latitude=13.04, longitude=80.23, zoom=11)
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", layers=[layer], initial_view_state=view_state))

    # 🔗 Book Button
    st.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <a href='/?page=Book+Slot' style='background-color: #0077b6; color: white; padding: 10px 25px; border-radius: 5px; text-decoration: none;'>
                🚘 Book a Charging Slot
            </a>
        </div>
    """, unsafe_allow_html=True)

# ---------- BOOK SLOT PAGE ---------- #
if page == "Book Slot":
    st.markdown("<h1 class='title-style'>📅 Book a Charging Slot</h1>", unsafe_allow_html=True)

    with st.form("booking_form"):
        selected_station = st.selectbox("Select Station", [s["name"] for s in stations])
        station_info = next((s for s in stations if s["name"] == selected_station), None)
        st.info(f"⏳ Estimated Waiting Time: {station_info['waiting_time']} minutes")
        vehicle = st.text_input("Vehicle Number")
        phone = st.text_input("Phone Number")
        submit = st.form_submit_button("✅ Confirm Booking Slot")

        if submit and selected_station and vehicle and phone:
            st.session_state["booking"] = {
                "station": selected_station,
                "location": station_info['location'],
                "vehicle": vehicle,
                "phone": phone,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.experimental_set_query_params(page="Booking+Confirmed")
            st.experimental_rerun()

# ---------- BOOKING CONFIRMED PAGE ---------- #
if page == "Booking Confirmed" and "booking" in st.session_state:
    booking = st.session_state["booking"]
    st.markdown("<h1 class='title-style'>🎉 Booking Confirmed!</h1>", unsafe_allow_html=True)
    st.success("Your EV charging slot has been successfully booked.")

    st.markdown("""
    <ul>
        <li><b>Station:</b> {station}</li>
        <li><b>Location:</b> {location}</li>
        <li><b>Vehicle Number:</b> {vehicle}</li>
        <li><b>Phone Number:</b> {phone}</li>
        <li><b>Time:</b> {time}</li>
    </ul>
    """.format(**booking), unsafe_allow_html=True)

    st.balloons()

