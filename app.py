import datetime
import math
import random

import pandas as pd
import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except Exception:
    def get_geolocation():
        return None

# ==========================================
# 1. PAGE SETUP & QUERY PARAMS HANDLING
# ==========================================
st.set_page_config(
    page_title="AI Civic Issue Reporting System",
    page_icon="🏛️",
    layout="wide",
)

query_params = st.query_params
url_ticket_id = query_params.get("ticket_id", None)
if url_ticket_id:
    try:
        url_ticket_id = int(url_ticket_id)
    except ValueError:
        url_ticket_id = None

# Initialize global shared state database
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {
            "ID": 1001,
            "Citizen": "Dev D.",
            "Issue": "Pothole",
            "Department": "Public Works Department (PWD)",
            "Severity": 4,
            "Lat": 21.1458,
            "Lon": 79.0882,
            "Upvotes": 2,
            "Status": "Reported",
            "Time": "2026-08-11 14:30:00",
        },
        {
            "ID": 1002,
            "Citizen": "Ananya S.",
            "Issue": "Water Leakage",
            "Department": "Water Supply Board",
            "Severity": 2,
            "Lat": 21.1490,
            "Lon": 79.0895,
            "Upvotes": 1,
            "Status": "In Progress",
            "Time": "2026-08-11 15:10:00",
        },
    ]


# ==========================================
# 2. HELPER UTILITIES
# ==========================================
def auto_route_department(issue_type):
    mapping = {
        "Pothole": "Public Works Department (PWD)",
        "Garbage Overflow": "Sanitation & Waste Management",
        "Broken Streetlight": "Electrical & Energy Dept",
        "Water Leakage": "Water Supply Board",
    }
    return mapping.get(issue_type, "General Administration")


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def check_duplicates(issue_type, lat, lon):
    for ticket in st.session_state.tickets:
        if ticket["Issue"] == issue_type and ticket["Status"] != "Resolved":
            if calculate_distance(lat, lon, ticket["Lat"], ticket["Lon"]) <= 30:
                return ticket
    return None


# ==========================================
# 3. SIDEBAR NAVIGATION & ROLE SELECTOR
# ==========================================
st.sidebar.title("🏛️ Civic App Navigation")

default_role_index = 0
if url_ticket_id:
    default_role_index = 1

user_role = st.sidebar.radio(
    "Select Your Role / Portal:",
    [
        "📱 Citizen Portal (Report Issue)",
        "🛠️ Field Staff Portal (Repair Team)",
        "📊 Admin Portal (Municipal Dashboard)",
    ],
    index=default_role_index,
)

st.sidebar.divider()
st.sidebar.caption("System Status: 🟢 AI Microservices Active")


