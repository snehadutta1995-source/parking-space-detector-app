"""
SLotX — User Portal (Updated)
Smart Parking Booking and Management for Customers
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import qrcode
import urllib.parse
import io
import base64

from pathlib import Path


from utils.database import (
    get_all_slots, get_rates, create_booking, get_user_bookings, cancel_booking,
    get_user, update_user_profile, get_user_notifications,
    add_to_waitlist, get_user_waitlist_position, get_waitlist,
    get_entry_exit_logs, get_overstay_alerts,
    send_notification, mark_notification_read,
)
from utils.styles import apply_theme, badge_html, rate_card_html, animated_slot_card_html, TIME_SLOTS

if not hasattr(st, "experimental_dialog") and hasattr(st, "dialog"):
    st.experimental_dialog = st.dialog


# ─────────────────────────────────────────────
# Footer Overlay Dialogs
# ─────────────────────────────────────────────
@st.experimental_dialog("🏠 Home", width="large")
def _footer_home_dialog():
    st.markdown("""
    ### Welcome to SLotX

    **Smart Parking Management System**

    SLotX is a next-generation parking slot management solution designed to make parking
    convenient, efficient, and hassle-free.

    #### Key Features
    - 🗺️ **Real-time Availability** - See available slots instantly
    - 📅 **Pre-Booking** - Reserve your slot in advance
    - 💳 **Secure Payments** - Multiple payment options available
    - 📊 **Smart Analytics** - Track your parking history
    - 🎫 **QR Entry/Exit** - Seamless gate entry with QR codes

    #### How It Works
    1. **Browse** available parking slots in real-time
    2. **Book** your preferred slot and time
    3. **Pay** securely through our payment gateway
    4. **Generate QR** for gate entry
    5. **Park** without hassle!

    Start booking your parking slot today!
    """)


@st.experimental_dialog("ℹ️ About Us", width="large")
def _footer_about_dialog():
    st.markdown("""
    ### About SLotX

    SLotX is revolutionizing urban parking management through intelligent technology and
    user-centric design.

    #### Our Mission
    To simplify parking and reduce parking-related stress through smart solutions.

    #### Our Vision
    A world where parking is no longer a hassle, but a seamless experience integrated
    into urban mobility.

    #### Why Choose SLotX?
    - **Innovative Technology** - Built with cutting-edge parking management algorithms
    - **User-Friendly** - Intuitive interface designed for everyone
    - **Reliable** - 99.9% uptime and secure transactions
    - **Eco-Friendly** - Reduce time spent searching for parking, lower emissions
    - **24/7 Support** - Always here to help

    #### Our Team
    A dedicated team of parking experts, engineers, and designers working to
    transform the parking experience.
    """)


@st.experimental_dialog("📧 Contact Us", width="large")
def _footer_contact_dialog():
    st.markdown("""
    ### Get in Touch

    Have questions or feedback? We'd love to hear from you!

    #### Contact Information
    - **Email:** support@slotx.com
    - **Phone:** +91 1800-SLOTX-11
    - **Website:** www.slotx.com
    - **Office:** Smart Parking Solutions Pvt. Ltd., Tech Park, Bangalore, India

    #### Business Hours
    - Monday - Friday: 9:00 AM - 6:00 PM IST
    - Saturday: 10:00 AM - 4:00 PM IST
    - Sunday: Closed

    #### Quick Support
    For urgent issues, reach out to our support team at support@slotx.com
    """)


@st.experimental_dialog("🔒 Privacy & Security", width="large")
def _footer_privacy_dialog():
    st.markdown("""
    ### Privacy & Security

    Your data is important to us. We follow industry-leading standards to protect
    your information.

    #### Data Protection
    - All personal data is encrypted with AES-256 encryption
    - Payment information is PCI-DSS compliant
    - We never share your data with third parties without consent

    #### Privacy Policy
    We collect only essential information needed to provide parking services.
    Your data is stored securely and used only for service improvement.

    #### Cookie Policy
    We use cookies to enhance your experience. You can manage cookie preferences
    in your browser settings.

    #### Your Rights
    - Right to access your data
    - Right to correct your information
    - Right to delete your account
    - Right to data portability
    """)


@st.experimental_dialog("📋 Terms of Service", width="large")
def _footer_terms_dialog():
    st.markdown("""
    ### Terms of Service

    By using SLotX, you agree to these terms and conditions.

    #### Usage Terms
    - Users must be 18+ years old to use this service
    - One user account per person
    - Bookings must be used by the registered user
    - Abusive behavior will result in account suspension

    #### Payment Terms
    - All payments are non-refundable except in case of system errors
    - Booking cancellations must be done before the booking time
    - Late cancellations may incur charges

    #### Liability
    SLotX provides the platform as-is. We are not liable for technical failures
    beyond our control.

    #### Changes to Terms
    We may update these terms anytime. Continued use means acceptance of changes.
    """)


def _render_footer(user):
    """Render the footer section with navigation and info links."""
    st.markdown("---")
    st.markdown("""
    <div style='padding: 20px 0; color: #9aa0b4; font-size: 13px;'>
    """, unsafe_allow_html=True)

    # Footer Navigation
    footer_cols = st.columns([1, 1, 1, 1, 1])

    with footer_cols[0]:
        if st.button("🏠 Home", use_container_width=True):
            _footer_home_dialog()

    with footer_cols[1]:
        if st.button("ℹ️ About Us", use_container_width=True):
            _footer_about_dialog()

    with footer_cols[2]:
        if st.button("📧 Contact", use_container_width=True):
            _footer_contact_dialog()

    with footer_cols[3]:
        if st.button("🔒 Privacy", use_container_width=True):
            _footer_privacy_dialog()

    with footer_cols[4]:
        if st.button("📋 Terms", use_container_width=True):
            _footer_terms_dialog()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; padding-top: 10px; color: #6b7280; font-size: 11px;'>© 2026 SLotX — Smart Parking Solutions. All rights reserved.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
def render_user():
    st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)

    BASE_DIR = Path(__file__).resolve().parents[1]
    LOGO_PATH = BASE_DIR / "slotx_logo.jpeg"

    # Hide sidebar and expand content to full width (user portal only)
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    .sidebar { display: none !important; width: 0 !important; }
    [data-testid="stMainBlockContainer"],
    .main { width: 100% !important; max-width: 100% !important; }
    .stAppViewContainer { max-width: 100% !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    [data-testid="stContainer"] { width: 100% !important; }
    .element-container { width: 100% !important; }

    /* Left Panel Styling */
    .left-panel {
        position: fixed;
        left: 0;
        top: 0;
        width: 100px;
        height: 100vh;
        background: linear-gradient(180deg, #0b0c0f 0%, #111318 50%, #0b0c0f 100%);
        border-right: 1px solid #2a2f3d;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 20px 0;
        gap: 30px;
        z-index: 999;
    }
    .left-panel-logo {
        width: 75px;
        height: 75px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(79, 124, 255, 0.3);
        flex-shrink: 0;
    }
    .left-panel-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

    # Left panel with logo and dark mode toggle (fixed position)
    dark_mode = st.session_state.dark
    dark_label = f"{'🌙' if dark_mode else '☀️'}"

    st.markdown(f"""
    <div class="left-panel">
        <div class="left-panel-logo">
            <img src="file:///{LOGO_PATH}" alt="SLotX" style="width: 100%; height: 100%; object-fit: cover; border-radius: 12px;">
        </div>
        <button id="dark-mode-btn" style="position: fixed; left: 20px; top: 130px; width: 60px; height: 60px; background: linear-gradient(135deg, #4f7cff, #22c55e); border-radius: 50%; border: none; cursor: pointer; font-size: 24px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); z-index: 999; transition: transform 0.2s ease;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
            {dark_label}
        </button>
    </div>
    """, unsafe_allow_html=True)

    # Display logo using Streamlit (for actual rendering)
    if LOGO_PATH.exists():
        st.markdown(f"""
        <div style="position: absolute; top: -9999px; left: -9999px; width: 75px; height: 75px;">
        """, unsafe_allow_html=True)
        st.image(str(LOGO_PATH), width=75)
        st.markdown("</div>", unsafe_allow_html=True)

    # Dark mode toggle button (invisible, positioned off-screen)
    st.markdown('<div style="position: absolute; top: -9999px; left: -9999px;">', unsafe_allow_html=True)
    if st.button(dark_label, key="left_dark_toggle"):
        st.session_state.dark = not st.session_state.dark
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    user = st.session_state.user

    # ── Top Bar: Navigation Buttons + Sign Out ────
    top_bar_cols = st.columns([5.4, 1.1])

    # Left: Navigation Buttons
    with top_bar_cols[0]:
        nav_buttons = st.columns(5, gap="small")
        nav_items = [
            ("🗺️ Availability", "availability"),
            ("📅 Pre-Book", "prebook"),
            ("📋 My Bookings", "bookings"),
            ("💰 Rates", "rates"),
            ("👤 Profile", "profile"),
        ]

        # Initialize current page in session state
        if "user_current_page" not in st.session_state:
            st.session_state.user_current_page = "availability"

        for col, (label, page_key) in zip(nav_buttons, nav_items):
            with col:
                if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.user_current_page = page_key
                    st.rerun()

        # Determine which page to show
        page = st.session_state.user_current_page

    # Right: Sign Out Button
    with top_bar_cols[1]:
        if st.button("➡️ Sign Out", use_container_width=True, key="logout_user"):
            for k in [
                "logged_in",
                "user",
                "role",
                "user_current_page",
                "pay_booking_ref",
                "pay_otp_stage",
                "pay_expected_otp",
                "pay_card_meta",
            ]:
                if k == "logged_in":
                    st.session_state[k] = False
                else:
                    st.session_state.pop(k, None)
            st.rerun()

    st.divider()

    # ── Payment interface (when a booking is awaiting payment) ──
    if st.session_state.get("pay_booking_ref"):
        from payment_page import render_payment
        render_payment()
        return

    # ── Page routing ─────────────────────────
    if   page == "availability": _availability()
    elif page == "prebook": _pre_book()
    elif page == "bookings": _my_bookings()
    elif page == "rates": _rates_view()
    elif page == "profile": _profile_page()

    # ── Footer (shown on all pages) ──────────
    _render_footer(user)


# ─────────────────────────────────────────────
# SLOT AVAILABILITY WITH ANIMATED GRID
# ─────────────────────────────────────────────
def _availability():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>🗺️</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Parking Availability</h1>
        <div style='font-size:13px;color:#9aa0b4'>Real-time slot status and live updates</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    slots = get_all_slots()
    vac   = sum(1 for s in slots if s["status"] == "vacant")
    occ   = len(slots) - vac

    c1, c2, c3 = st.columns(3)
    c1.metric("Available",   vac,        delta=f"{int(vac/len(slots)*100)}% free" if slots else "—")
    c2.metric("Occupied",    occ,        delta_color="inverse")
    c3.metric("Total Slots", len(slots))

    st.divider()

    # Filter
    st.markdown("**Filter Slots**")
    fc1, fc2, fc3 = st.columns(3)
    ftype   = fc1.selectbox("Filter by type",   ["All", "4-wheeler", "2-wheeler"], key="avail_type")
    ffloor  = fc2.selectbox("Filter by floor",  ["All", "G", "1", "2"], key="avail_floor")
    fstatus = fc3.selectbox("Filter by status", ["All", "Vacant", "Occupied"], key="avail_status")

    filtered = slots
    if ftype  != "All":    filtered = [s for s in filtered if s["type"]   == ftype]
    if ffloor != "All":    filtered = [s for s in filtered if s["floor"]  == ffloor]
    if fstatus == "Vacant":   filtered = [s for s in filtered if s["status"] == "vacant"]
    if fstatus == "Occupied": filtered = [s for s in filtered if s["status"] == "occupied"]

    st.divider()
    st.markdown(
        "<div style='display:flex;gap:16px;font-size:12px;color:#9aa0b4;margin-bottom:12px'>"
        "<span>🟢 <b>Vacant (Free)</b></span>"
        "<span>🔴 <b>Occupied (Taken)</b></span></div>",
        unsafe_allow_html=True,
    )

    for floor in ["G", "1", "2"]:
        fslots = [s for s in filtered if s["floor"] == floor]
        if not fslots:
            continue
        vf = sum(1 for s in fslots if s["status"] == "vacant")
        st.markdown(f"**Floor {floor}** — {vf}/{len(fslots)} free")
        cols = st.columns(8)
        for i, slot in enumerate(fslots):
            with cols[i % 8]:
                st.markdown(
                    animated_slot_card_html(slot, clickable=True, index=i),
                    unsafe_allow_html=True,
                )
        st.markdown("")


# ─────────────────────────────────────────────
# PRE-BOOKING WITH DATE PICKER
# ─────────────────────────────────────────────
def _pre_book():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>📅</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Pre-Book a Slot</h1>
        <div style='font-size:13px;color:#9aa0b4'>Reserve your parking in advance</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rates = get_rates()
    slots = get_all_slots()

    st.markdown("### 🗺️ Choose Parking Location")
    parking_data = {
        "West Bengal": {
            "Kolkata": {
                "New Market Parking": (22.5581, 88.3508),
                "Park Street Parking": (22.5535, 88.3525),
                "Howrah Station Parking": (22.5839, 88.3426),
                "Salt Lake Sector V Parking": (22.5769, 88.4335),
                "Science City Parking": (22.5410, 88.3960),
            },
            "Siliguri": {"City Centre Parking": (26.7271, 88.3953)},
        },
        "Maharashtra": {"Mumbai": {"Bandra Parking": (19.0607, 72.8362), "Andheri Parking": (19.1197, 72.8464)}},
        "Delhi": {"New Delhi": {"Connaught Place Parking": (28.6315, 77.2167)}},
        "Karnataka": {"Bengaluru": {"MG Road Parking": (12.9756, 77.6068)}},
    }
    c1, c2, c3 = st.columns(3)
    state = c1.selectbox("Choose State", list(parking_data.keys()))
    city = c2.selectbox("Choose City", list(parking_data[state].keys()))
    area = c3.selectbox("Choose Parking Area", list(parking_data[state][city].keys()))
    lat, lon = parking_data[state][city][area]
    try:
        import folium
        from streamlit_folium import st_folium
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="OpenStreetMap")
        for name, (a_lat, a_lon) in parking_data[state][city].items():
            folium.Marker([a_lat, a_lon], popup=name, tooltip=name, icon=folium.Icon(color="green" if name == area else "blue", icon="car", prefix="fa")).add_to(m)
        st_folium(m, width=900, height=380)
    except Exception:
        st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))
    directions_url = "https://www.google.com/maps/dir/?api=1&destination=" + urllib.parse.quote(f"{lat},{lon}")
    st.markdown(f"**Selected:** {area}, {city}, {state}  ")
    st.markdown(f"[Get Directions]({directions_url})")


    tab_book, tab_waitlist = st.tabs(["📅 Book Now", "⏳ Join Waitlist"])

    with tab_book:
        col_form, col_summary = st.columns([1.1, 0.9])

        with col_form:
            st.markdown("#### Booking Details")

            with st.container():
                vehicle_no = st.text_input("Vehicle Number", placeholder="MH12AB1234").upper()
                vtype      = st.selectbox("Vehicle Type", ["4-wheeler", "2-wheeler"])
                booking_date = st.date_input("Booking Date", value=datetime.now().date(), 
                                           min_value=datetime.now().date())
                from_t   = st.time_input("From Time", value=time(9, 0))
                duration = st.selectbox("Duration", [1, 2, 3, 4, 6, 8], index=1,
                                       format_func=lambda h: f"{h} hour{'s' if h>1 else ''}")

                vac_slots = [s for s in slots if s["status"] == "vacant" and s["type"] == vtype]
                if not vac_slots:
                    st.warning(f"❌ No vacant {vtype} slots available.")
                    st.button("Book Now", disabled=True)
                    return

                slot_opts  = {f"{s['slot_code']} — Floor {s['floor']}": s for s in vac_slots}
                slot_label = st.selectbox("Select Slot", list(slot_opts.keys()))
                sel_slot   = slot_opts[slot_label]

                from_dt = datetime.combine(datetime.today(), from_t)
                from_minutes = from_dt.hour * 60 + from_dt.minute
                to_minutes   = from_minutes + duration * 60
                to_h, to_m   = divmod(to_minutes % (24*60), 60)
                to_t         = time(to_h, to_m)

                rate   = rates.get(vtype, 30 if vtype == "4-wheeler" else 10)
                amount = rate * duration

                submitted = st.button("✅ Book Now", use_container_width=True)

        with col_summary:
            st.markdown("#### Fare Summary")
            rate_now = rates.get(vtype if 'vtype' in dir() else "4-wheeler", 30)
            dur_now  = duration if 'duration' in dir() else 2
            amt_now  = rate_now * dur_now
            sl_now   = sel_slot["slot_code"] if 'sel_slot' in dir() else "—"
            date_str = booking_date.strftime("%d %b %Y") if 'booking_date' in dir() else "—"

            st.markdown(f"""
            <div style='background:#111318;border:1px solid #2a2f3d;border-radius:12px;padding:1.5rem'>
              <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2f3d'>
                <span style='color:#9aa0b4;font-size:13px'>Date</span>
                <span style='font-weight:500'>{date_str}</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2f3d'>
                <span style='color:#9aa0b4;font-size:13px'>Vehicle</span>
                <span style='font-weight:500'>{vtype if 'vtype' in dir() else '—'}</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2f3d'>
                <span style='color:#9aa0b4;font-size:13px'>Rate</span>
                <span style='color:#f59e0b;font-weight:500'>₹{rate_now}/hr</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2f3d'>
                <span style='color:#9aa0b4;font-size:13px'>Duration</span>
                <span style='font-weight:500'>{dur_now} hr(s)</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2f3d'>
                <span style='color:#9aa0b4;font-size:13px'>Slot</span>
                <span style='font-family:DM Mono,monospace;color:#4f7cff;font-weight:600'>{sl_now}</span>
              </div>
              <div style='display:flex;justify-content:space-between;align-items:center;padding-top:14px'>
                <span style='font-family:Syne,sans-serif;font-weight:700;font-size:15px'>Total</span>
                <span style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:#f59e0b'>₹{amt_now}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if submitted:
            if not vehicle_no:
                st.error("Please enter your vehicle number.")
            elif not sel_slot:
                st.error("Please select a slot.")
            else:
                # Create booking with 'pending' status (not active yet)
                ref = create_booking(
                    user_id    = st.session_state.user["id"],
                    slot_id    = sel_slot["id"],
                    vehicle_no = vehicle_no,
                    from_time  = str(from_t)[:5],
                    to_time    = str(to_t)[:5],
                    from_date  = str(booking_date),
                    duration_hr= duration,
                    amount     = amount,
                )
                
                # Booking created (pending) — go straight to the payment interface.
                st.session_state["pay_booking_ref"] = ref
                st.rerun()

    # ── Waitlist tab ───────────────────────────
    with tab_waitlist:
        st.markdown("#### Join Waitlist")
        st.markdown("Can't find a slot? Join the waitlist!")

        with st.form("waitlist_form"):
            w_vtype = st.selectbox("Vehicle Type", ["4-wheeler", "2-wheeler"], key="wait_type")
            w_date = st.date_input("Preferred Date", value=datetime.now().date(), key="wait_date")
            w_duration = st.selectbox("Duration", [1, 2, 3, 4, 6, 8], index=1, key="wait_dur")
            
            if st.form_submit_button("📝 Join Waitlist"):
                pos = add_to_waitlist(
                    st.session_state.user["id"],
                    w_vtype,
                    str(w_date),
                    duration_hr=w_duration
                )
                st.success(f"✅ You're #{pos} in the waitlist!")
                st.rerun()


