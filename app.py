import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="My Barber", page_icon="💈", layout="wide")

# --- 1. INITIALIZE SESSION STATE DATA ---
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

if "app_language" not in st.session_state:
    st.session_state.app_language = "English"

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Light"

if "owner_logged_in" not in st.session_state:
    st.session_state.owner_logged_in = False

if "logged_owner_mobile" not in st.session_state:
    st.session_state.logged_owner_mobile = None

if "registered_owners" not in st.session_state:
    # Keyed by mobile number to enforce 1 mobile = 1 shop rule
    st.session_state.registered_owners = {
        "9876543210": {
            "owner_name": "Ramesh Kumar",
            "gender": "Male",
            "age": 34,
            "mobile": "9876543210",
            "shop_name": "Royal Cut Salon",
            "shop_name_hi": "रॉयल कट सलून",
            "payment": ["Offline", "Online"],
            "address": "Main Market, Clock Tower, Ujjain",
            "lat": 23.1765,
            "lon": 75.7885,
            "shop_id": 1
        }
    }

if "shops" not in st.session_state:
    st.session_state.shops = [
        {
            "id": 1,
            "name": "Royal Cut Salon",
            "name_hi": "रॉयल कट सलून",
            "lat": 23.1765,
            "lon": 75.7885,
            "address": "Main Market, Clock Tower, Ujjain",
            "address_hi": "मुख्य बाजार, क्लॉक टावर, उज्जैन",
            "distance": "1.2 km",
            "outside_photo": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400",
            "avg_time_per_cut": 20,
            "queue": ["Amit (Token #18)", "Vikas (Token #19)"]
        },
        {
            "id": 2,
            "name": "Classic Barber Hub",
            "name_hi": "क्लासिक बारबर हब",
            "lat": 23.1810,
            "lon": 75.7920,
            "address": "Station Road, Opposite Bank, Ujjain",
            "address_hi": "स्टेशन रोड, बैंक के सामने, उज्जैन",
            "distance": "2.5 km",
            "outside_photo": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=400",
            "inside_photo": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=400",
            "avg_time_per_cut": 25,
            "queue": ["Deepak (Token #11)", "Sanjay (Token #12)", "Pooja (Token #13)", "Rohan (Token #14)", "Karan (Token #15)", "Manoj (Token #16)"]
        }
    ]

# --- 2. LANGUAGE DICTIONARY HELPERS ---
is_hi = st.session_state.app_language == "Hindi"

T = {
    "title": "💈 My Barber" if not is_hi else "💈 माय बारबर",
    "subtitle": "Live Wait Times • Instant Virtual Queue" if not is_hi else "लाइव प्रतीक्षा समय • त्वरित वर्चुअल कतार",
    "menu_title": "💈 Navigation / मेनू",
    "nav_options": [
        "Home" if not is_hi else "होम (Home)",
        "About" if not is_hi else "प्रोफ़ाइल (About)",
        "My Appointments" if not is_hi else "मेरी अपॉइंटमेंट (My Appointments)",
        "Join as Shop Owner" if not is_hi else "दुकान मालिक के रूप में जुड़ें",
        "Settings" if not is_hi else "सेटिंग्स (Settings)"
    ]
}

