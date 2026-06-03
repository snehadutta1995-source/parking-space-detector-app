"""
SLotX — Admin Interface
Management Console for Smart Parking System
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os, io
from pathlib import Path
from datetime import datetime, timedelta

matplotlib.use("Agg")

from utils.database import (
    get_all_slots, add_slot, log_entry, log_exit, update_slot, delete_slot, toggle_slot_status,
    get_all_bookings, cancel_booking, complete_booking,
    get_rates, update_rate, get_analytics, get_revenue_by_period,
    save_media_record, get_all_media,
    get_entry_exit_logs, get_overstay_alerts, resolve_overstay_alert, log_entry_by_ref, log_exit_by_ref,
    get_waitlist, remove_from_waitlist,
)
from utils.styles import apply_theme, badge_html, rate_card_html, animated_slot_card_html, TIME_SLOTS

if not hasattr(st, "experimental_dialog") and hasattr(st, "dialog"):
    st.experimental_dialog = st.dialog

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
BASE_DIR = Path(__file__).resolve().parents[1]
LOGO_PATH = BASE_DIR / "slotx_logo.jpeg"


# ─────────────────────────────────────────────
# Footer Overlay Dialogs (shared with user module)
# ─────────────────────────────────────────────
@st.experimental_dialog("🏠 Home", width="large")
def _footer_home_dialog():
    st.markdown("""
    ### Welcome to SLotX Admin

    **Smart Parking Management System - Administrator Dashboard**

    This is your command center for managing the entire SLotX parking network.

    #### Key Admin Features
    - 📊 **Dashboard** - Real-time occupancy and analytics
    - 🅿️ **Slot Management** - Add, edit, and manage parking slots
    - 📁 **Media Control** - Monitor parking area media feeds
    - 📋 **Booking Admin** - Manage and track all bookings
    - 💰 **Rate Settings** - Configure parking rates
    - 📈 **Advanced Analytics** - Detailed reporting and insights
    - 🚗 **Entry/Exit Logs** - Track vehicle movements
    - ⚠️ **Overstay Alerts** - Monitor and resolve overstays

    Use this dashboard to optimize your parking operations.
    """)


@st.experimental_dialog("ℹ️ About Admin", width="large")
def _footer_about_dialog():
    st.markdown("""
    ### About SLotX Admin Console

    The SLotX Admin Dashboard is designed for parking facility managers and administrators.

    #### Admin Capabilities
    - **Full Control** - Manage all aspects of your parking facility
    - **Real-Time Data** - Live occupancy, revenue, and booking information
    - **Advanced Tools** - Overstay management, media monitoring, analytics
    - **User Management** - Monitor user activity and bookings
    - **Revenue Insights** - Track income and occupancy trends
    - **System Monitoring** - Entry/exit logs and security features

    #### For Support
    Contact the SLotX support team for admin-specific assistance.
    """)


def _render_footer():
    """Render the admin footer section."""
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
        if st.button("ℹ️ About", use_container_width=True):
            _footer_about_dialog()

    with footer_cols[2]:
        st.markdown("<div style='opacity:0;cursor:default;'><button style='width:100%;'>Placeholder</button></div>", unsafe_allow_html=True)

    with footer_cols[3]:
        st.markdown("<div style='opacity:0;cursor:default;'><button style='width:100%;'>Placeholder</button></div>", unsafe_allow_html=True)

    with footer_cols[4]:
        st.markdown("<div style='opacity:0;cursor:default;'><button style='width:100%;'>Placeholder</button></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; padding-top: 10px; color: #6b7280; font-size: 11px;'>© 2026 SLotX — Smart Parking Solutions. All rights reserved.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
def render_admin():
    st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)

    BASE_DIR = Path(__file__).resolve().parents[1]
    LOGO_PATH = BASE_DIR / "slotx_logo.jpeg"

    # Hide sidebar and expand content to full width (admin console only)
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
    if st.button(dark_label, key="left_dark_toggle_admin"):
        st.session_state.dark = not st.session_state.dark
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Top Bar: Navigation Buttons + Sign Out ────
    top_bar_cols = st.columns([5.8, 0.7])

    # Left: Navigation buttons (split into two rows due to space)
    with top_bar_cols[0]:
        nav_row1 = st.columns(5, gap="small")
        nav_row2 = st.columns(4, gap="small")

        nav_items_1 = [
            ("📊 Dashboard", "dashboard"),
            ("🅿️ Slots", "slots"),
            ("📁 Media", "media"),
            ("📋 Bookings", "bookings"),
            ("💰 Rates", "rates"),
        ]

        nav_items_2 = [
            ("📈 Analytics", "analytics"),
            ("🚗 Entry/Exit", "entry_exit"),
            ("⚠️ Overstay", "overstay"),
            ("⏳ Waitlist", "waitlist"),
        ]

        # Initialize current page in session state
        if "admin_current_page" not in st.session_state:
            st.session_state.admin_current_page = "dashboard"

        # First row of nav buttons
        for col, (label, page_key) in zip(nav_row1, nav_items_1):
            with col:
                if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.admin_current_page = page_key
                    st.rerun()

        # Second row of nav buttons
        for col, (label, page_key) in zip(nav_row2, nav_items_2):
            with col:
                if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.admin_current_page = page_key
                    st.rerun()

        # Determine which page to show
        page = st.session_state.admin_current_page

    # Right: Sign Out Button
    with top_bar_cols[1]:
        if st.button("➡️ Sign Out", use_container_width=True, key="logout_admin"):
            for k in ["logged_in", "user", "role"]:
                st.session_state[k] = None if k != "logged_in" else False
            st.rerun()


    st.divider()

    # ── Page routing ─────────────────────────
    if   page == "dashboard": _dashboard()
    elif page == "slots": _slots_page()
    elif page == "media": _uploads_page()
    elif page == "bookings": _bookings_page()
    elif page == "rates": _rates_page()
    elif page == "analytics": _analytics_page()
    elif page == "entry_exit": _entry_exit_page()
    elif page == "overstay": _overstay_page()
    elif page == "waitlist": _waitlist_page()

    # ── Footer (shown on all pages) ──────────
    _render_footer()


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
def _dashboard():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>📊</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Dashboard</h1>
        <div style='font-size:13px;color:#9aa0b4'>Real-time parking management overview</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_analytics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Slots",     stats["total"])
    c2.metric("Available",       stats["vacant"],          delta=f"{int(stats['vacant']/stats['total']*100)}% free" if stats["total"] else "—")
    c3.metric("Occupied",        stats["occupied"],         delta_color="inverse", delta=f"{int(stats['occupied']/stats['total']*100)}% full" if stats["total"] else "—")
    c4.metric("Today's Revenue", f"₹{stats['today_revenue']:.0f}")

    st.divider()
    col_a, col_b = st.columns(2)

    # Recent bookings
    with col_a:
        st.markdown("### 📋 Recent Bookings")
        bookings = get_all_bookings()[:6]
        if bookings:
            rows = []
            for b in bookings:
                status_icon = "🟢" if b["status"] == "active" else ("✅" if b["status"] == "completed" else "❌")
                rows.append({
                    "Ref":     b["booking_ref"],
                    "User":    b["user_name"],
                    "Vehicle": b["vehicle_no"],
                    "Slot":    b["slot_code"],
                    "Amount":  f"₹{b['amount']:.0f}",
                    "Status":  f"{status_icon}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No bookings yet.")

    # Peak hours chart
    with col_b:
        st.markdown("### ⏰ Peak Hours Occupancy")
        hours  = ["6am","7am","8am","9am","10am","11am","12pm","1pm"]
        values = [35, 62, 88, 100, 92, 74, 58, 67]
        fig, ax = plt.subplots(figsize=(6, 3.5))
        bg = "#111318" if st.session_state.dark else "#ffffff"
        fg = "#e8eaf0" if st.session_state.dark else "#1a1d27"
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
        bar_colors = ["#ef4444" if v > 85 else "#f59e0b" if v > 60 else "#4f7cff" for v in values]
        ax.bar(hours, values, color=bar_colors, edgecolor="none", width=0.65)
        ax.set_ylim(0, 115)
        ax.tick_params(colors=fg, labelsize=9)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.yaxis.set_visible(False)
        for i, v in enumerate(values):
            ax.text(i, v + 2, f"{v}%", ha="center", va="bottom", fontsize=8, color=fg)
        ax.set_title("Occupancy % by Hour", color=fg, fontsize=11, pad=8)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    # Floor summary
    st.divider()
    st.markdown("### 🏢 Floor Summary")
    fc1, fc2, fc3 = st.columns(3)
    for col, floor_data in zip([fc1, fc2, fc3], stats["by_floor"]):
        fl   = floor_data["floor"]
        tot  = floor_data["total"]
        vac2 = floor_data["vacant"]
        pct2 = int(vac2 / tot * 100) if tot else 0
        col.metric(f"Floor {fl}", f"{vac2}/{tot} free", delta=f"{pct2}% available")


# ─────────────────────────────────────────────
# SLOTS MANAGEMENT
# ─────────────────────────────────────────────
def _slots_page():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>🅿️</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Parking Slots</h1>
        <div style='font-size:13px;color:#9aa0b4'>Manage all parking slots and floor layouts</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_map, tab_add, tab_manage = st.tabs(["🎨 Grid", "🗺️ Floor Map", "➕ Add", "✏️ Edit"])

    # ── Animated Visual grid ───────────────────────────
    with tab_view:
        slots = get_all_slots()
        st.markdown("*Click slots to toggle their status*")
        
        for floor in ["G", "1", "2"]:
            fslots = [s for s in slots if s["floor"] == floor]
            if not fslots:
                continue
            vac_f = sum(1 for s in fslots if s["status"] == "vacant")
            st.markdown(f"**Floor {floor}** — {vac_f}/{len(fslots)} free")
            cols = st.columns(8)
            for i, slot in enumerate(fslots):
                with cols[i % 8]:
                    st.markdown(
                        animated_slot_card_html(slot, clickable=True, index=i),
                        unsafe_allow_html=True,
                    )
                    if st.button("Toggle", key=f"toggle_{slot['id']}", use_container_width=True):
                        toggle_slot_status(slot["id"])
                        st.rerun()
            st.markdown("")

    # ── Floor Map View ───────────────────────────────
    with tab_map:
        st.markdown("**Parking Floor Map**")
        
        slots = get_all_slots()
        for floor in ["G", "1", "2"]:
            fslots = [s for s in slots if s["floor"] == floor]
            if not fslots:
                continue
            
            vac_f = sum(1 for s in fslots if s["status"] == "vacant")
            occ_f = len(fslots) - vac_f
            
            st.markdown(f"""
            <div style='background:#181b22;border:1px solid #2a2f3d;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem'>
                <div style='font-family:Syne;font-weight:800;font-size:20px'>Floor {floor}</div>
                <div style='display:flex;gap:2rem;font-size:14px'>
                  <span>🟢 {vac_f} Free</span>
                  <span>🔴 {occ_f} Occupied</span>
                </div>
              </div>
              <div style='display:grid;grid-template-columns:repeat(8,1fr);gap:8px'>
            """, unsafe_allow_html=True)
            
            for slot in fslots:
                is_vacant = slot["status"] == "vacant"
                color = "#22c55e" if is_vacant else "#ef4444"
                bg = "rgba(34,197,94,.15)" if is_vacant else "rgba(239,68,68,.15)"
                icon = "🚗" if slot["type"] == "4-wheeler" else "🏍️"
                
                st.markdown(f"""
                <div style='background:{bg};border:2px solid {color};border-radius:8px;padding:12px;text-align:center;font-weight:700'>
                  <div style='font-size:16px;margin-bottom:4px'>{icon}</div>
                  <div style='font-size:12px;color:{color}'>{slot['slot_code']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Add Slot ───────────────────────────────────
    with tab_add:
        st.markdown("#### Add New Parking Slot")
        with st.form("add_slot_form"):
            col1, col2, col3, col4 = st.columns(4)
            slot_code = col1.text_input("Slot Code", placeholder="S25")
            floor     = col2.selectbox("Floor", ["G", "1", "2"])
            vtype     = col3.selectbox("Vehicle Type", ["4-wheeler", "2-wheeler"])
            status    = col4.selectbox("Status", ["vacant", "occupied"])

            if st.form_submit_button("✅ Add Slot", use_container_width=True):
                success, msg = add_slot(slot_code, floor, vtype, status)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ── Edit/Delete ───────────────────────────
    with tab_manage:
        st.markdown("#### Edit or Delete Slot")
        slots = get_all_slots()
        selected = st.selectbox("Select Slot", [f"{s['slot_code']} (Floor {s['floor']})" for s in slots])
        sel_slot = next((s for s in slots if f"{s['slot_code']} (Floor {s['floor']})" == selected), None)

        if sel_slot:
            col1, col2, col3, col4 = st.columns(4)
            new_floor = col1.selectbox("Floor", ["G", "1", "2"], index=["G", "1", "2"].index(sel_slot["floor"]), key="edit_floor")
            new_type = col2.selectbox("Vehicle Type", ["4-wheeler", "2-wheeler"], index=0 if sel_slot["type"] == "4-wheeler" else 1, key="edit_type")
            new_status = col3.selectbox("Status", ["vacant", "occupied"], index=0 if sel_slot["status"] == "vacant" else 1, key="edit_status")

            col_save, col_del = st.columns(2)
            if col_save.button("💾 Update", use_container_width=True):
                update_slot(sel_slot["id"], new_floor, new_type, new_status)
                st.success("✅ Slot updated.")
                st.rerun()

            if col_del.button("🗑️ Delete", use_container_width=True):
                delete_slot(sel_slot["id"])
                st.warning("❌ Slot deleted.")
                st.rerun()


# ─────────────────────────────────────────────
# COMPLETE ADMIN PAGES
# ─────────────────────────────────────────────

def _uploads_page():
    st.markdown("## 📁 Media Uploads")
    st.info("Upload and manage parking lot images, CCTV clips, reports and documents.")
    uploaded = st.file_uploader("Upload media/document", type=["png","jpg","jpeg","mp4","pdf","docx","txt"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            save_path = os.path.join(UPLOAD_DIR, f.name)
            with open(save_path, "wb") as out:
                out.write(f.getbuffer())
            save_media_record(f.name, f.type or "file")
        st.success("Uploaded successfully.")
    media = get_all_media()
    if media:
        st.dataframe(pd.DataFrame(media), use_container_width=True, hide_index=True)
    else:
        st.info("No uploads yet.")


def _bookings_page():
    st.markdown("## 📋 Bookings Management")
    bookings = get_all_bookings()
    if bookings:
        df = pd.DataFrame(bookings)
        show_cols = [c for c in ["id","booking_ref","user_name","vehicle_no","slot_code","from_date","from_time","to_time","amount","status"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
        active = [b for b in bookings if b["status"] == "active"]
        if active:
            opts = {f"{b['booking_ref']} - {b['vehicle_no']} - {b['slot_code']}": b for b in active}
            selected = st.selectbox("Select active booking", list(opts.keys()))
            c1, c2 = st.columns(2)
            if c1.button("Cancel Booking", use_container_width=True):
                cancel_booking(opts[selected]["id"]); st.success("Booking cancelled."); st.rerun()
            if c2.button("Mark Completed", use_container_width=True):
                complete_booking(opts[selected]["id"]); st.success("Booking completed."); st.rerun()
    else:
        st.info("No bookings found.")


def _rates_page():
    st.markdown("## 💰 Rates & Configuration")
    rates = get_rates()
    st.markdown(rate_card_html(rates), unsafe_allow_html=True)
    st.markdown("### Edit Rates")
    c1, c2 = st.columns(2)
    four = c1.number_input("4-wheeler hourly rate", min_value=0.0, value=float(rates.get("4-wheeler", 30)), step=5.0)
    two = c2.number_input("2-wheeler hourly rate", min_value=0.0, value=float(rates.get("2-wheeler", 10)), step=5.0)
    if st.button("Save Rate Configuration", use_container_width=True):
        update_rate("4-wheeler", four); update_rate("2-wheeler", two)
        st.success("Rates updated."); st.rerun()


def _analytics_page():
    st.markdown("## 📈 Analytics & Reports")
    stats = get_analytics()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Slots", stats["total"]); c2.metric("Vacant", stats["vacant"]); c3.metric("Occupied", stats["occupied"]); c4.metric("Revenue", f"₹{stats['total_revenue']:.0f}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Slot Status")
        st.bar_chart(pd.DataFrame({"Status":["Vacant","Occupied"],"Count":[stats["vacant"],stats["occupied"]]}).set_index("Status"))
    with col2:
        st.markdown("### Revenue Trend")
        rev = get_revenue_by_period("day")
        if rev:
            st.line_chart(pd.DataFrame(rev).set_index("period")[["revenue"]])
        else:
            st.info("Revenue data will appear after bookings.")


def _entry_exit_page():
    st.markdown("## 🚗 Entry/Exit Logs")
    st.info("Scan/enter booking reference at entry and exit gate.")
    col1, col2 = st.columns(2)
    with col1:
        ref = st.text_input("Booking Reference for Entry", placeholder="BK001")
        gate = st.selectbox("Gate", ["Main", "North", "South", "Basement"])
        if st.button("Log Entry", use_container_width=True):
            ok, msg = log_entry_by_ref(ref, gate)
            st.success(msg) if ok else st.error(msg)
    with col2:
        exit_ref = st.text_input("Booking Reference for Exit", placeholder="BK001", key="exit_booking_ref")
        if st.button("Log Exit", use_container_width=True):
            ok, msg = log_exit_by_ref(exit_ref)
            st.success(msg) if ok else st.error(msg)
    logs = get_entry_exit_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)


def _overstay_page():
    st.markdown("## ⚠️ Overstay Management")
    alerts = get_overstay_alerts()
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)
        opts = {f"{a['booking_ref']} - ₹{a['penalty_amount']}": a for a in alerts}
        sel = st.selectbox("Resolve alert", list(opts.keys()))
        if st.button("Mark Resolved"):
            resolve_overstay_alert(opts[sel]["id"]); st.success("Alert resolved."); st.rerun()
    else:
        st.success("No pending overstay alerts.")
        sample = pd.DataFrame([
            {"Vehicle":"WB02AB1234","Slot":"S08","Extra Time":"18 min","Penalty":"₹90","Status":"Sample"},
            {"Vehicle":"MH12XY9999","Slot":"S12","Extra Time":"34 min","Penalty":"₹170","Status":"Sample"},
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)


def _waitlist_page():
    st.markdown("## ⏳ Waitlist Management")
    wait = get_waitlist()
    if wait:
        st.dataframe(pd.DataFrame(wait), use_container_width=True, hide_index=True)
        opts = {f"#{w['position']} - {w['name']} - {w['vehicle_type']}": w for w in wait}
        sel = st.selectbox("Assign/remove from waitlist", list(opts.keys()))
        if st.button("Assign Slot / Mark Fulfilled", use_container_width=True):
            remove_from_waitlist(opts[sel]["id"]); st.success("Waitlist entry fulfilled."); st.rerun()
    else:
        st.info("No active waitlist entries.")