# ─────────────────────────────────────────────
# MY BOOKINGS
# ─────────────────────────────────────────────
def _my_bookings():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>📋</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>My Bookings</h1>
        <div style='font-size:13px;color:#9aa0b4'>Your parking reservations</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bookings = get_user_bookings(st.session_state.user["id"])

    if not bookings:
        st.info("No bookings yet. Start by booking a slot!")
        if st.button("Book a Slot →"):
            st.rerun()
        return

    # Filter bookings by status
    tab_active, tab_pending, tab_completed, tab_cancelled = st.tabs(
        ["🟢 Active", "⏳ Pending Payment", "✅ Completed", "❌ Cancelled"]
    )
    
    with tab_active:
        active_bookings = [b for b in bookings if b["status"] == "active"]
        if not active_bookings:
            st.info("No active bookings")
        else:
            _display_bookings_grid(active_bookings)

    with tab_pending:
        pending_bookings = [b for b in bookings if b["status"] == "pending"]
        if not pending_bookings:
            st.info("No pending bookings")
        else:
            _display_pending_bookings(pending_bookings)
    
    with tab_completed:
        completed_bookings = [b for b in bookings if b["status"] == "completed"]
        if not completed_bookings:
            st.info("No completed bookings")
        else:
            _display_bookings_list(completed_bookings)
    
    with tab_cancelled:
        cancelled_bookings = [b for b in bookings if b["status"] == "cancelled"]
        if not cancelled_bookings:
            st.info("No cancelled bookings")
        else:
            _display_bookings_list(cancelled_bookings)