# --- HEADER ---
st.markdown(f"<h2 style='text-align: center; margin-bottom: 0px;'>{T['title']}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 13px; color: gray;'>{T['subtitle']}</p>", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
st.sidebar.title(T["menu_title"])
selected_menu = st.sidebar.radio("Go to:", T["nav_options"])

def get_badge_color(count, is_user_booked=False):
    if is_user_booked:
        return "#1E88E5" # Blue
    if count <= 5:
        return "#2E7D32" # Green
    elif count <= 10:
        return "#F57C00" # Yellow/Orange
    else:
        return "#D32F2F" # Red

# ==========================================
# 1. HOME VIEW (CUSTOMER MAIN MAP)
# ==========================================
if "Home" in selected_menu or "होम" in selected_menu:
    loc = get_geolocation()
    user_lat, user_lon = 23.1765, 75.7885
    if loc and "coords" in loc:
        user_lat = loc["coords"]["latitude"]
        user_lon = loc["coords"]["longitude"]

    m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
    
    # User Location Marker
    folium.Marker(
        [user_lat, user_lon], 
        tooltip="आप यहाँ हैं" if is_hi else "You are here",
        icon=folium.Icon(color="cadetblue", icon="user", prefix="fa")
    ).add_to(m)

    # Render Shop Pins with Clean Dynamic Static Badges
    for shop in st.session_state.shops:
        count = len(shop["queue"])
        has_user = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == shop["id"]
        color_code = get_badge_color(count, is_user_booked=has_user)
        
        s_name = shop["name_hi"] if is_hi else shop["name"]
        label_text = f"{s_name} | Q: {count}"
        if has_user:
            label_text = f"🔵 {s_name} | {st.session_state.user_booking['token_label']}"

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
        
        folium.Marker(
            [shop["lat"], shop["lon"]],
            icon=folium.DivIcon(html=icon_html, icon_size=(120, 36), icon_anchor=(60, 18))
        ).add_to(m)

    map_data = st_folium(m, width=1000, height=380)

    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        
        for s in st.session_state.shops:
            if abs(s["lat"] - clicked_lat) < 0.005 and abs(s["lon"] - clicked_lon) < 0.005:
                st.session_state.selected_shop_id = s["id"]

    # --- SHOP DETAILS PANEL ---
    if st.session_state.selected_shop_id:
        selected_shop = next((s for s in st.session_state.shops if s["id"] == st.session_state.selected_shop_id), None)
        
        if selected_shop:
            st.divider()
            head_col1, head_col2 = st.columns([8, 1])
            s_title = selected_shop['name_hi'] if is_hi else selected_shop['name']
            s_addr = selected_shop['address_hi'] if is_hi else selected_shop['address']

            with head_col1:
                st.subheader(f"💈 {s_title}")
            with head_col2:
                if st.button("✖️ " + ("बंद करें" if is_hi else "Close"), key="close_shop_details"):
                    st.session_state.selected_shop_id = None
                    st.rerun()

            st.write(f"📍 **{'दूरी' if is_hi else 'Distance'}:** {selected_shop['distance']} | {s_addr}")

            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(selected_shop["outside_photo"], caption="बाहर का दृश्य" if is_hi else "Outside View", use_container_width=True)
            with img_col2:
                st.image(selected_shop["inside_photo"], caption="अंदर का दृश्य" if is_hi else "Inside View", use_container_width=True)

            q_count = len(selected_shop["queue"])
            est_wait = q_count * selected_shop["avg_time_per_cut"]
            has_booking_here = st.session_state.user_booking and st.session_state.user_booking["shop_id"] == selected_shop["id"]

            if has_booking_here:
                st.info(f"🔵 **{'आपकी बुक की गई सीट' if is_hi else 'YOUR BOOKED SEAT(S)'}:** {st.session_state.user_booking['token_label']}")
            else:
                st.write(f"👥 **{'वर्तमान कतार' if is_hi else 'Current Queue'}:** `{q_count} {'लोग प्रतीक्षा में' if is_hi else 'waiting'}` | ⏱️ **{'अनुमानित समय' if is_hi else 'Approx. Wait'}:** `{est_wait} {'मिनट' if is_hi else 'mins'}`")
                
                if st.button("➕ " + ("कतार में शामिल हों" if is_hi else "Join Virtual Queue"), type="primary"):
                    st.session_state[f"show_confirm_{selected_shop['id']}"] = True

                if st.session_state.get(f"show_confirm_{selected_shop['id']}", False):
                    with st.form(f"confirm_booking_form_{selected_shop['id']}"):
                        st.markdown("### 📋 " + ("बुकिंग की पुष्टि करें" if is_hi else "Confirm Queue Entry"))
                        st.write(f"👤 **{'नाम' if is_hi else 'Name'}:** {st.session_state.user_profile['name']}")
                        st.write(f"💈 **{'दुकान' if is_hi else 'Shop Name'}:** {s_title}")
                        
                        add_group = st.checkbox("परिवार या दोस्तों को जोड़ें (+ अतिरिक्त सीटें)" if is_hi else "Add family or friends (+ extra seats)")
                        num_people = 1
                        if add_group:
                            num_people = st.number_input("व्यक्तियों की संख्या (आपके सहित):" if is_hi else "Number of persons (including you):", min_value=2, max_value=6, value=2, step=1)
                        
                        start_token = len(selected_shop["queue"]) + 20
                        if num_people == 1:
                            token_label = f"Token #{start_token}"
                        else:
                            end_token = start_token + num_people - 1
                            token_label = f"Tokens #{start_token} to #{end_token}"
                            
                        st.write(f"🔢 **{'आवंटित टोकन संख्या' if is_hi else 'Exact Assigned Queue Number'}:** `{token_label}`")
                        reach_time = st.number_input("दुकान तक पहुँचने का समय (मिनट में):" if is_hi else "Enter your travel time to reach shop (in minutes):", min_value=5, max_value=60, value=None, placeholder="e.g. 15")

                        if st.form_submit_button("पुष्टि करें और सीट बुक करें" if is_hi else "Confirm & Book Seat"):
                            if reach_time is None:
                                st.error("कृपया पुष्टि करने से पहले अपना यात्रा समय दर्ज करें।" if is_hi else "Please fill in your estimated travel time before confirming.")
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
                                    "distance": selected_shop["distance"],
                                    "lat": selected_shop["lat"],
                                    "lon": selected_shop["lon"]
                                }
                                st.session_state[f"show_confirm_{selected_shop['id']}"] = False
                                st.success(f"सीट बुक हो गई! reserved: {token_label}" if is_hi else f"Seat(s) Booked Successfully! Reserved: {token_label}")
                                st.rerun()

