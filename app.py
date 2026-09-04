import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt
import time
import random

st.set_page_config(page_title="My Barber", page_icon="💈", layout="wide")

# Helper function to calculate exact distance in meters
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return 999999, "Unknown"
    R = 6371000  # Earth radius in meters
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))
    dist_m = R * c
    if dist_m >= 1000:
        return dist_m, f"{dist_m / 1000:.2f} km"
    return dist_m, f"{int(dist_m)} meters"

# --- 1. INITIALIZE SESSION STATE ---
if "app_language" not in st.session_state:
    st.session_state.app_language = "English"

if "user_name" not in st.session_state:
    st.session_state.user_name = "Rahul"

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Rahul",
        "age": "",
        "mobile": "",
        "email": "",
        "address": ""
    }

if "profile_edit_mode" not in st.session_state:
    st.session_state.profile_edit_mode = False

if "user_booking" not in st.session_state:
    st.session_state.user_booking = None

if "selected_shop_id" not in st.session_state:
    st.session_state.selected_shop_id = None

# Registration State Variables
if "reg_mobile_verified" not in st.session_state:
    st.session_state.reg_mobile_verified = False

if "reg_verified_mobile_num" not in st.session_state:
    st.session_state.reg_verified_mobile_num = ""

if "otp_sent_time" not in st.session_state:
    st.session_state.otp_sent_time = 0

if "otp_generated_code" not in st.session_state:
    st.session_state.otp_generated_code = None

if "login_otp_code" not in st.session_state:
    st.session_state.login_otp_code = None

if "show_unverified_error" not in st.session_state:
    st.session_state.show_unverified_error = False

# Location Pin State
if "reg_shop_pin_lat" not in st.session_state:
    st.session_state.reg_shop_pin_lat = None

if "reg_shop_pin_lon" not in st.session_state:
    st.session_state.reg_shop_pin_lon = None

if "reg_location_saved" not in st.session_state:
    st.session_state.reg_location_saved = False

# Registration Photo States
if "reg_outside_photo_img" not in st.session_state:
    st.session_state.reg_outside_photo_img = None

if "reg_inside_photo_img" not in st.session_state:
    st.session_state.reg_inside_photo_img = None

if "owner_logged_in" not in st.session_state:
    st.session_state.owner_logged_in = False

if "logged_owner_mobile" not in st.session_state:
    st.session_state.logged_owner_mobile = None

if "registered_owners" not in st.session_state:
    st.session_state.registered_owners = {
        "9876543210": {
            "owner_name": "Ramesh Kumar",
            "gender": "Male",
            "age": 34,
            "mobile": "9876543210",
            "shop_name": "Royal Cut Salon",
            "shop_name_hi": "रॉयल कट सलून",
            "payment": ["Offline Cash", "Online UPI/Card"],
            "address": "Main Market, Clock Tower, Ujjain, Madhya Pradesh, India",
            "lat": 23.1765,
            "lon": 75.7885,
            "shop_id": 1
        }
    }

if "shops" not in st.session_state:
    st.session_state.shops = [
        {
            "id": 1,
            "owner_mobile": "9876543210",
            "name": "Royal Cut Salon",
            "name_hi": "रॉयल कट सलून",
            "lat": 23.1765,
            "lon": 75.7885,
            "address": "Main Market, Clock Tower, Ujjain, MP, India",
            "address_hi": "मुख्य बाजार, क्लॉक टावर, उज्जैन, म.प्र., भारत",
            "outside_photo": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400",
            "avg_time_per_cut": 20,
            "queue": ["Amit (Token #18)", "Vikas (Token #19)"]
        },
        {
            "id": 2,
            "owner_mobile": "9999999999",
            "name": "Classic Barber Hub",
            "name_hi": "क्लासिक बारबर हब",
            "lat": 23.1810,
            "lon": 75.7920,
            "address": "Station Road, Opposite Bank, Ujjain, MP, India",
            "address_hi": "स्टेशन रोड, बैंक के सामने, उज्जैन, म.प्र., भारत",
            "outside_photo": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=400",
            "avg_time_per_cut": 25,
            "queue": ["Deepak (Token #11)", "Sanjay (Token #12)", "Pooja (Token #13)"]
        }
    ]

# --- 2. GET CURRENT DEVICE GEOLOCATION ---
loc_data = get_geolocation()
device_lat, device_lon = 23.1780, 75.7890
if loc_data and "coords" in loc_data:
    device_lat = loc_data["coords"]["latitude"]
    device_lon = loc_data["coords"]["longitude"]

