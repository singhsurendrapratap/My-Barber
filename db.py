"""
db.py — Supabase persistence layer for My Barber.

Every function here talks to Supabase so that shop, owner and queue data
survives app restarts/redeploys instead of living only in st.session_state.

Requires two Streamlit secrets (Settings -> Secrets on Streamlit Cloud,
or a local .streamlit/secrets.toml):

    SUPABASE_URL = "https://xxxxx.supabase.co"
    SUPABASE_KEY = "your-anon-public-key"

Both are found in Supabase: Project -> Settings -> API.
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ---------------------------------------------------------------------
# SHOPS + OWNERS
# ---------------------------------------------------------------------

def load_shops_and_owners():
    """Fetch shops, attach their live queue, and return (shops_list, owners_by_mobile)."""
    sb = get_client()

    shops_resp = sb.table("shops").select("*").order("id").execute()
    owners_resp = sb.table("registered_owners").select("*").execute()
    queue_resp = (
        sb.table("queue_entries")
        .select("*")
        .eq("status", "waiting")
        .order("token_number")
        .execute()
    )

    shops = shops_resp.data or []
    owners_rows = owners_resp.data or []
    queue_rows = queue_resp.data or []

    # group waiting queue entries by shop_id, formatted like the old string labels
    queue_by_shop = {}
    for entry in queue_rows:
        label = f"{entry['customer_name']} (Token #{entry['token_number']})"
        queue_by_shop.setdefault(entry["shop_id"], []).append(
            {"id": entry["id"], "label": label, "token_number": entry["token_number"],
             "customer_name": entry["customer_name"]}
        )

    for shop in shops:
        shop["queue"] = queue_by_shop.get(shop["id"], [])

    owners = {row["mobile"]: {**row, "shop_id": row["shop_id"]} for row in owners_rows}
    # attach shop_name for convenience (owners table no longer duplicates shop fields)
    shops_by_id = {s["id"]: s for s in shops}
    for mobile, row in owners.items():
        shop = shops_by_id.get(row["shop_id"])
        if shop:
            row["shop_name"] = shop["name"]
            row["mobile"] = mobile

    return shops, owners


def register_shop(owner_name, gender, age, mobile, shop_name, lat, lon, address,
                   outside_photo_url, inside_photo_url, avg_time_per_cut=20):
    sb = get_client()
    shop_insert = sb.table("shops").insert({
        "owner_mobile": mobile,
        "name": shop_name,
        "name_hi": shop_name,
        "lat": lat,
        "lon": lon,
        "address": address,
        "address_hi": address,
        "outside_photo": outside_photo_url,
        "inside_photo": inside_photo_url,
        "avg_time_per_cut": avg_time_per_cut,
    }).execute()
    new_shop = shop_insert.data[0]

    sb.table("registered_owners").insert({
        "mobile": mobile,
        "owner_name": owner_name,
        "gender": gender,
        "age": age,
        "shop_id": new_shop["id"],
    }).execute()

    return new_shop


# ---------------------------------------------------------------------
# QUEUE
# ---------------------------------------------------------------------

def next_token_number(shop_id, current_queue_len):
    # Matches your original scheme: starts at len(queue) + 20
    return current_queue_len + 20


def join_queue(shop_id, customer_name, start_token, num_people):
    sb = get_client()
    rows = []
    for i in range(num_people):
        token = start_token + i
        name = f"{customer_name} (Person {i + 1})" if num_people > 1 else customer_name
        rows.append({"shop_id": shop_id, "customer_name": name, "token_number": token})
    sb.table("queue_entries").insert(rows).execute()


def cancel_customer_booking(shop_id, customer_name):
    sb = get_client()
    sb.table("queue_entries").update({"status": "cancelled"}).eq(
        "shop_id", shop_id
    ).like("customer_name", f"{customer_name}%").eq("status", "waiting").execute()


def complete_first_in_queue(entry_id):
    sb = get_client()
    sb.table("queue_entries").update({"status": "done"}).eq("id", entry_id).execute()