# ==========================================
# 2. ABOUT (CUSTOMER PROFILE VIEW)
# ==========================================
elif "About" in selected_menu or "प्रोफ़ाइल" in selected_menu:
    st.title("👤 " + ("उपयोगकर्ता प्रोफ़ाइल (About)" if is_hi else "Customer Profile (About)"))
    st.write("अपने विवरण देखें और अपडेट करें:" if is_hi else "View and manage your personal details:")

    p = st.session_state.user_profile

    if not st.session_state.profile_edit_mode:
        st.info(f"👤 **{'नाम (Name)' if is_hi else 'Name'}:** {p['name']}")
        st.write(f"🎂 **{'आयु (Age)' if is_hi else 'Age'}:** {p['age'] if p['age'] else 'Not set'}")
        st.write(f"📱 **{'मोबाइल नंबर (Mobile)' if is_hi else 'Mobile Number'}:** {p['mobile'] if p['mobile'] else 'Not set'}")
        st.write(f"📧 **{'ईमेल (Email)' if is_hi else 'Email Address'}:** {p['email'] if p['email'] else 'Not set'}")
        st.write(f"🏠 **{'घर का पता (Home Address)' if is_hi else 'Home Address'}:** {p['address'] if p['address'] else 'Not set'}")
        
        st.divider()
        if st.button("✏️ " + ("विवरण संपादित करें" if is_hi else "Edit Details")):
            st.session_state.profile_edit_mode = True
            st.rerun()
    else:
        with st.form("edit_profile_form"):
            st.subheader("✏️ " + ("विवरण अपडेट करें" if is_hi else "Update Details"))
            new_name = st.text_input("नाम (Name)*", value=p["name"])
            new_age = st.text_input("आयु (Age)", value=p["age"])
            new_mobile = st.text_input("मोबाइल नंबर (Mobile Number)", value=p["mobile"])
            new_email = st.text_input("ईमेल (Email Address)", value=p["email"])
            new_address = st.text_area("घर का पता (Home Address)", value=p["address"])

            if st.form_submit_button("💾 " + ("विवरण सहेजें" if is_hi else "Save Details")):
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
                    st.success("विवरण सफलतापूर्वक सहेजे गए!" if is_hi else "Details saved successfully!")
                    st.rerun()
                else:
                    st.error("नाम अनिवार्य है।" if is_hi else "Name is required.")

