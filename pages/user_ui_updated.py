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

from pathlib import Path


from utils.database import (
    get_all_slots, get_rates, create_booking, get_user_bookings, cancel_booking,
    get_user, update_user_profile, get_user_notifications,
    add_to_waitlist, get_user_waitlist_position, get_waitlist,
    get_entry_exit_logs, get_overstay_alerts,
    send_notification, mark_notification_read,
)
from utils.styles import apply_theme, badge_html, rate_card_html, animated_slot_card_html, TIME_SLOTS


# ─────────────────────────────────────────────
def render_user():
    st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)
    user = st.session_state.user

    # ── Sidebar ───────────────────────────────
    with st.sidebar:
        # SLotX Logo & Branding
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;padding:6px 0 16px'>
          <div style='width:36px;height:36px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-family:Syne,sans-serif;font-weight:800;font-size:18px;color:#fff'>S</div>
          <div>
            <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700'>SLotX</div>
            <div style='font-size:11px;color:#9aa0b4'>User Portal</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # User Info Card
        initials = "".join(p[0].upper() for p in user["name"].split()[:2])
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;background:#1e222c;
                    border-radius:8px;padding:12px;margin-bottom:1rem;border:1px solid #2a2f3d'>
          <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-size:16px;font-weight:700;color:#fff'>{initials}</div>
          <div>
            <div style='font-size:13px;font-weight:600;color:#e8eaf0'>{user['name']}</div>
            <div style='font-size:11px;color:#9aa0b4'>Parking Member</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["🗺️ Availability", "📅 Pre-Book", "📋 My Bookings", "💰 Rates", "👤 Profile"],
            label_visibility="collapsed",
        )

        st.divider()

        # Notifications & Availability
        notifs = get_user_notifications(user["id"], limit=5)
        unread = len([n for n in notifs if n["status"] == "sent"])
        
        col_notif, col_avail = st.columns(2)
        
        with col_notif:
            st.markdown(
                f"<div style='text-align:center'><div style='font-size:11px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em'>Notifications</div>"
                f"<div style='font-family:Syne;font-size:22px;font-weight:800;color:#4f7cff'>{unread}</div>"
                f"<div style='font-size:10px;color:#9aa0b4'>unread</div></div>",
                unsafe_allow_html=True,
            )
        
        with col_avail:
            slots = get_all_slots()
            vac   = sum(1 for s in slots if s["status"] == "vacant")
            st.markdown(
                f"<div style='text-align:center'><div style='font-size:11px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em'>Available</div>"
                f"<div style='font-family:Syne;font-size:22px;font-weight:800;color:#22c55e'>{vac}</div>"
                f"<div style='font-size:10px;color:#9aa0b4'>slots free</div></div>",
                unsafe_allow_html=True,
            )

        st.divider()
        
        col_theme, col_logout = st.columns(2)
        
        with col_theme:
            dark = st.toggle("Dark mode", value=st.session_state.dark)
            if dark != st.session_state.dark:
                st.session_state.dark = dark
                st.rerun()

        with col_logout:
            if st.button("Sign Out", use_container_width=True):
                for k in ["logged_in", "user", "role"]:
                    st.session_state[k] = None if k != "logged_in" else False
                st.rerun()

    # ── Page routing ─────────────────────────
    if   page.startswith("🗺️"): _availability()
    elif page.startswith("📅"): _pre_book()
    elif page.startswith("📋"): _my_bookings()
    elif page.startswith("💰"): _rates_view()
    elif page.startswith("👤"): _profile_page()


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

            with st.form("booking_form"):
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
                    st.form_submit_button("Book Now", disabled=True)
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

                submitted = st.form_submit_button("✅ Book Now", use_container_width=True)

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
                
                # Show booking confirmation with payment option
                st.success(f"✅ Booking Created! Ref: **{ref}**")
                st.balloons()
                
                st.markdown(f"""
                <div style='background:#1e222c;border-radius:8px;padding:16px;margin-top:1rem;border:1px solid #4f7cff'>
                    <div style='color:#4f7cff;font-weight:700;margin-bottom:12px'>Your Booking Details</div>
                    <div style='font-size:13px;color:#9aa0b4;line-height:1.8'>
                        <div><b>Reference:</b> <code style='color:#22c55e'>{ref}</code></div>
                        <div><b>Slot:</b> {sel_slot['slot_code']} (Floor {sel_slot['floor']})</div>
                        <div><b>Date:</b> {booking_date.strftime("%d %b %Y")}</div>
                        <div><b>Time:</b> {from_t.strftime("%H:%M")} - {to_t.strftime("%H:%M")}</div>
                        <div><b>Vehicle:</b> {vehicle_no}</div>
                        <div style='margin-top:8px;padding-top:8px;border-top:1px solid #2a2f3d'>
                            <div style='font-size:11px'>Amount Due: <span style='color:#f59e0b;font-weight:700'>₹{amount:.2f}</span></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.warning("⚠️ This booking is pending payment. Please proceed to payment to confirm.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💳 Proceed to Payment", use_container_width=True, key="pay_btn"):
                        st.markdown(
                            f'<meta http-equiv="refresh" content="0; url=/?page=payment_page&booking_ref={ref}">',
                            unsafe_allow_html=True
                        )
                        st.info(f"Redirecting to payment page... Click [here](/?page=payment_page&booking_ref={ref}) if not redirected.")
                
                with col2:
                    if st.button("📋 View My Bookings", use_container_width=True):
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
            _display_bookings_list(active_bookings)
    
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
                    qr_data = f"SLOTX|{b['booking_ref']}|{b['vehicle_no']}|{b['slot_code']}"
                    qr = qrcode.QRCode(version=1, box_size=8)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    buf = io.BytesIO()
                    qr_img.save(buf, "PNG")
                    buf.seek(0)
                    st.image(buf, use_column_width=True)


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
                        st.markdown(
                            f'<meta http-equiv="refresh" content="0; url=/?page=payment_page&booking_ref={b["booking_ref"]}">',
                            unsafe_allow_html=True
                        )
                        st.info(f"Redirecting to payment...")
                
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