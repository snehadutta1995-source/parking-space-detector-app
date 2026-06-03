"""
SLotX — User Portal (Enhanced & Professional UI)
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

def render_user():
    st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)
    user = st.session_state.user

    # ── Sidebar ───────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:10px 0 20px'>
          <div style='width:42px;height:42px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                      display:flex;align-items:center;justify-content:center;
                      font-family:Syne,sans-serif;font-weight:800;font-size:22px;color:#fff;box-shadow: 0 4px 12px rgba(79,124,255,0.3)'>S</div>
          <div>
            <div style='font-family:Syne,sans-serif;font-size:17px;font-weight:700;letter-spacing:0.5px;'>SLotX</div>
            <div style='font-size:11px;color:#9aa0b4;text-transform:uppercase;letter-spacing:1px'>User Portal</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        initials = "".join(p[0].upper() for p in user["name"].split()[:2])
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;background:linear-gradient(145deg, #1e2230, #141722);
                    border-radius:12px;padding:14px;margin-bottom:1.5rem;border:1px solid #2a3146;box-shadow: 0 4px 15px rgba(0,0,0,0.2)'>
          <div style='width:44px;height:44px;background:linear-gradient(135deg,#22c55e,#4f7cff);border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-size:16px;font-weight:700;color:#fff;box-shadow:0 2px 8px rgba(34,197,94,0.3)'>{initials}</div>
          <div>
            <div style='font-size:14px;font-weight:600;color:#e8eaf0'>{user['name']}</div>
            <div style='font-size:11px;color:#4f7cff;font-weight:500'>✨ Premium Member</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["🗺️ Availability", "📅 Pre-Book", "📋 My Bookings", "💰 Rates", "👤 Profile"],
            label_visibility="collapsed",
        )

        st.divider()

        notifs = get_user_notifications(user["id"], limit=5)
        unread = len([n for n in notifs if n["status"] == "sent"])
        slots = get_all_slots()
        vac   = sum(1 for s in slots if s["status"] == "vacant")
        
        st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;background:#141722;padding:12px;border-radius:10px;border:1px solid #232736;'>
            <div style='text-align:center;border-right:1px solid #232736;padding-right:5px;'>
                <div style='font-size:10px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.05em'>Alerts</div>
                <div style='font-family:Syne;font-size:20px;font-weight:800;color:#4f7cff'>{unread}</div>
                <div style='font-size:10px;color:#6b7280'>unread</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:10px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.05em'>Free Slots</div>
                <div style='font-family:Syne;font-size:20px;font-weight:800;color:#22c55e'>{vac}</div>
                <div style='font-size:10px;color:#6b7280'>available</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

    if   page.startswith("🗺️"): _availability()
    elif page.startswith("📅"): _pre_book()
    elif page.startswith("📋"): _my_bookings()
    elif page.startswith("💰"): _rates_view()
    elif page.startswith("👤"): _profile_page()


def _availability():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;background:linear-gradient(90deg, #1e2235, transparent);padding:15px;border-radius:12px;border-left:4px solid #4f7cff'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 4px 12px rgba(79,124,255,0.2)'>🗺️</div>
      <div>
        <h2 style='margin:0;font-family:Syne,sans-serif;font-weight:700;font-size:26px;'>Parking Availability</h2>
        <div style='font-size:13px;color:#9aa0b4'>Live tracking & structural smart allocation map</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    slots = get_all_slots()
    vac   = sum(1 for s in slots if s["status"] == "vacant")
    occ   = len(slots) - vac

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:#181b26; border: 1px solid #2b3046; padding: 20px; border-radius: 12px; text-align: center;'>
            <div style='font-size: 13px; color: #9aa0b4; text-transform: uppercase; font-weight: 600;'>Available Slots</div>
            <div style='font-size: 36px; font-weight: 800; color: #22c55e; font-family: Syne;'>{vac}</div>
            <div style='font-size: 12px; color: #6b7280;'>{int(vac/len(slots)*100) if slots else 0}% space left</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:#181b26; border: 1px solid #2b3046; padding: 20px; border-radius: 12px; text-align: center;'>
            <div style='font-size: 13px; color: #9aa0b4; text-transform: uppercase; font-weight: 600;'>Occupied Spaces</div>
            <div style='font-size: 36px; font-weight: 800; color: #ef4444; font-family: Syne;'>{occ}</div>
            <div style='font-size: 12px; color: #6b7280;'>Live tracking active</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:#181b26; border: 1px solid #2b3046; padding: 20px; border-radius: 12px; text-align: center;'>
            <div style='font-size: 13px; color: #9aa0b4; text-transform: uppercase; font-weight: 600;'>Total Tracked Capacity</div>
            <div style='font-size: 36px; font-weight: 800; color: #4f7cff; font-family: Syne;'>{len(slots)}</div>
            <div style='font-size: 12px; color: #6b7280;'>Dynamic load layout</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><h4>🔍 Advanced Filter Layout</h4>", unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    ftype   = fc1.selectbox("Vehicle Classification",   ["All", "4-wheeler", "2-wheeler"], key="avail_type")
    ffloor  = fc2.selectbox("Level / Floor",  ["All", "G", "1", "2"], key="avail_floor")
    fstatus = fc3.selectbox("Availability Matrix", ["All", "Vacant", "Occupied"], key="avail_status")

    filtered = slots
    if ftype  != "All":    filtered = [s for s in filtered if s["type"]   == ftype]
    if ffloor != "All":    filtered = [s for s in filtered if s["floor"]  == ffloor]
    if fstatus == "Vacant":   filtered = [s for s in filtered if s["status"] == "vacant"]
    if fstatus == "Occupied": filtered = [s for s in filtered if s["status"] == "occupied"]

    st.divider()
    st.markdown(
        "<div style='display:flex;gap:20px;font-size:13px;color:#9aa0b4;margin-bottom:16px'>"
        "<span><span style='color:#22c55e;margin-right:6px;'>●</span><b>Vacant (Available)</b></span>"
        "<span><span style='color:#ef4444;margin-right:6px;'>●</span><b>Occupied (In-Use)</b></span></div>",
        unsafe_allow_html=True,
    )

    for floor in ["G", "1", "2"]:
        fslots = [s for s in filtered if s["floor"] == floor]
        if not fslots:
            continue
        vf = sum(1 for s in fslots if s["status"] == "vacant")
        st.markdown(f"<div style='padding:6px 12px; background:#1e2330; border-radius:6px; font-weight:600; margin-bottom:12px;'>Floor {floor} Layout &nbsp;•&nbsp; <span style='color:#22c55e'>{vf} open slots</span></div>", unsafe_allow_html=True)
        cols = st.columns(8)
        for i, slot in enumerate(fslots):
            with cols[i % 8]:
                st.markdown(
                    animated_slot_card_html(slot, clickable=True, index=i),
                    unsafe_allow_html=True,
                )
        st.markdown("")


def _pre_book():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;background:linear-gradient(90deg, #1e2235, transparent);padding:15px;border-radius:12px;border-left:4px solid #22c55e'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#22c55e,#4f7cff);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 4px 12px rgba(34,197,94,0.2)'>📅</div>
      <div>
        <h2 style='margin:0;font-family:Syne,sans-serif;font-weight:700;font-size:26px;'>Pre-Book a Smart Slot</h2>
        <div style='font-size:13px;color:#9aa0b4'>Instant scheduling and navigation mapping configuration</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rates = get_rates()
    slots = get_all_slots()

    st.markdown("### 🗺️ Terminal Localization Map")
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
    state = c1.selectbox("State Region", list(parking_data.keys()))
    city = c2.selectbox("Metropolitan Area", list(parking_data[state].keys()))
    area = c3.selectbox("Parking Complex Facility", list(parking_data[state][city].keys()))
    lat, lon = parking_data[state][city][area]
    
    try:
        import folium
        from streamlit_folium import st_folium
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="OpenStreetMap")
        for name, (a_lat, a_lon) in parking_data[state][city].items():
            folium.Marker([a_lat, a_lon], popup=name, tooltip=name, icon=folium.Icon(color="green" if name == area else "blue", icon="car", prefix="fa")).add_to(m)
        st_folium(m, width=900, height=350)
    except Exception:
        st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))
        
    directions_url = "https://www.google.com/maps/dir/?api=1&destination=" + urllib.parse.quote(f"{lat},{lon}")
    st.markdown(f"""
    <div style='background:#141722; padding:12px; border-radius:8px; border:1px dashed #2d3248; margin-top:10px;'>
        📍 <b>Active Complex Selected:</b> {area}, {city}, {state} &nbsp;&nbsp;|&nbsp;&nbsp; 🚀 <a href='{directions_url}' target='_blank' style='color:#4f7cff; text-decoration:none; font-weight:600;'>Get Route Directions →</a>
    </div>
    """, unsafe_allow_html=True)

    tab_book, tab_waitlist = st.tabs(["⚡ Secure Instant Booking", "⏳ Join Smart Queue Waitlist"])

    with tab_book:
        col_form, col_summary = st.columns([1.1, 0.9])

        with col_form:
            st.markdown("#### Form Parameters")
            with st.form("booking_form"):
                vehicle_no = st.text_input("Registration Plate / Vehicle Number", placeholder="WB02AB1234").upper()
                vtype      = st.selectbox("Vehicle Type Structure", ["4-wheeler", "2-wheeler"])
                booking_date = st.date_input("Reservation Date Focus", value=datetime.now().date(), min_value=datetime.now().date())
                from_t   = st.time_input("Arrival Time Horizon", value=time(9, 0))
                duration = st.selectbox("Duration Timeline Block", [1, 2, 3, 4, 6, 8], index=1, format_func=lambda h: f"{h} hour{'s' if h>1 else ''}")

                vac_slots = [s for s in slots if s["status"] == "vacant" and s["type"] == vtype]
                if not vac_slots:
                    st.warning(f"❌ No vacant spatial profiles found matching your {vtype} categorization.")
                    st.form_submit_button("Book Now Locked", disabled=True)
                    return

                slot_opts  = {f"Slot {s['slot_code']} [Level {s['floor']}]": s for s in vac_slots}
                slot_label = st.selectbox("Target Allocation Row/Slot", list(slot_opts.keys()))
                sel_slot   = slot_opts[slot_label]

                from_dt = datetime.combine(datetime.today(), from_t)
                from_minutes = from_dt.hour * 60 + from_dt.minute
                to_minutes   = from_minutes + duration * 60
                to_h, to_m   = divmod(to_minutes % (24*60), 60)
                to_t         = time(to_h, to_m)

                rate   = rates.get(vtype, 30 if vtype == "4-wheeler" else 10)
                amount = rate * duration
                submitted = st.form_submit_button("💳 Proceed to Checkout & Hold Slot", use_container_width=True)

        with col_summary:
            st.markdown("#### Invoice / Summary Preview")
            rate_now = rates.get(vtype if 'vtype' in dir() else "4-wheeler", 30)
            dur_now  = duration if 'duration' in dir() else 2
            amt_now  = rate_now * dur_now
            sl_now   = sel_slot["slot_code"] if 'sel_slot' in dir() else "—"
            date_str = booking_date.strftime("%d %b %Y") if 'booking_date' in dir() else "—"

            st.markdown(f"""
            <div style='background:linear-gradient(135deg, #181c28, #11131a);border:1px solid #2b324c;border-radius:16px;padding:22px; box-shadow:0 8px 24px rgba(0,0,0,0.3)'>
              <div style='text-align:center; padding-bottom:15px; border-bottom:1px dashed #2b324c; margin-bottom:15px;'>
                <div style='font-size:12px; color:#9aa0b4; text-transform:uppercase; letter-spacing:1px;'>Total Gateway Fare</div>
                <div style='font-family:Syne,sans-serif;font-size:42px;font-weight:800;color:#f59e0b; margin:5px 0;'>₹{amt_now}</div>
                <div style='font-size:11px; color:#22c55e; background:rgba(34,197,94,0.1); display:inline-block; padding:2px 8px; border-radius:20px;'>Best Value Guaranteed</div>
              </div>
              <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1e2230'>
                <span style='color:#9aa0b4;font-size:13px'>Selected Date</span>
                <span style='font-weight:600; color:#e8eaf0;'>{date_str}</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1e2230'>
                <span style='color:#9aa0b4;font-size:13px'>Classification</span>
                <span style='font-weight:600; color:#e8eaf0;'>{vtype if 'vtype' in dir() else '—'}</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1e2230'>
                <span style='color:#9aa0b4;font-size:13px'>Tariff Standard</span>
                <span style='color:#f59e0b;font-weight:600'>₹{rate_now}/hr</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1e2230'>
                <span style='color:#9aa0b4;font-size:13px'>Timeline Length</span>
                <span style='font-weight:600; color:#e8eaf0;'>{dur_now} Hours Matrix</span>
              </div>
              <div style='display:flex;justify-content:space-between;padding:10px 0;'>
                <span style='color:#9aa0b4;font-size:13px'>Assigned Node</span>
                <span style='font-family:monospace;color:#4f7cff;font-weight:700; font-size:15px;'>{sl_now}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if submitted:
            if not vehicle_no:
                st.error("Missing vehicular identification matrix. Please configure registration number plates.")
            elif not sel_slot:
                st.error("No core spatial sector locked.")
            else:
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
                
                st.success(f"🎉 System Profile Provisioned! Reference ID: **{ref}**")
                st.balloons()
                
                st.markdown(f"""
                <div style='background:linear-gradient(145deg, #181b26, #1f2436);border-radius:12px;padding:20px;margin-top:1.5rem;border:1px solid #4f7cff; box-shadow:0 4px 20px rgba(79,124,255,0.15)'>
                    <div style='color:#4f7cff;font-weight:700;font-size:16px;margin-bottom:12px; font-family:Syne;'>Lock Mechanism Initialized Successfully</div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:13px; color:#cbd5e1; line-height:1.6;'>
                        <div><b>Receipt Token:</b> <code style='color:#22c55e; font-size:14px;'>{ref}</code></div>
                        <div><b>Node Unit:</b> {sel_slot['slot_code']} (Level {sel_slot['floor']})</div>
                        <div><b>Target Day:</b> {booking_date.strftime("%d %b %Y")}</div>
                        <div><b>Window Duration:</b> {from_t.strftime("%H:%M")} - {to_t.strftime("%H:%M")}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.warning("⚠️ Action Required: Invoice is currently in its checkout lifecycle phase. Finalize transaction verification.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💳 Disburse Balance securely", use_container_width=True, key="pay_btn"):
                        st.markdown(f'<meta http-equiv="refresh" content="0; url=/?page=payment_page&booking_ref={ref}">', unsafe_allow_html=True)
                with c2:
                    if st.button("📋 Open Booking Registry Portfolio", use_container_width=True):
                        st.rerun()

    with tab_waitlist:
        st.markdown("#### Automated Queue Routing")
        with st.form("waitlist_form"):
            w_vtype = st.selectbox("Vehicle Architecture Category", ["4-wheeler", "2-wheeler"], key="wait_type")
            w_date = st.date_input("Target Space Date Window", value=datetime.now().date(), key="wait_date")
            w_duration = st.selectbox("Expected Duration Cycle", [1, 2, 3, 4, 6, 8], index=1, key="wait_dur")
            
            if st.form_submit_button("📝 Register In Queue Stack"):
                pos = add_to_waitlist(st.session_state.user["id"], w_vtype, str(w_date), duration_hr=w_duration)
                st.success(f"🎯 Queue allocation successful! Position verification tag index: #{pos}")
                st.rerun()


def _my_bookings():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;background:linear-gradient(90deg, #1e2235, transparent);padding:15px;border-radius:12px;border-left:4px solid #f59e0b'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#f59e0b,#ef4444);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;'>📋</div>
      <div>
        <h2 style='margin:0;font-family:Syne,sans-serif;font-weight:700;font-size:26px;'>Your Booking Registry</h2>
        <div style='font-size:13px;color:#9aa0b4'>Comprehensive transactional metrics database file system</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bookings = get_user_bookings(st.session_state.user["id"])
    if not bookings:
        st.info("No bookings recorded inside the structural stack workspace file layout.")
        return

    tab_active, tab_pending, tab_completed, tab_cancelled = st.tabs([
        "🟢 Live / Confirmed Logs", "⏳ Pending Verification Lifecycle", "✅ Archive Fulfilled Records", "❌ Revoked Systems"
    ])
    
    with tab_active:
        active_bookings = [b for b in bookings if b["status"] == "active"]
        if not active_bookings: st.info("No active profiles running currently.")
        else: _display_bookings_list(active_bookings)
    with tab_pending:
        pending_bookings = [b for b in bookings if b["status"] == "pending"]
        if not pending_bookings: st.info("Clear system profile pipeline.")
        else: _display_pending_bookings(pending_bookings)
    with tab_completed:
        completed_bookings = [b for b in bookings if b["status"] == "completed"]
        if not completed_bookings: st.info("No historical logs.")
        else: _display_bookings_list(completed_bookings)
    with tab_cancelled:
        cancelled_bookings = [b for b in bookings if b["status"] == "cancelled"]
        if not cancelled_bookings: st.info("No revoked entities registered.")
        else: _display_bookings_list(cancelled_bookings)


def _display_bookings_list(bookings):
    active = [b for b in bookings if b["status"] == "active"]
    spent = sum(b["amount"] for b in bookings if b["status"] != "cancelled")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total System Events", len(bookings))
    m2.metric("Operational Cycles", len(active))
    m3.metric("Financial Settlement Sum", f"₹{spent:.0f}")
    st.divider()

    for b in bookings:
        status_icon = "🟢" if b["status"] == "active" else ("✅" if b["status"] == "completed" else "❌")
        with st.expander(f"{status_icon} Token Unit: {b['booking_ref']}  —  Node Focus: {b['slot_code']}  · Total Price: ₹{b['amount']:.0f}", expanded=b["status"] == "active"):
            col1, col2 = st.columns([1.4, 1.1])
            with col1:
                st.markdown(f"""
                <div style='background:#141720; padding:15px; border-radius:10px; border:1px solid #232838; line-height:2;'>
                    • <b>Complex Node Target:</b> {b['slot_code']} (Level {b['floor']})<br>
                    • <b>Vehicular Profile Identification:</b> {b['vehicle_no']}<br>
                    • <b>Operational Interval Window:</b> {b['from_date']} ({b['from_time']} - {b['to_time']})<br>
                    • <b>Timeline Duration Array:</b> {b['duration_hr']} hour blocks<br>
                    • <b>Disbursed Transaction Cost:</b> <span style='color:#22c55e; font-weight:600;'>₹{b['amount']:.0f} Settled</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if b["status"] == "active":
                    qr_data = f"SLOTX|{b['booking_ref']}|{b['vehicle_no']}|{b['slot_code']}"
                    qr = qrcode.QRCode(version=1, box_size=6)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    buf = io.BytesIO()
                    qr_img.save(buf, "PNG")
                    buf.seek(0)
                    st.image(buf, width=190, caption="Gate Entry Authentication Token Matrix")


def _display_pending_bookings(bookings):
    st.warning("⚠️ Attention Required: Unresolved balance elements noticed inside execution pipelines.")
    st.divider()
    for b in bookings:
        with st.expander(f"⏳ Processing Lifecycle Entity: {b['booking_ref']} — Node: `{b['slot_code']}`"):
            col1, col2 = st.columns([1.5, 1])
            with col1:
                st.markdown(f"""
                <div style='background:#1b1912; padding:15px; border-radius:10px; border:1px solid #4a3e1a; margin-bottom:12px;'>
                    <b>Temporal Coordinates:</b> {b['from_date']} @ {b['from_time']} – {b['to_time']}<br>
                    <b>Vehicular Target Identification:</b> {b['vehicle_no']}<br>
                    <b>Balance Due Liability:</b> <span style='color:#f59e0b; font-weight:700;'>₹{b['amount']:.0f}</span>
                </div>
                """, unsafe_allow_html=True)
                
                col_pay, col_cancel = st.columns(2)
                with col_pay:
                    if st.button(f"💳 Disburse Balance Now", key=f"pay_{b['id']}", use_container_width=True):
                        st.markdown(f'<meta http-equiv="refresh" content="0; url=/?page=payment_page&booking_ref={b["booking_ref"]}">', unsafe_allow_html=True)
                with col_cancel:
                    if st.button(f"❌ Revoke Pipeline Unit", key=f"cancel_{b['id']}", use_container_width=True):
                        cancel_booking(b['id'])
                        st.success("Lifecycle structural asset destroyed.")
                        st.rerun()


def _rates_view():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;background:linear-gradient(90deg, #1e2235, transparent);padding:15px;border-radius:12px;border-left:4px solid #a855f7'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#a855f7,#4f7cff);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;'>💰</div>
      <div>
        <h2 style='margin:0;font-family:Syne,sans-serif;font-weight:700;font-size:26px;'>Tariff Optimization Configuration</h2>
        <div style='font-size:13px;color:#9aa0b4'>Transparent billing algorithms and class parameters</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    rates = get_rates()
    st.markdown(rate_card_html(rates), unsafe_allow_html=True)


def _profile_page():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;background:linear-gradient(90deg, #1e2235, transparent);padding:15px;border-radius:12px;border-left:4px solid #06b6d4'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#06b6d4,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:22px;'>👤</div>
      <div>
        <h2 style='margin:0;font-family:Syne,sans-serif;font-weight:700;font-size:26px;'>User Control Architecture</h2>
        <div style='font-size:13px;color:#9aa0b4'>Manage credentials, activity nodes, and communication preferences</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    user = get_user(st.session_state.user["id"])
    if not user:
        st.error("System profile synchronization anomaly detected.")
        return
    
    tab_profile, tab_activity = st.tabs(["👤 Core Identity profile", "📊 Activity Telemetry Matrix"])
    
    with tab_profile:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### User Interface Avatar")
            name_value = (user.get("name") or "").strip()
            initials = "".join(p[0].upper() for p in name_value.split()[:2]) if name_value else "NA"
            st.markdown(f"""
            <div style='text-align:center; padding:20px; background:#181b26; border-radius:16px; border:1px solid #2a3146;'>
                <div style='background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:50%;width:110px;height:110px;
                            display:flex;align-items:center;justify-content:center; margin: 0 auto;
                            font-size:42px;font-weight:800;color:white;font-family:Syne;box-shadow:0 4px 15px rgba(0,0,0,0.4)'>
                  {initials}
                </div>
                <div style='margin-top:15px; font-weight:600; color:#e8eaf0; font-size:16px;'>{user.get("name")}</div>
                <div style='font-size:11px; color:#4f7cff; text-transform:uppercase; margin-top:4px;'>Verified Secure Client</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Modify Configuration Coordinates")
            with st.form("profile_form"):
                new_name = st.text_input("Name Identifier", value=user.get("name") or "")
                new_email = st.text_input("Communications Interface Address (Email)", value=user.get("email") or "")
                new_phone = st.text_input("Mobile Security Route Node (Phone)", value=user.get("phone") or "", placeholder="+91-XXXXXXXXXX")
                
                if st.form_submit_button("💾 Synchronize Modification Matrix Changes"):
                    update_user_profile(user["id"], new_name, new_email, new_phone) # type: ignore
                    st.session_state.user["name"] = new_name
                    st.success("✅ Information synchronized.")
                    st.rerun()
    
    with tab_activity:
        st.markdown("#### Metric Tracking Analytics")
        bookings = get_user_bookings(user["id"])
        if bookings:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Registered Booking Events", len(bookings))
            col2.metric("Active Lifecycle Operations", len([b for b in bookings if b["status"] == "active"]))
            col3.metric("Archived Completed Units", len([b for b in bookings if b["status"] == "completed"]))
            col4.metric("Consolidated Settlement Capital", f"₹{sum(b['amount'] for b in bookings if b['status'] != 'cancelled'):.0f}")