# ==========================================
# 3. MY APPOINTMENTS VIEW
# ==========================================
elif "My Appointments" in selected_menu or "मेरी अपॉइंटमेंट" in selected_menu:
    st.title("📋 " + ("मेरी अपॉइंटमेंट" if is_hi else "My Active Appointments"))
    
    if st.session_state.user_booking:
        b = st.session_state.user_booking
        
        st.info(f"### 💈 {b['shop_name']}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"🔵 **{'टोकन नंबर' if is_hi else 'Your Queue Token'}:** <h2 style='color: #1E88E5; display: inline;'>{b['token_label']}</h2>", unsafe_allow_html=True)
            st.write(f"👥 **{'कुल सीटें' if is_hi else 'Total Reserved'}:** {b['num_people']}")
            st.write(f"📍 **{'पता' if is_hi else 'Address'}:** {b['address']}")
            st.write(f"⏱️ **{'यात्रा का समय' if is_hi else 'Your Travel Time'}:** {b['travel_time']} mins")
            st.write(f"📏 **{'दूरी' if is_hi else 'Distance'}:** {b['distance']}")
        
        with col_b:
            st.subheader("🧭 " + ("लाइव नेविगेशन" if is_hi else "In-App Live Route"))
            route_map = folium.Map(location=[b['lat'], b['lon']], zoom_start=14)
            folium.Marker([23.1765, 75.7885], popup="Your Location", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(route_map)
            folium.Marker([b['lat'], b['lon']], popup=b['shop_name'], icon=folium.Icon(color="red", icon="cut", prefix="fa")).add_to(route_map)
            folium.PolyLine([(23.1765, 75.7885), (b['lat'], b['lon'])], color="#1E88E5", weight=4, opacity=0.8).add_to(route_map)
            st_folium(route_map, width=450, height=220)

        st.divider()
        st.subheader("❌ " + ("अपॉइंटमेंट रद्द करें" if is_hi else "Cancel Appointment"))
        with st.expander("रद्द करें (Cancel)"):
            cancel_reason_app = st.text_input("रद्द करने का कारण:" if is_hi else "Reason for cancellation:", key="cancel_app_input")
            if st.button("पुष्टि करें और रद्द करें" if is_hi else "Confirm & Cancel Appointment", type="primary"):
                if cancel_reason_app.strip():
                    target_shop = next((s for s in st.session_state.shops if s["id"] == b["shop_id"]), None)
                    if target_shop:
                        target_shop["queue"] = [q for q in target_shop["queue"] if st.session_state.user_profile["name"] not in q]
                    st.session_state.user_booking = None
                    st.success("अपॉइंटमेंट सफलतापूर्वक रद्द कर दी गई।" if is_hi else "Appointment cancelled successfully.")
                    st.rerun()
                else:
                    st.warning("कृपया रद्द करने का कारण दर्ज करें।" if is_hi else "Please provide a reason before cancelling.")
    else:
        st.warning("आपकी कोई सक्रिय अपॉइंटमेंट नहीं है।" if is_hi else "You do not have any active appointment booked right now.")

# ==========================================
# 4. JOIN AS SHOP OWNER VIEW
# ==========================================
elif "Shop Owner" in selected_menu or "दुकान मालिक" in selected_menu:
    st.title("✂️ " + ("दुकान मालिक पोर्टल" if is_hi else "Barber Shop Owner Portal"))

    if not st.session_state.owner_logged_in:
        tab_login, tab_register = st.tabs(["🔐 Login (लॉग इन)", "📝 Register as New (नया पंजीकरण)"])

        # LOGIN TAB (MOBILE OTP)
        with tab_login:
            st.subheader("🔑 Login with Mobile OTP")
            login_mobile = st.text_input("Mobile Number (पंजीकृत मोबाइल नंबर):", key="login_mob")
            
            if st.button("Send OTP"):
                if login_mobile in st.session_state.registered_owners:
                    st.session_state["otp_sent_login"] = True
                    st.success("OTP sent to your registered mobile: 1234 (Demo)")
                else:
                    st.error("Mobile number not registered! Please register as a new shop first.")

            if st.session_state.get("otp_sent_login", False):
                entered_otp = st.text_input("Enter 4-Digit OTP:", key="login_otp", type="password")
                if st.button("Verify & Login"):
                    if entered_otp == "1234":
                        st.session_state.owner_logged_in = True
                        st.session_state.logged_owner_mobile = login_mobile
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid OTP!")

        # REGISTER TAB (1 MOBILE = 1 SHOP RULE)
        with tab_register:
            st.subheader("📝 Register New Shop (1 Mobile Number = 1 Shop)")
            st.caption("All fields marked with * are compulsory.")

            with st.form("register_shop_form"):
                o_name = st.text_input("Owner Name (मालिक का नाम)*", value=st.session_state.user_profile["name"])
                o_gender = st.selectbox("Gender (लिंग)*", ["Male", "Female", "Other"])
                o_age = st.number_input("Age (आयु)*", min_value=18, max_value=80, value=30)
                
                o_mobile = st.text_input("Mobile Number (OTP Verification Required)*")
                s_name = st.text_input("Shop Name (दुकान का नाम)*")
                
                st.write("Payment Options Accepted (भुगतान के तरीके)*:")
                p_offline = st.checkbox("Offline Cash", value=True)
                p_online = st.checkbox("Online UPI/Card", value=True)
                
                s_address = st.text_area("Shop Address (दुकान का पूरा पता)*")
                s_outside = st.text_input("Outside Photo URL*", value="https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400")
                s_inside = st.text_input("Inside Photo URL*", value="https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400")
                
                st.write("Locate via Map (GPS Coordinates)*:")
                s_lat = st.number_input("Latitude", value=23.1780, format="%.4f")
                s_lon = st.number_input("Longitude", value=75.7890, format="%.4f")

                submit_reg = st.form_submit_button("Save & Register Shop")

                if submit_reg:
                    if not o_mobile.strip() or not s_name.strip() or not s_address.strip():
                        st.error("Please fill all compulsory star-marked fields!")
                    elif o_mobile in st.session_state.registered_owners:
                        st.error("This Mobile Number is already registered with another shop! (1 Mobile = 1 Shop Rule)")
                    else:
                        # Register New Shop
                        new_id = len(st.session_state.shops) + 1
                        payments = []
                        if p_offline: payments.append("Offline")
                        if p_online: payments.append("Online")

                        st.session_state.registered_owners[o_mobile] = {
                            "owner_name": o_name,
                            "gender": o_gender,
                            "age": o_age,
                            "mobile": o_mobile,
                            "shop_name": s_name,
                            "shop_name_hi": s_name,
                            "payment": payments,
                            "address": s_address,
                            "lat": s_lat,
                            "lon": s_lon,
                            "shop_id": new_id
                        }

                        st.session_state.shops.append({
                            "id": new_id,
                            "name": s_name,
                            "name_hi": s_name,
                            "lat": s_lat,
                            "lon": s_lon,
                            "address": s_address,
                            "address_hi": s_address,
                            "distance": "1.0 km",
                            "outside_photo": s_outside,
                            "inside_photo": s_inside,
                            "avg_time_per_cut": 20,
                            "queue": []
                        })

                        st.session_state.owner_logged_in = True
                        st.session_state.logged_owner_mobile = o_mobile
                        st.success("Shop Registered Successfully!")
                        st.rerun()

    else:
        # LOGGED-IN SHOP OWNER DASHBOARD
        owner_data = st.session_state.registered_owners.get(st.session_state.logged_owner_mobile)
        owner_shop = next(s for s in st.session_state.shops if s["id"] == owner_data["shop_id"])

        st.success(f"Logged in as Owner of **{owner_shop['name']}** ({owner_data['mobile']})")

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
elif "Settings" in selected_menu or "सेटिंग्स" in selected_menu:
    st.title("⚙️ " + ("सेटिंग्स (Settings)" if is_hi else "App Settings"))

    # Language Toggle
    st.subheader("🌐 Language / भाषा")
    lang_choice = st.radio("Select Language:", ["English", "Hindi (हिंदी)"], index=0 if st.session_state.app_language == "English" else 1)
    if lang_choice != ("English" if st.session_state.app_language == "English" else "Hindi (हिंदी)"):
        st.session_state.app_language = "English" if "English" in lang_choice else "Hindi"
        st.rerun()

    st.divider()

    # Theme Toggle
    st.subheader("🎨 Theme / थीम")
    theme_choice = st.radio("Select Theme:", ["Normal (Light)", "Dark"], index=0 if st.session_state.app_theme == "Light" else 1)
    if "Dark" in theme_choice and st.session_state.app_theme != "Dark":
        st.session_state.app_theme = "Dark"
        st.info("Dark theme style preference updated.")
    elif "Normal" in theme_choice and st.session_state.app_theme != "Light":
        st.session_state.app_theme = "Light"
        st.info("Light theme style preference updated.")

    st.divider()

    # Logout Option for Shop Owners
    st.subheader("🚪 Account / लॉग आउट")
    if st.session_state.owner_logged_in:
        st.write("You are currently logged in as a Shop Owner.")
        if st.button("Log Out as Shop Owner", type="primary"):
            st.session_state.owner_logged_in = False
            st.session_state.logged_owner_mobile = None
            st.success("Logged out successfully. Returned to Customer Mode.")
            st.rerun()
    else:
        st.write("Currently active as Customer (No login required for customers).")