# --- 3. DYNAMICALLY EVALUATE SHOP OPEN/CLOSED STATUS (10 METERS PROXIMITY RULE) ---
for shop in st.session_state.shops:
    owner_mob = shop.get("owner_mobile")
    # Rule: Active owner app session AND owner within 10 meters of fixed registered shop location
    if st.session_state.owner_logged_in and st.session_state.logged_owner_mobile == owner_mob:
        dist_m, dist_lbl = calculate_haversine_distance(device_lat, device_lon, shop["lat"], shop["lon"])
        if dist_m <= 10.0:
            shop["is_open"] = True
            shop["status_reason"] = "Owner at shop (within 10m)"
        else:
            shop["is_open"] = False
            shop["status_reason"] = f"Owner is away ({dist_lbl} from shop)"
    else:
        shop["is_open"] = False
        shop["status_reason"] = "Owner inactive/offline"

# --- 4. LANGUAGE DICTIONARIES ---
is_hi = st.session_state.app_language == "Hindi"

if is_hi:
    T = {
        "title": "💈 माय बारबर",
        "subtitle": "लाइव प्रतीक्षा समय • त्वरित वर्चुअल कतार",
        "menu_title": "💈 मेनू",
        "nav_home": "होम",
        "nav_about": "प्रोफ़ाइल",
        "nav_appts": "मेरी अपॉइंटमेंट",
        "nav_owner": "दुकान मालिक पोर्टल",
        "nav_settings": "सेटिंग्स",
        "close": "बंद करें",
        "distance": "दूरी",
        "outside": "बाहर का दृश्य",
        "inside": "अंदर का दृश्य",
        "curr_q": "वर्तमान कतार",
        "waiting": "लोग प्रतीक्षा में",
        "est_wait": "अनुमानित समय",
        "mins": "मिनट",
        "join_q": "कतार में शामिल हों",
        "confirm_q": "बुकिंग की पुष्टि करें",
        "name": "नाम",
        "shop": "दुकान का नाम",
        "add_group": "परिवार या दोस्तों को जोड़ें (+ अतिरिक्त सीटें)",
        "num_persons": "व्यक्तियों की संख्या (आपके सहित):",
        "assigned_token": "आवंटित टोकन संख्या",
        "travel_time_prompt": "दुकान तक पहुँचने का समय (मिनट में):",
        "confirm_btn": "पुष्टि करें और सीट बुक करें",
        "cancel_btn": "अपॉइंटमेंट रद्द करें",
        "cancel_reason": "रद्द करने का कारण:"
    }
else:
    T = {
        "title": "💈 My Barber",
        "subtitle": "Live Wait Times • Instant Virtual Queue",
        "menu_title": "💈 Navigation",
        "nav_home": "Home",
        "nav_about": "About",
        "nav_appts": "My Appointments",
        "nav_owner": "Join as Shop Owner",
        "nav_settings": "Settings",
        "close": "Close",
        "distance": "Distance",
        "outside": "Outside View",
        "inside": "Inside View",
        "curr_q": "Current Queue",
        "waiting": "waiting",
        "est_wait": "Approx. Wait",
        "mins": "mins",
        "join_q": "Join Virtual Queue",
        "confirm_q": "Confirm Queue Entry",
        "name": "Name",
        "shop": "Shop Name",
        "add_group": "Add family or friends (+ extra seats)",
        "num_persons": "Number of persons (including you):",
        "assigned_token": "Exact Assigned Queue Number",
        "travel_time_prompt": "Enter your travel time to reach shop (in minutes):",
        "confirm_btn": "Confirm & Book Seat",
        "cancel_btn": "Cancel Appointment",
        "cancel_reason": "Reason for cancellation:"
    }

