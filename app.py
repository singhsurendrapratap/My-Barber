import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="My Barber", page_icon="💈", layout="wide")

# --- ENGINE: INITIALIZE USER & MOCK BACKEND DATA IN SESSION STATE ---
if "user_name" not in st.session_state:
    st.session_state.user_name = "Rahul" # Default stored name after first-time prompt

if "user_booking" not in st.session_state:
    st.session_state.user_booking = None # Tracks active booking details

if "selected_shop_id" not in st.session_state:
    st.session_state.selected_shop_id = None # Tracks currently tapped shop on the map

if "shops" not in st.session_state:
    st.session_state.shops = [
        {
            "id": 1,
            "name": "Royal Cut Salon",
            "lat": 23.1765,
            "lon": 75.7885,
            "address": "Main Market, Clock Tower",
            "distance": "1.2 km",
            "outside_photo": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400",
            "avg_time_per_cut": 20,
            "queue": ["Amit (Token #18)", "Vikas (Token #19)"]
        },
        {
            "id": 2,
            "name": "Classic Barber Hub",
            "lat": 23.1810,
            "lon": 75.7920,
            "address": "Station Road, Opposite Bank",
            "distance": "2.5 km",
            "outside_photo": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=400",
            "avg_time_per_cut": 25,
            "queue": ["Deepak (Token #11)", "Sanjay (Token #12)", "Pooja (Token #13)", "Rohan (Token #14)", "Karan (Token #15)", "Manoj (Token #16)"]
        }
    ]

# --- SLIM COMPACT HEADER ---
st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>💈 My Barber</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; color: gray;'>Live Wait Times • Instant Virtual Queue</p>", unsafe_allow_html=True)

# --- TOP-LEFT NAVIGATION MENU ---
st.sidebar.title("💈 Menu")
role = st.sidebar.radio("Navigation:", ["Map View", "My Appointment", "Shop Owner View"])

# Helper function to get queue badge color
def get_queue_color(count, is_user_booked=False):
    if is_user_booked:
        return "blue"
    if count <= 5:
        return "green"
    elif count <= 10:
        return "orange"
    else:
        return "red"

# ==========================================
# 1. MAP VIEW (CUSTOMER MAIN INTERFACE)
# ==========================================
if role == "Map View":
    # Fetch User GPS Location
    loc = get_geolocation()
    user_lat, user_lon = 23.1765, 75.7885 # Default fallback location
    if loc and "coords" in loc:
        user_lat = loc["coords"]["latitude"]
        user_lon = loc["coords"]["longitude"]

    # Render Interactive Map
    m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
    
    # "You are currently here" Marker
    folium.Marker(
        [user_lat, user_lon], 
        popup="<b>You are currently here</b>", 
        tooltip="You are here",
        icon=folium.Icon(color="cadetblue", icon="user", prefix="fa")
    ).add_to(m)

    # Render Shop Pins with Dynamic Colors (Green <= 5, Orange/Yellow <= 10, Red 11+)
    for shop in st.session_state.shops:
        count = len(shop["queue"])
        has_user = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == shop["id"]
        pin_color = get_queue_color(count, is_user_booked=has_user)
        
        display_label = f"{shop['name']} | Q: {count}"
        if has_user:
            display_label = f"🔵 {shop['name']} | YOUR QUEUE: {st.session_state.user_booking['token_label']}"

        folium.Marker(
            [shop["lat"], shop["lon"]], 
            popup=display_label, 
            tooltip=display_label,
            icon=folium.Icon(color=pin_color, icon="cut", prefix="fa")
        ).add_to(m)

    map_data = st_folium(m, width=1000, height=380)

    # Check if user clicked a pin on the map
    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        
        for s in st.session_state.shops:
            if abs(s["lat"] - clicked_lat) < 0.001 and abs(s["lon"] - clicked_lon) < 0.001:
                st.session_state.selected_shop_id = s["id"]

    # --- SHOP DETAILS PANEL (TAPPED SHOP ONLY) ---
    if st.session_state.selected_shop_id:
        selected_shop = next((s for s in st.session_state.shops if s["id"] == st.session_state.selected_shop_id), None)
        
        if selected_shop:
            st.divider()
            
            # Close Button (✖️)
            head_col1, head_col2 = st.columns([8, 1])
            with head_col1:
                st.subheader(f"💈 {selected_shop['name']}")
            with head_col2:
                if st.button("✖️ Close", key="close_shop_details"):
                    st.session_state.selected_shop_id = None
                    st.rerun()

            st.write(f"📍 **Distance:** {selected_shop['distance']} away | [{selected_shop['address']}]")
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={selected_shop['lat']},{selected_shop['lon']}"
            st.markdown(f"🧭 **[Get Directions on Google Maps]({maps_url})**")

            # Photos Side by Side
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(selected_shop["outside_photo"], caption="Outside View", use_container_width=True)
            with img_col2:
                st.image(selected_shop["inside_photo"], caption="Inside View", use_container_width=True)

            q_count = len(selected_shop["queue"])
            est_wait = q_count * selected_shop["avg_time_per_cut"]
            
            has_booking_here = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == selected_shop["id"]

            if has_booking_here:
                # ACTIVE BOOKED STATE
                st.info(f"🔵 **YOUR BOOKED SEAT(S):** {st.session_state.user_booking['token_label']} | Status: Waiting in Line")
                
                with st.expander("❌ Cancel Booking"):
                    cancel_reason = st.text_input("Please enter reason for cancellation:")
                    if st.button("Confirm Cancellation", type="primary"):
                        if cancel_reason.strip():
                            # Remove booked entries from shop queue
                            selected_shop["queue"] = [q for q in selected_shop["queue"] if st.session_state.user_name not in q]
                            st.session_state.user_booking = None
                            st.success("Booking cancelled successfully.")
                            st.rerun()
                        else:
                            st.warning("Please specify a reason before cancelling.")
            else:
                st.write(f"👥 **Current Queue:** `{q_count} waiting` | ⏱️ **Approx. Wait:** `{est_wait} mins`")
                
                # JOIN QUEUE BUTTON
                if st.button("➕ Join Virtual Queue", type="primary"):
                    st.session_state[f"show_confirm_{selected_shop['id']}"] = True

                # CONFIRMATION MODAL / BOX
                if st.session_state.get(f"show_confirm_{selected_shop['id']}", False):
                    with st.form(f"confirm_booking_form_{selected_shop['id']}"):
                        st.markdown("### 📋 Confirm Queue Entry")
                        st.write(f"👤 **Name:** {st.session_state.user_name} *(Auto-filled)*")
                        st.write(f"💈 **Shop Name:** {selected_shop['name']}")
                        st.write(f"📏 **Distance:** {selected_shop['distance']}")
                        
                        # Checkbox to add family/friends
                        add_group = st.checkbox("Add family or friends (+ extra seats)")
                        
                        num_people = 1
                        if add_group:
                            # Dynamic input when checkbox is ticked
                            num_people = st.number_input("Number of persons (including you):", min_value=2, max_value=6, value=2, step=1)
                        
                        # Calculate exact assigned queue token numbers
                        start_token = len(selected_shop["queue"]) + 20
                        if num_people == 1:
                            token_label = f"Token #{start_token}"
                        else:
                            end_token = start_token + num_people - 1
                            token_label = f"Tokens #{start_token} to #{end_token}"
                            
                        st.write(f"🔢 **Exact Assigned Queue Number:** `{token_label}`")
                        
                        # Travel/Reaching Time (NOT pre-filled; requires user input)
                        reach_time = st.number_input("Enter your travel time to reach shop (in minutes):", min_value=5, max_value=60, value=None, placeholder="e.g. 15")

                        if st.form_submit_button("Confirm & Book Seat"):
                            if reach_time is None:
                                st.error("Please fill in your estimated travel time before confirming.")
                            else:
                                # Append booked seats to shop queue engine
                                for i in range(num_people):
                                    t_num = start_token + i
                                    label = f"{st.session_state.user_name} (Person {i+1}) (Token #{t_num})" if num_people > 1 else f"{st.session_state.user_name} (Token #{t_num})"
                                    selected_shop["queue"].append(label)
                                
                                # Save details in user session
                                st.session_state.user_booking = {
                                    "shop_id": selected_shop["id"],
                                    "shop_name": selected_shop["name"],
                                    "token_label": token_label,
                                    "num_people": num_people,
                                    "travel_time": reach_time,
                                    "address": selected_shop["address"],
                                    "lat": selected_shop["lat"],
                                    "lon": selected_shop["lon"]
                                }
                                st.session_state[f"show_confirm_{selected_shop['id']}"] = False
                                st.success(f"Seat(s) Booked Successfully! Reserved: {token_label}")
                                st.rerun()