# ==========================================
# ROLE 1: CITIZEN PORTAL
# ==========================================
if user_role == "📱 Citizen Portal (Report Issue)":
    st.header("📱 Citizen Issue Reporting Portal")
    st.write(
        "Report civic infrastructure issues in your area. AI will automatically analyze and route your report!"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. File a New Report")
        citizen_name = st.text_input("Your Name", value="Dev D.")
        issue_type = st.selectbox(
            "Select Issue Type (AI Vision Simulation)",
            [
                "Pothole",
                "Garbage Overflow",
                "Broken Streetlight",
                "Water Leakage",
            ],
        )
        uploaded_file = st.file_uploader(
            "Upload Image (Camera/Gallery)", type=["jpg", "jpeg", "png"]
        )

        st.markdown("#### 📍 GPS Location Detection")

        loc = get_geolocation()
        default_lat = 21.1458
        default_lon = 79.0882

        if loc and "coords" in loc:
            default_lat = float(loc["coords"]["latitude"])
            default_lon = float(loc["coords"]["longitude"])
            st.success("🎯 Device GPS location auto-detected!")
        else:
            st.info("💡 Allow browser location access or manually adjust coordinates below.")

        lat = st.number_input("Latitude", value=default_lat, format="%.6f")
        lon = st.number_input("Longitude", value=default_lon, format="%.6f")

        if st.button("Submit Report to City", type="primary"):
            dup = check_duplicates(issue_type, lat, lon)
            if dup:
                dup["Upvotes"] += 1
                st.warning(
                    f"⚠️ A similar report already exists within 30m! Upvoted existing Ticket #{dup['ID']} (Total Upvotes: {dup['Upvotes']})."
                )
            else:
                dept = auto_route_department(issue_type)
                severity = random.randint(2, 5)
                new_id = max(ticket["ID"] for ticket in st.session_state.tickets) + 1

                st.session_state.tickets.append(
                    {
                        "ID": new_id,
                        "Citizen": citizen_name,
                        "Issue": issue_type,
                        "Department": dept,
                        "Severity": severity,
                        "Lat": lat,
                        "Lon": lon,
                        "Upvotes": 1,
                        "Status": "Reported",
                        "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                st.success(f"🎉 Ticket #{new_id} Created! Automatically routed to [{dept}].")

    with col2:
        st.subheader("2. Track Existing Neighborhood Issues")
        df = pd.DataFrame(st.session_state.tickets)
        st.dataframe(
            df[["ID", "Issue", "Department", "Upvotes", "Status"]],
            use_container_width=True,
        )

        st.subheader("📍 City Issue Map")
        st.map(
            df[["Lat", "Lon"]].rename(
                columns={"Lat": "latitude", "Lon": "longitude"}
            ),
            zoom=12,
        )


# ==========================================
# ROLE 2: FIELD REPAIR STAFF PORTAL
# ==========================================
elif user_role == "🛠️ Field Staff Portal (Repair Team)":
    st.header("🛠️ Municipal Field Crew Portal")
    st.write("Update issue resolution status and submit post-repair inspection proofs.")

    if len(st.session_state.tickets) == 0:
        st.info("No active tickets found.")
    else:
        ticket_ids = [t["ID"] for t in st.session_state.tickets]

        default_index = 0
        if url_ticket_id in ticket_ids:
            default_index = ticket_ids.index(url_ticket_id)
            st.info(f"🔗 Opened directly via Ticket Link #{url_ticket_id}")

        selected_id = st.selectbox(
            "Select Ticket ID to Work On:", ticket_ids, index=default_index
        )

        ticket = next(t for t in st.session_state.tickets if t["ID"] == selected_id)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Issue Type", ticket["Issue"])
            st.metric("Assigned Dept", ticket["Department"])
            st.metric("Current Status", ticket["Status"])

        with col2:
            st.metric("Severity Score", f"{ticket['Severity']}/5")
            st.metric("Community Upvotes", ticket["Upvotes"])
            st.write(f"**GPS Coordinates:** {ticket['Lat']}, {ticket['Lon']}")

        st.markdown("#### 🔗 Shareable Direct Ticket Link")
        shareable_link = f"https://share.streamlit.io/?ticket_id={ticket['ID']}"
        st.code(shareable_link, language="text")

        st.divider()
        st.subheader("Update Resolution Status")
        new_status = st.selectbox(
            "Change Status:", ["Reported", "In Progress", "Resolved"]
        )
        proof_photo = st.file_uploader("Upload Completion Proof Photo")

        if st.button("Update Ticket Status", type="primary"):
            ticket["Status"] = new_status
            st.success(
                f"✅ Ticket #{ticket['ID']} updated successfully to status: '{new_status}'!"
            )


# ==========================================
# ROLE 3: MUNICIPAL ADMIN PORTAL
# ==========================================
elif user_role == "📊 Admin Portal (Municipal Dashboard)":
    st.header("📊 City Administration & Executive Analytics")

    df = pd.DataFrame(st.session_state.tickets)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Complaints", len(df))
    col2.metric("Pending Triage", len(df[df["Status"] == "Reported"]))
    col3.metric("Under Repair", len(df[df["Status"] == "In Progress"]))
    col4.metric("Resolved", len(df[df["Status"] == "Resolved"]))

    st.divider()

    st.subheader("Departmental Ticket Overview")
    st.dataframe(df, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tickets by Issue Type")
        st.bar_chart(df["Issue"].value_counts())

    with col_b:
        st.subheader("Status Breakdown")
        st.bar_chart(df["Status"].value_counts())