def _qr_buffer(b, box_size: int = 8):
    """Build a PNG buffer of the booking QR code."""
    qr_data = f"SLOTX|{b['booking_ref']}|{b['vehicle_no']}|{b['slot_code']}"
    qr = qrcode.QRCode(version=1, box_size=box_size)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    qr_img.save(buf, "PNG")
    buf.seek(0)
    return buf


@st.experimental_dialog("📱 Booking QR Code")
def _qr_dialog(b):
    """Large QR overlay. The dialog provides a built-in dismiss (✕) icon."""
    st.markdown(
        f"<div style='text-align:center;font-family:Syne,sans-serif;font-weight:700;"
        f"font-size:18px;margin-bottom:4px'>{b['booking_ref']}</div>"
        f"<div style='text-align:center;color:#9aa0b4;font-size:13px;margin-bottom:12px'>"
        f"Slot {b['slot_code']} · {b['vehicle_no']}</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(_qr_buffer(b, box_size=16), use_column_width=True)
    st.caption("Scan this code at the gate to check in / out.")


def _render_active_qr(b, key_prefix: str):
    """Render the QR image as the clickable target (button is invisible but positioned over it)."""
    uid = f"{key_prefix}_{b['id']}"

    # Render the QR image directly and visibly.
    st.image(_qr_buffer(b), width=150, use_column_width=False)

    # CSS to make the button invisible but still clickable, positioned over the image.
    st.markdown(
        f"<style>"
        f"/* Target the button that comes right after the image (sibling selector) */"
        f"[data-testid='stImage'] + [data-testid='stButton'] button {{"
        f"  opacity: 0 !important;"
        f"  cursor: pointer;"
        f"  margin-top: -155px !important;"
        f"  width: 150px !important;"
        f"  height: 150px !important;"
        f"  padding: 0 !important;"
        f"  border: none !important;"
        f"}}"
        f"</style>",
        unsafe_allow_html=True,
    )

    # Invisible button that's clickable (positioned over the image via CSS).
    if st.button("", key=f"qrbtn_{uid}"):
        _qr_dialog(b)


def _display_bookings_list(bookings):
    """Display list of bookings."""
    active = [b for b in bookings if b["status"] == "active"]
    spent = sum(b["amount"] for b in bookings if b["status"] != "cancelled")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total", len(bookings))
    m2.metric("Active", len(active))
    m3.metric("Total Amount", f"₹{spent:.0f}")

    st.divider()

    for b in bookings:
        status_icon = "🟢" if b["status"] == "active" else ("✅" if b["status"] == "completed" else "❌")
        with st.expander(f"{status_icon} {b['booking_ref']} — `{b['slot_code']}` · ₹{b['amount']:.0f}", expanded=b["status"] == "active"):
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                st.markdown(f"""
                - **Slot:** {b['slot_code']} (Floor {b['floor']})
                - **Vehicle:** {b['vehicle_no']}
                - **Date:** {b['from_date']}
                - **Time:** {b['from_time']} – {b['to_time']}
                - **Duration:** {b['duration_hr']} hour(s)
                - **Amount:** ₹{b['amount']:.0f}
                """)
            
            with col2:
                if b["status"] == "active":
                    _render_active_qr(b, key_prefix="list")


def _display_bookings_grid(bookings, cols_per_row: int = 3):
    """Display active bookings as a grid of cards."""
    spent = sum(b["amount"] for b in bookings)

    m1, m2 = st.columns(2)
    m1.metric("Active Bookings", len(bookings))
    m2.metric("Total Amount", f"₹{spent:.0f}")

    st.divider()

    for i in range(0, len(bookings), cols_per_row):
        row = bookings[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, b in zip(cols, row):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='font-family:Syne,sans-serif;font-weight:700;font-size:15px'>"
                        f"🟢 {b['booking_ref']}</div>"
                        f"<div style='color:#9aa0b4;font-size:12px;margin-bottom:8px'>"
                        f"Slot {b['slot_code']} · Floor {b['floor']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"""
                    - **Vehicle:** {b['vehicle_no']}
                    - **Date:** {b['from_date']}
                    - **Time:** {b['from_time']} – {b['to_time']}
                    - **Duration:** {b['duration_hr']} hour(s)
                    - **Amount:** ₹{b['amount']:.0f}
                    """)

                    if st.button("📱 Click to Generate QR", key=f"qr_btn_{b['id']}", use_container_width=True):
                        _qr_dialog(b)


def _display_pending_bookings(bookings):
    """Display pending bookings with payment option."""
    st.warning("⚠️ These bookings require payment to be activated.")
    st.divider()
    
    for b in bookings:
        with st.expander(f"⏳ {b['booking_ref']} — `{b['slot_code']}` · ₹{b['amount']:.0f}"):
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                st.markdown(f"""
                - **Slot:** {b['slot_code']} (Floor {b['floor']})
                - **Vehicle:** {b['vehicle_no']}
                - **Date:** {b['from_date']}
                - **Time:** {b['from_time']} – {b['to_time']}
                - **Duration:** {b['duration_hr']} hour(s)
                - **Amount:** ₹{b['amount']:.0f}
                """)
                
                col_pay, col_cancel = st.columns(2)
                with col_pay:
                    if st.button(f"💳 Pay Now", key=f"pay_{b['id']}"):
                        st.session_state["pay_booking_ref"] = b["booking_ref"]
                        st.rerun()
                
                with col_cancel:
                    if st.button(f"❌ Cancel", key=f"cancel_{b['id']}"):
                        cancel_booking(b['id'])
                        st.success("Booking cancelled!")
                        st.rerun()


# ─────────────────────────────────────────────
# RATES VIEW
# ─────────────────────────────────────────────
def _rates_view():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>💰</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Parking Rates</h1>
        <div style='font-size:13px;color:#9aa0b4'>Pricing and fare information</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rates = get_rates()
    st.markdown(rate_card_html(rates), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# USER PROFILE PAGE
# ─────────────────────────────────────────────
def _profile_page():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>👤</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Your Profile</h1>
        <div style='font-size:13px;color:#9aa0b4'>Manage your account settings</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    user = get_user(st.session_state.user["id"])
    if not user:
        st.error("User not found.")
        return
    
    tab_profile, tab_activity = st.tabs(["👤 Profile", "📊 Activity"])
    
    with tab_profile:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Profile Picture")
            name_value = (user.get("name") or "").strip()
            initials = "".join(p[0].upper() for p in name_value.split()[:2]) if name_value else "NA"
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:50%;width:120px;height:120px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:48px;font-weight:800;color:white;font-family:Syne'>
              {initials}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Edit Profile")
            with st.form("profile_form"):
                new_name = st.text_input("Name", value=user.get("name") or "")
                new_email = st.text_input("Email", value=user.get("email") or "")
                new_phone = st.text_input("Phone", value=user.get("phone") or "", placeholder="+91-XXXXXXXXXX")
                
                if st.form_submit_button("💾 Save Changes"):
                    update_user_profile(user["id"], new_name, new_email, new_phone) # type: ignore
                    st.session_state.user["name"] = new_name
                    st.success("✅ Profile updated!")
                    st.rerun()
    
    with tab_activity:
        st.markdown("#### Your Activity")
        bookings = get_user_bookings(user["id"])
        
        if bookings:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Bookings", len(bookings))
            col2.metric("Active", len([b for b in bookings if b["status"] == "active"]))
            col3.metric("Completed", len([b for b in bookings if b["status"] == "completed"]))
            col4.metric("Total Spent", f"₹{sum(b['amount'] for b in bookings if b['status'] != 'cancelled'):.0f}")