# ==========================================
# 2. MY APPOINTMENT TAB
# ==========================================
elif role == "My Appointment":
    st.title("📋 My Active Appointment")
    
    if st.session_state.user_booking:
        b = st.session_state.user_booking
        st.info(f"### 💈 {b['shop_name']}")
        st.markdown(f"🔵 **Your Booked Queue Number:** <h2 style='color: #1E88E5; display: inline;'>{b['token_label']}</h2>", unsafe_allow_html=True)
        st.write(f"👥 **Total Persons Reserved:** {b['num_people']}")
        st.write(f"📍 **Address:** {b['address']}")
        st.write(f"⏱️ **Your Filled Travel Time:** {b['travel_time']} mins")

        maps_url = f"https://www.google.com/maps/dir/?api=1&destination={b['lat']},{b['lon']}"
        st.markdown(f"🧭 **[Click Here for Google Maps Navigation Helper]({maps_url})**")
        
        st.divider()
        if st.button("Go to Map to Manage/Cancel"):
            st.session_state.selected_shop_id = b["shop_id"]
            st.rerun()
    else:
        st.warning("You do not have any active appointment booked right now.")
        st.write("Go to the **Map View** to select a shop and join the virtual line.")

# ==========================================
# 3. SHOP OWNER VIEW (SPLIT DASHBOARD)
# ==========================================
elif role == "Shop Owner View":
    st.title("✂️ Barber Owner Dashboard")
    
    owner_shop_name = st.sidebar.selectbox("Active Shop Account:", [s["name"] for s in st.session_state.shops])
    owner_shop = next(s for s in st.session_state.shops if s["name"] == owner_shop_name)

    col_chair, col_queue = st.columns([2, 1])

    with col_chair:
        st.subheader("💺 Active Chair Focus")
        
        if len(owner_shop["queue"]) > 0:
            current_cust = owner_shop["queue"][0]
            st.info(f"### Currently Serving: **{current_cust}**")
            
            st.write("---")
            b_col1, b_col2, b_col3 = st.columns(3)
            
            if b_col1.button("🟢 Completed / Next", use_container_width=True):
                finished = owner_shop["queue"].pop(0)
                if st.session_state.user_booking and st.session_state.user_name in finished:
                    st.session_state.user_booking = None
                st.toast(f"Completed service for {finished}!")
                st.rerun()

            if b_col2.button("🟡 Customer Not Reached", use_container_width=True):
                st.warning(f"{current_cust} placed on 5-minute hold alert.")

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