# --- HEADER ---
st.markdown(f"<h2 style='text-align: center; margin-bottom: 0px;'>{T['title']}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 13px; color: gray;'>{T['subtitle']}</p>", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
st.sidebar.title(T["menu_title"])
nav_selection = st.sidebar.radio("Go to:", [T["nav_home"], T["nav_about"], T["nav_appts"], T["nav_owner"], T["nav_settings"]])

def get_badge_color(count, is_open=True, is_user_booked=False):
    if not is_open:
        return "#757575" # Gray for Closed
    if is_user_booked:
        return "#1E88E5" # Blue
    if count <= 5:
        return "#2E7D32" # Green
    elif count <= 10:
        return "#F57C00" # Orange
    else:
        return "#D32F2F" # Red

# ==========================================
# 1. HOME VIEW (MAIN MAP)
# ==========================================
if nav_selection == T["nav_home"]:
    m = folium.Map(location=[device_lat, device_lon], zoom_start=15, tiles="OpenStreetMap")
    
    folium.Marker(
        [device_lat, device_lon], 
        tooltip="आप यहाँ हैं" if is_hi else "Your Device Location",
        icon=folium.Icon(color="cadetblue", icon="user", prefix="fa")
    ).add_to(m)

    for shop in st.session_state.shops:
        count = len(shop["queue"])
        has_user = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == shop["id"]
        is_shop_open = shop.get("is_open", False)
        color_code = get_badge_color(count, is_open=is_shop_open, is_user_booked=has_user)
        
        s_name = shop["name_hi"] if is_hi else shop["name"]
        
        if is_shop_open:
            label_text = f"🟢 OPEN | {s_name} | Q: {count}"
            if has_user:
                label_text = f"🔵 {s_name} | {st.session_state.user_booking['token_label']}"
        else:
            label_text = f"🔴 CLOSED | {s_name}"

        icon_html = f"""
        <div style="
            background-color: {color_code};
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            white-space: nowrap;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            border: 1px solid white;">
            ✂️ {label_text}
        </div>
        """
        
        # Lock marker to the fixed registered shop coordinates
        folium.Marker(
            [shop["lat"], shop["lon"]],
            icon=folium.DivIcon(html=icon_html, icon_size=(130, 36), icon_anchor=(65, 18))
        ).add_to(m)

    map_data = st_folium(m, width=1000, height=380)

    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        
        for s in st.session_state.shops:
            if abs(s["lat"] - clicked_lat) < 0.005 and abs(s["lon"] - clicked_lon) < 0.005:
                st.session_state.selected_shop_id = s["id"]

    if st.session_state.selected_shop_id:
        selected_shop = next((s for s in st.session_state.shops if s["id"] == st.session_state.selected_shop_id), None)
        
        if selected_shop:
            st.divider()
            head_col1, head_col2 = st.columns([8, 1])
            s_title = selected_shop['name_hi'] if is_hi else selected_shop['name']
            s_addr = selected_shop['address_hi'] if is_hi else selected_shop['address']
            is_open = selected_shop.get("is_open", False)

            with head_col1:
                status_str = "🟢 OPEN" if is_open else "🔴 CLOSED"
                st.subheader(f"💈 {s_title} ({status_str})")
            with head_col2:
                if st.button(f"✖️ {T['close']}", key="close_shop_details"):
                    st.session_state.selected_shop_id = None
                    st.rerun()

            calc_m, calc_lbl = calculate_haversine_distance(device_lat, device_lon, selected_shop["lat"], selected_shop["lon"])
            st.write(f"📍 **{T['distance']}:** {calc_lbl} | {s_addr}")

            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(selected_shop["outside_photo"], caption=T['outside'], use_container_width=True)
            with img_col2:
                st.image(selected_shop["inside_photo"], caption=T['inside'], use_container_width=True)

            q_count = len(selected_shop["queue"])
            est_wait = q_count * selected_shop["avg_time_per_cut"]
            has_booking_here = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == selected_shop["id"]

            if not is_open:
                st.error("🔒 **यह दुकान वर्तमान में बंद है।** (मालिक दुकान पर उपस्थित नहीं है या ऐप सक्रिय नहीं है)" if is_hi else "🔒 **This shop is currently CLOSED.** (Owner is not present at the shop or app is inactive)")
            else:
                if has_booking_here:
                    st.info(f"🔵 **{'आपकी टोकन संख्या' if is_hi else 'YOUR BOOKED SEAT'}:** {st.session_state.user_booking['token_label']}")
                else:
                    st.write(f"👥 **{T['curr_q']}:** `{q_count} {T['waiting']}` | ⏱️ **{T['est_wait']}:** `{est_wait} {T['mins']}`")
                    
                    if st.button(f"➕ {T['join_q']}", type="primary"):
                        st.session_state[f"show_confirm_{selected_shop['id']}"] = True

                    if st.session_state.get(f"show_confirm_{selected_shop['id']}", False):
                        with st.form(f"confirm_booking_form_{selected_shop['id']}"):
                            st.markdown(f"### 📋 {T['confirm_q']}")
                            st.write(f"👤 **{T['name']}:** {st.session_state.user_profile['name']}")
                            st.write(f"💈 **{T['shop']}:** {s_title}")
                            
                            add_group = st.checkbox(T['add_group'])
                            num_people = 1
                            if add_group:
                                num_people = st.number_input(T['num_persons'], min_value=2, max_value=6, value=2, step=1)
                            
                            start_token = len(selected_shop["queue"]) + 20
                            if num_people == 1:
                                token_label = f"Token #{start_token}"
                            else:
                                end_token = start_token + num_people - 1
                                token_label = f"Tokens #{start_token} to #{end_token}"
                                
                            st.write(f"🔢 **{T['assigned_token']}:** `{token_label}`")
                            reach_time = st.number_input(T['travel_time_prompt'], min_value=5, max_value=60, value=None, placeholder="e.g. 15")

                            if st.form_submit_button(T['confirm_btn']):
                                if reach_time is None:
                                    st.error("कृपया यात्रा समय दर्ज करें।" if is_hi else "Please enter travel time.")
                                else:
                                    for i in range(num_people):
                                        t_num = start_token + i
                                        label = f"{st.session_state.user_profile['name']} (Person {i+1}) (Token #{t_num})" if num_people > 1 else f"{st.session_state.user_profile['name']} (Token #{t_num})"
                                        selected_shop["queue"].append(label)
                                    
                                    st.session_state.user_booking = {
                                        "shop_id": selected_shop["id"],
                                        "shop_name": s_title,
                                        "token_label": token_label,
                                        "num_people": num_people,
                                        "travel_time": reach_time,
                                        "address": s_addr,
                                        "distance": calc_lbl,
                                        "lat": selected_shop["lat"],
                                        "lon": selected_shop["lon"]
                                    }
                                    st.session_state[f"show_confirm_{selected_shop['id']}"] = False
                                    st.success(f"सीट बुक हो गई: {token_label}" if is_hi else f"Seat Booked: {token_label}")
                                    st.rerun()

# ==========================================
# 2. ABOUT (PROFILE VIEW)
# ==========================================
elif nav_selection == T["nav_about"]:
    st.title("👤 " + ("उपयोगकर्ता प्रोफ़ाइल" if is_hi else "User Profile"))

    p = st.session_state.user_profile

    if not st.session_state.profile_edit_mode:
        st.info(f"👤 **{'नाम' if is_hi else 'Name'}:** {p['name']}")
        st.write(f"🎂 **{'आयु' if is_hi else 'Age'}:** {p['age'] if p['age'] else 'Not set'}")
        st.write(f"📱 **{'मोबाइल नंबर' if is_hi else 'Mobile Number'}:** {p['mobile'] if p['mobile'] else 'Not set'}")
        st.write(f"📧 **{'ईमेल' if is_hi else 'Email'}:** {p['email'] if p['email'] else 'Not set'}")
        st.write(f"🏠 **{'पता' if is_hi else 'Address'}:** {p['address'] if p['address'] else 'Not set'}")
        
        st.divider()
        if st.button("✏️ " + ("संपादित करें" if is_hi else "Edit Details")):
            st.session_state.profile_edit_mode = True
            st.rerun()
    else:
        with st.form("edit_profile_form"):
            st.subheader("✏️ " + ("विवरण अपडेट करें" if is_hi else "Update Details"))
            new_name = st.text_input("नाम / Name*", value=p["name"])
            new_age = st.text_input("आयु / Age", value=p["age"])
            new_mobile = st.text_input("मोबाइल / Mobile", value=p["mobile"])
            new_email = st.text_input("ईमेल / Email", value=p["email"])
            new_address = st.text_area("पता / Address", value=p["address"])

            if st.form_submit_button("💾 " + ("सहेजें" if is_hi else "Save Details")):
                if new_name.strip():
                    st.session_state.user_profile = {
                        "name": new_name.strip(),
                        "age": new_age.strip(),
                        "mobile": new_mobile.strip(),
                        "email": new_email.strip(),
                        "address": new_address.strip()
                    }
                    st.session_state.user_name = new_name.strip()
                    st.session_state.profile_edit_mode = False
                    st.success("विवरण सहेजे गए!" if is_hi else "Details saved!")
                    st.rerun()
                else:
                    st.error("नाम अनिवार्य है।" if is_hi else "Name is required.")

# ==========================================
# 3. MY APPOINTMENTS VIEW
# ==========================================
elif nav_selection == T["nav_appts"]:
    st.title("📋 " + ("मेरी अपॉइंटमेंट" if is_hi else "My Active Appointments"))
    
    if st.session_state.user_booking:
        b = st.session_state.user_booking
        
        st.info(f"### 💈 {b['shop_name']}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"🔵 **{'टोकन' if is_hi else 'Queue Token'}:** <h2 style='color: #1E88E5; display: inline;'>{b['token_label']}</h2>", unsafe_allow_html=True)
            st.write(f"👥 **{'सीटें' if is_hi else 'Reserved'}:** {b['num_people']}")
            st.write(f"📍 **{'पता' if is_hi else 'Address'}:** {b['address']}")
            st.write(f"⏱️ **{'समय' if is_hi else 'Travel Time'}:** {b['travel_time']} mins")
            st.write(f"📏 **{'दूरी' if is_hi else 'Distance'}:** {b['distance']}")
        
        with col_b:
            st.subheader("🧭 " + ("नेविगेशन" if is_hi else "In-App Route Map"))
            route_map = folium.Map(location=[b['lat'], b['lon']], zoom_start=15, tiles="OpenStreetMap")
            folium.Marker([device_lat, device_lon], popup="You", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(route_map)
            folium.Marker([b['lat'], b['lon']], popup=b['shop_name'], icon=folium.Icon(color="red", icon="cut", prefix="fa")).add_to(route_map)
            folium.PolyLine([(device_lat, device_lon), (b['lat'], b['lon'])], color="#1E88E5", weight=4, opacity=0.8).add_to(route_map)
            st_folium(route_map, width=450, height=220)

        st.divider()
        st.subheader(f"❌ {T['cancel_btn']}")
        with st.expander(T['cancel_btn']):
            cancel_reason_app = st.text_input(T['cancel_reason'], key="cancel_app_input")
            if st.button(T['cancel_btn'], type="primary"):
                if cancel_reason_app.strip():
                    target_shop = next((s for s in st.session_state.shops if s["id"] == b["shop_id"]), None)
                    if target_shop:
                        target_shop["queue"] = [q for q in target_shop["queue"] if st.session_state.user_profile["name"] not in q]
                    st.session_state.user_booking = None
                    st.success("अपॉइंटमेंट रद्द हो गई।" if is_hi else "Appointment cancelled.")
                    st.rerun()
                else:
                    st.warning("कारण दर्ज करें।" if is_hi else "Please provide a reason.")
    else:
        st.warning("कोई सक्रिय अपॉइंटमेंट नहीं है।" if is_hi else "No active appointment.")

# ==========================================
# 4. JOIN AS SHOP OWNER VIEW
# ==========================================
elif nav_selection == T["nav_owner"]:
    st.title("✂️ " + ("दुकान मालिक पोर्टल" if is_hi else "Barber Owner Portal"))

    if not st.session_state.owner_logged_in:
        tab_login, tab_register = st.tabs(["🔐 " + ("लॉग इन" if is_hi else "Login"), "📝 " + ("नया पंजीकरण" if is_hi else "Shop Registration")])

        # LOGIN TAB
        with tab_login:
            st.subheader("🔑 Login with Mobile OTP (Demo Mode)")
            login_mobile = st.text_input("Mobile Number:", key="login_mob")
            
            if st.button("Send Login OTP"):
                if login_mobile in st.session_state.registered_owners:
                    generated_login_otp = str(random.randint(1000, 9999))
                    st.session_state.login_otp_code = generated_login_otp
                    st.session_state["otp_sent_login"] = True
                    st.rerun()
                else:
                    st.error("Mobile number not registered! Standard registered demo mobile: 9876543210")

            if st.session_state.get("otp_sent_login", False):
                st.warning(f"🔑 **DEMO TESTING OTP:** `{st.session_state.login_otp_code}`")
                entered_otp = st.text_input("Enter Received 4-Digit OTP:", key="login_otp", type="password")
                
                col_log_v1, col_log_v2 = st.columns([1, 1])
                with col_log_v1:
                    if st.button("Verify & Login"):
                        if entered_otp == st.session_state.login_otp_code:
                            st.session_state.owner_logged_in = True
                            st.session_state.logged_owner_mobile = login_mobile
                            st.success("Login Successful!")
                            st.rerun()
                        else:
                            st.error("Invalid OTP code!")
                with col_log_v2:
                    if st.button("⚡ Auto-fill OTP & Login"):
                        st.session_state.owner_logged_in = True
                        st.session_state.logged_owner_mobile = login_mobile
                        st.success("Login Successful!")
                        st.rerun()

        # SHOP REGISTRATION
        with tab_register:
            st.subheader("📝 Shop Owner Registration Form")
            st.caption("Please fill all details. Mobile verification is required before final submission.")

            # --- MOBILE & OTP ---
            col_mob_input, col_mob_action = st.columns([2, 1])

            with col_mob_input:
                reg_mobile_num = st.text_input(
                    "Mobile Number (OTP Verification Required)*",
                    value=st.session_state.reg_verified_mobile_num,
                    disabled=st.session_state.reg_mobile_verified,
                    placeholder="Enter 10-digit mobile number"
                )

            with col_mob_action:
                st.write(" ")
                st.write(" ")
                time_now = time.time()
                time_diff = time_now - st.session_state.otp_sent_time

                if not st.session_state.reg_mobile_verified:
                    if time_diff > 60 or st.session_state.otp_sent_time == 0:
                        btn_label = "Send OTP" if st.session_state.otp_sent_time == 0 else "Resend OTP"
                        if st.button(btn_label, key="send_otp_btn"):
                            if len(reg_mobile_num.strip()) >= 10:
                                if reg_mobile_num.strip() in st.session_state.registered_owners:
                                    st.error("Mobile number already registered!")
                                else:
                                    new_rand_otp = str(random.randint(1000, 9999))
                                    st.session_state.otp_sent_time = time.time()
                                    st.session_state.otp_generated_code = new_rand_otp
                                    st.rerun()
                            else:
                                st.error("Enter valid 10-digit number.")
                    else:
                        secs_left = int(60 - time_diff)
                        st.caption(f"⏳ Resend available in **{secs_left}s**")

            if st.session_state.otp_generated_code and not st.session_state.reg_mobile_verified:
                st.warning(f"🔑 **DEMO MODE OTP CODE:** `{st.session_state.otp_generated_code}`")
                
                col_otp_in, col_otp_btn = st.columns([2, 1])
                with col_otp_in:
                    user_otp_input = st.text_input("Enter the 4-Digit OTP Code", type="password", key="inline_otp_key")
                with col_otp_btn:
                    st.write(" ")
                    st.write(" ")
                    if st.button("Verify OTP", key="verify_otp_btn"):
                        if user_otp_input == st.session_state.otp_generated_code:
                            st.session_state.reg_mobile_verified = True
                            st.session_state.reg_verified_mobile_num = reg_mobile_num.strip()
                            st.session_state.show_unverified_error = False
                            st.success("Mobile Verified Successfully! ✅")
                            st.rerun()
                        else:
                            st.error("Incorrect OTP code!")

            if st.session_state.reg_mobile_verified:
                st.success(f"✅ Verified Mobile: {st.session_state.reg_verified_mobile_num}")
            elif st.session_state.show_unverified_error:
                st.markdown("<p style='color: #D32F2F; font-weight: bold; font-size: 14px;'>🚨 Please verify your mobile number with OTP before submitting!</p>", unsafe_allow_html=True)

            st.divider()

            # REGISTRATION FORM FIELDS
            reg_owner_name = st.text_input("Owner Name*", value=st.session_state.user_profile["name"])
            reg_gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            reg_age = st.number_input("Age*", min_value=18, max_value=80, value=30)
            
            reg_shop_name = st.text_input("Shop Name (दुकान का नाम)*")
            
            st.write("Payment Options Accepted (भुगतान के तरीके)*:")
            p_off = st.checkbox("Offline Cash", value=True)
            p_on = st.checkbox("Online UPI/Card", value=True)

            st.write("📍 **Detailed Shop Address Structure (दुकान का पता)**")
            addr_col1, addr_col2 = st.columns(2)
            with addr_col1:
                addr_street = st.text_input("Street / Related Address*", placeholder="e.g. Shop No. 4, Clock Tower Road")
                addr_colony = st.text_input("Colony / Village*", placeholder="e.g. Main Market / Rampur")
                addr_city = st.text_input("City / Town*", placeholder="e.g. Ujjain")
            with addr_col2:
                addr_district = st.text_input("District*", placeholder="e.g. Ujjain District")
                addr_state = st.text_input("State*", placeholder="e.g. Madhya Pradesh")
                addr_country = st.text_input("Country*", value="India")

            # PHOTO ATTACHMENTS
            st.divider()
            st.write("📸 **Add Shop Outside Photo***")
            uploaded_out = st.file_uploader("Choose Outside Photo from Device Gallery", type=["jpg", "png", "jpeg"], key="uploader_outside_gallery")
            if uploaded_out is not None:
                st.session_state.reg_outside_photo_img = uploaded_out

            if st.session_state.reg_outside_photo_img is not None:
                st.image(st.session_state.reg_outside_photo_img, caption="Preview: Shop Outside Photo", width=300)
                if st.button("🔄 Change Outside Photo", key="reset_out_photo"):
                    st.session_state.reg_outside_photo_img = None
                    st.rerun()

            st.write("📸 **Add Shop Inside Photo***")
            uploaded_in = st.file_uploader("Choose Inside Photo from Device Gallery", type=["jpg", "png", "jpeg"], key="uploader_inside_gallery")
            if uploaded_in is not None:
                st.session_state.reg_inside_photo_img = uploaded_in

            if st.session_state.reg_inside_photo_img is not None:
                st.image(st.session_state.reg_inside_photo_img, caption="Preview: Shop Inside Photo", width=300)
                if st.button("🔄 Change Inside Photo", key="reset_in_photo"):
                    st.session_state.reg_inside_photo_img = None
                    st.rerun()

            # MAP PINPOINT FOR SHOP LOCATION
            st.divider()
            st.write("📍 **Pinpoint Exact Shop Location via Map***")

            if st.session_state.reg_shop_pin_lat is None or st.session_state.reg_shop_pin_lon is None:
                st.session_state.reg_shop_pin_lat = device_lat
                st.session_state.reg_shop_pin_lon = device_lon

            dual_map = folium.Map(
                location=[st.session_state.reg_shop_pin_lat, st.session_state.reg_shop_pin_lon],
                zoom_start=17,
                tiles="OpenStreetMap"
            )

            folium.CircleMarker(
                location=[device_lat, device_lon],
                radius=8,
                tooltip="🔴 Current Device Location",
                color="#D32F2F",
                fill=True,
                fill_color="#FF5252",
                fill_opacity=0.9
            ).add_to(dual_map)

            folium.Marker(
                [st.session_state.reg_shop_pin_lat, st.session_state.reg_shop_pin_lon],
                tooltip="🔵 Target Shop Location Pin",
                draggable=True,
                icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa")
            ).add_to(dual_map)

            folium.PolyLine(
                locations=[[device_lat, device_lon], [st.session_state.reg_shop_pin_lat, st.session_state.reg_shop_pin_lon]],
                color="#1565C0",
                weight=3,
                opacity=0.8,
                dash_array="8, 8"
            ).add_to(dual_map)

            map_event = st_folium(dual_map, width=750, height=360, key="interactive_dual_pinpoint_map")

            if map_event:
                click_lat, click_lon = None, None
                if map_event.get("last_clicked"):
                    click_lat = map_event["last_clicked"]["lat"]
                    click_lon = map_event["last_clicked"]["lng"]
                elif map_event.get("last_marker_dragged"):
                    click_lat = map_event["last_marker_dragged"]["lat"]
                    click_lon = map_event["last_marker_dragged"]["lng"]

                if click_lat is not None and click_lon is not None:
                    if abs(click_lat - st.session_state.reg_shop_pin_lat) > 0.00005 or abs(click_lon - st.session_state.reg_shop_pin_lon) > 0.00005:
                        st.session_state.reg_shop_pin_lat = click_lat
                        st.session_state.reg_shop_pin_lon = click_lon
                        st.session_state.reg_location_saved = True
                        st.rerun()

            dist_val, dist_str = calculate_haversine_distance(
                device_lat, device_lon, st.session_state.reg_shop_pin_lat, st.session_state.reg_shop_pin_lon
            )

            col_pin1, col_pin2 = st.columns([2, 1])
            with col_pin1:
                st.info(f"🔴 **Current Device:** `{device_lat:.5f}, {device_lon:.5f}`\n\n🔵 **Shop Location Pin:** `{st.session_state.reg_shop_pin_lat:.5f}, {st.session_state.reg_shop_pin_lon:.5f}`\n\n📏 **Distance:** **{dist_str}**")
            with col_pin2:
                st.write(" ")
                if st.button("📌 Confirm Shop Pin Location", key="save_pin_btn"):
                    st.session_state.reg_location_saved = True
                    st.success("Shop Location Pin Saved!")

            st.divider()

            if st.button("Save & Register Shop", type="primary"):
                full_address_str = f"{addr_street}, {addr_colony}, {addr_city}, {addr_district}, {addr_state}, {addr_country}".strip(", ")
                
                if not st.session_state.reg_mobile_verified:
                    st.session_state.show_unverified_error = True
                    st.error("Submission Failed: Mobile number is not verified.")
                    st.rerun()
                elif not reg_shop_name.strip() or not reg_owner_name.strip() or not addr_street.strip() or not addr_city.strip() or not addr_state.strip():
                    st.error("Please fill all required text and address fields marked with *")
                elif st.session_state.reg_outside_photo_img is None or st.session_state.reg_inside_photo_img is None:
                    st.error("Please select both Shop Outside and Shop Inside photos from your device gallery.")
                elif not st.session_state.reg_location_saved:
                    st.error("Please click 'Confirm Shop Pin Location' on the map before submitting.")
                else:
                    new_shop_id = len(st.session_state.shops) + 1
                    pay_methods = []
                    if p_off: pay_methods.append("Offline Cash")
                    if p_on: pay_methods.append("Online UPI/Card")

                    verified_mob = st.session_state.reg_verified_mobile_num

                    outside_url = "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400"
                    inside_url = "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400"

                    st.session_state.registered_owners[verified_mob] = {
                        "owner_name": reg_owner_name,
                        "gender": reg_gender,
                        "age": reg_age,
                        "mobile": verified_mob,
                        "shop_name": reg_shop_name,
                        "shop_name_hi": reg_shop_name,
                        "payment": pay_methods,
                        "address": full_address_str,
                        "lat": st.session_state.reg_shop_pin_lat,
                        "lon": st.session_state.reg_shop_pin_lon,
                        "shop_id": new_shop_id
                    }

                    st.session_state.shops.append({
                        "id": new_shop_id,
                        "owner_mobile": verified_mob,
                        "name": reg_shop_name,
                        "name_hi": reg_shop_name,
                        "lat": st.session_state.reg_shop_pin_lat,
                        "lon": st.session_state.reg_shop_pin_lon,
                        "address": full_address_str,
                        "address_hi": full_address_str,
                        "outside_photo": outside_url,
                        "inside_photo": inside_url,
                        "avg_time_per_cut": 20,
                        "queue": []
                    })

                    st.session_state.owner_logged_in = True
                    st.session_state.logged_owner_mobile = verified_mob
                    st.session_state.reg_mobile_verified = False
                    st.session_state.reg_location_saved = False
                    st.session_state.reg_outside_photo_img = None
                    st.session_state.reg_inside_photo_img = None
                    st.session_state.show_unverified_error = False
                    st.session_state.otp_generated_code = None
                    st.success("Shop Registered Successfully!")
                    st.rerun()

    else:
        # LOGGED-IN SHOP OWNER DASHBOARD
        owner_data = st.session_state.registered_owners.get(st.session_state.logged_owner_mobile)
        owner_shop = next(s for s in st.session_state.shops if s["id"] == owner_data["shop_id"])

        # Calculate live distance from owner's active device to their registered shop
        owner_dist_m, owner_dist_str = calculate_haversine_distance(
            device_lat, device_lon, owner_shop["lat"], owner_shop["lon"]
        )
        is_shop_open = owner_shop.get("is_open", False)

        st.success(f"Logged in as Owner of **{owner_shop['name']}** ({owner_data['mobile']})")

        # Automatic Open/Closed Status Banner
        if is_shop_open:
            st.markdown(f"### 🟢 Shop Status: **OPEN**\n*Device is **{int(owner_dist_m)} meters** from shop (Within 10m range)*")
        else:
            st.markdown(f"### 🔴 Shop Status: **CLOSED**\n*Owner device is **{owner_dist_str}** away from shop location (Requires <= 10 meters to activate Open status)*")

        st.divider()

        col_chair, col_queue = st.columns([2, 1])

        with col_chair:
            st.subheader("💺 Active Chair Focus")
            if len(owner_shop["queue"]) > 0:
                current_cust = owner_shop["queue"][0]
                st.info(f"### Currently Serving: **{current_cust}**")
                
                b_col1, b_col2, b_col3 = st.columns(3)
                if b_col1.button("🟢 Completed / Next", use_container_width=True):
                    finished = owner_shop["queue"].pop(0)
                    st.toast(f"Completed service for {finished}!")
                    st.rerun()

                if b_col2.button("🟡 Customer Not Reached", use_container_width=True):
                    st.warning(f"{current_cust} placed on 5-minute hold alert.")

                if b_col3.button("🔴 Closing Soon", use_container_width=True):
                    st.error("Queue locked for new joins!")
            else:
                st.success("🎉 All clear! No customers currently waiting in line.")

        with col_queue:
            st.subheader("📋 Waiting Queue")
            if len(owner_shop["queue"]) > 1:
                for idx, person in enumerate(owner_shop["queue"][1:], start=1):
                    est_time = idx * owner_shop["avg_time_per_cut"]
                    st.write(f"**{idx}. {person}** — *~{est_time} mins*")
            else:
                st.write("Queue is empty.")

# ==========================================
# 5. SETTINGS VIEW
# ==========================================
elif nav_selection == T["nav_settings"]:
    st.title("⚙️ " + ("सेटिंग्स" if is_hi else "App Settings"))

    st.subheader("🌐 Language / भाषा")
    lang_choice = st.radio("Select Language / भाषा चुनें:", ["English", "Hindi"], index=0 if st.session_state.app_language == "English" else 1)
    if lang_choice != st.session_state.app_language:
        st.session_state.app_language = lang_choice
        st.rerun()

    st.divider()

    st.subheader("🚪 " + ("लॉग आउट" if is_hi else "Account / Logout"))
    if st.session_state.owner_logged_in:
        st.write("आप दुकान मालिक के रूप में लॉग इन हैं।" if is_hi else "You are logged in as a Shop Owner.")
        if st.button("लॉग आउट करें" if is_hi else "Log Out as Shop Owner", type="primary"):
            st.session_state.owner_logged_in = False
            st.session_state.logged_owner_mobile = None
            st.success("लॉग आउट हो गए।" if is_hi else "Logged out successfully.")
            st.rerun()
    else:
        st.write("ग्राहक मोड सक्रिय है।" if is_hi else "Active in Customer Mode (No login required).")
