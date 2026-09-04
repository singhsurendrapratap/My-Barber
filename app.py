import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="My Barber", page_icon="💈", layout="wide")

# --- ENGINE: INITIALIZE MOCK BACKEND DATA IN SESSION STATE ---
if "shops" not in st.session_state:
    st.session_state.shops = [
        {
            "id": 1,
            "name": "Royal Cut Salon",
            "lat": 23.1765,
            "lon": 75.7885,
            "address": "Main Market, Near Clock Tower",
            "outside_photo": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400",
            "avg_time_per_cut": 20, # minutes
            "queue": ["Rahul (Token #20)", "Amit (Token #21)", "Vikas (Token #22)"]
        },
        {
            "id": 2,
            "name": "Classic Barber Hub",
            "lat": 23.1810,
            "lon": 75.7920,
            "address": "Station Road, Opposite Bank",
            "outside_photo": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=400",
            "avg_time_per_cut": 25, # minutes
            "queue": ["Deepak (Token #14)"]
        }
    ]

# --- TOP-LEFT NAVIGATION MENU ---
st.sidebar.title("💈 My Barber")
role = st.sidebar.radio("Select View Mode:", ["Customer View", "Shop Owner View"])

# ==========================================
# 1. CUSTOMER VIEW
# ==========================================
if role == "Customer View":
    st.title("✂️ Find Nearby Shops & Skip The Waiting Line")
    st.write("Check real-time crowds, view shop photos, and join the virtual queue remotely.")

    # Location Permission Check
    loc = get_geolocation()
    user_lat, user_lon = 23.1765, 75.7885 # Default fallback coordinates
    if loc and "coords" in loc:
        user_lat = loc["coords"]["latitude"]
        user_lon = loc["coords"]["longitude"]

    # Render Map
    m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
    folium.Marker([user_lat, user_lon], popup="Your Location", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)

    # Plot Shops with Dynamic Wait-Color Status
    for shop in st.session_state.shops:
        count = len(shop["queue"])
        color = "green" if count <= 2 else ("orange" if count <= 4 else "red")
        popup_text = f"{shop['name']} | Waiting: {count} people"
        folium.Marker(
            [shop["lat"], shop["lon"]], 
            popup=popup_text, 
            icon=folium.Icon(color=color, icon="cut", prefix="fa")
        ).add_to(m)

    st_folium(m, width=1000, height=350)
    st.divider()

    # Shop Selection & Queue Joining
    shop_names = [s["name"] for s in st.session_state.shops]
    selected_shop_name = st.selectbox("Select a Barber Shop to view details or join line:", shop_names)
    
    selected_shop = next(s for s in st.session_state.shops if s["name"] == selected_shop_name)
    current_wait_count = len(selected_shop["queue"])
    approx_wait_time = current_wait_count * selected_shop["avg_time_per_cut"]

    # Display Store Photos
    col_img1, col_img2, col_info = st.columns([1, 1, 2])
    with col_img1:
        st.image(selected_shop["outside_photo"], caption="Outside View", use_column_width=True)
    with col_img2:
        st.image(selected_shop["inside_photo"], caption="Inside View", use_column_width=True)
    with col_info:
        st.subheader(selected_shop["name"])
        st.write(f"📍 **Address:** {selected_shop['address']}")
        st.write(f"👥 **Current People Waiting:** `{current_wait_count}`")
        st.write(f"⏱️ **Approx. Wait Time:** `{approx_wait_time} mins`")

        # Join Queue Form
        with st.form("join_queue_form"):
            st.write("### Join Virtual Line")
            cust_name = st.text_input("Enter Your Name")
            add_family = st.checkbox("Adding a family member (+1 Child/Friend)")
            remind_mins = st.number_input("How many minutes do you need to travel to reach shop?", min_value=5, max_value=60, value=15)
            submit = st.form_submit_button("Confirm & Join Queue")

            if submit:
                if cust_name.strip():
                    ticket_name = f"{cust_name} (+1)" if add_family else cust_name
                    token_num = len(selected_shop["queue"]) + 20
                    entry = f"{ticket_name} (Token #{token_num})"
                    
                    # ENGINE LOGIC: Append customer to selected shop's backend queue
                    selected_shop["queue"].append(entry)
                    st.success(f"Success! You joined the line as '{entry}'. Set your alarm: We will notify you {remind_mins} mins before your turn!")
                    st.rerun()
                else:
                    st.error("Please enter your name before joining.")

# ==========================================
# 2. SHOP OWNER VIEW (SPLIT DASHBOARD)
# ==========================================
elif role == "Shop Owner View":
    st.title("💈 Shop Owner Dashboard")
    
    owner_shop_name = st.sidebar.selectbox("Active Shop Account:", [s["name"] for s in st.session_state.shops])
    owner_shop = next(s for s in st.session_state.shops if s["name"] == owner_shop_name)

    # Split-Screen Layout
    col_chair, col_queue = st.columns([2, 1])

    with col_chair:
        st.subheader("💺 Active Chair Focus")
        
        if len(owner_shop["queue"]) > 0:
            current_cust = owner_shop["queue"][0]
            st.info(f"### Currently Serving: **{current_cust}**")
            
            st.write("---")
            b_col1, b_col2, b_col3 = st.columns(3)
            
            # ENGINE LOGIC: Complete current customer and call next
            if b_col1.button("🟢 Completed / Next", use_container_width=True):
                finished = owner_shop["queue"].pop(0)
                st.toast(f"Completed service for {finished}!")
                st.rerun()

            if b_col2.button("🟡 Customer Not Reached", use_container_width=True):
                st.warning(f"{current_cust} put on 5-minute hold alert.")

            if b_col3.button("🔴 Closing Soon Today", use_container_width=True):
                st.error("Queue locked for new joins!")
        else:
            st.success("🎉 All clear! No customers currently waiting in line.")

    with col_queue:
        st.subheader("📋 Waiting Queue")
        
        if len(owner_shop["queue"]) > 1:
            for idx, person in enumerate(owner_shop["queue"][1:], start=1):
                est_time = idx * owner_shop["avg_time_per_cut"]
                st.write(f"**{idx}. {person}** — *~{est_time} mins*")
        elif len(owner_shop["queue"]) == 1:
            st.write("Next customer is currently in the chair!")
        else:
            st.write("Queue is empty.")

        st.divider()
        if st.button("📢 Broadcast Message to Queue", use_container_width=True):
            st.toast("Alert sent to all waiting customers!")
