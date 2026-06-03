"""
SLotX — Smart Parking Management System
Next-Generation Parking Slot Management

Run: streamlit run app.py
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import init_db, authenticate
from utils.styles import apply_theme, badge_html, rate_card_html, animated_slot_card_html, TIME_SLOTS

st.set_page_config(
    page_title="SLotX — Smart Parking",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB bootstrap ─────────────────────────────
init_db()

# ── Asset paths ──────────────────────────────
from pathlib import Path
import time
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "slotx_logo.jpeg"
SPLASH_VIDEO_PATH = BASE_DIR / "splash_video.mp4"

# ── Session defaults ─────────────────────────
defaults = {
    "logged_in": False,
    "user":      None,
    "role":      None,
    "dark":      True,
    "splash_done": False,
    "auth_mode": "login",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme ────────────────────────────────────
st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)

# ── Splash screen ────────────────────────────
# Initialize session state variables
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if "splash_start_time" not in st.session_state:
    st.session_state.splash_start_time = None

if not st.session_state.splash_shown:
    if st.session_state.splash_start_time is None:
        st.session_state.splash_start_time = time.time()
    
    elapsed_time = time.time() - st.session_state.splash_start_time
    
    # Display splash screen for 5 seconds
    if elapsed_time < 5:
        st.markdown("""
        <style>
            .splash-container {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f1729 100%);
                flex-direction: column;
                gap: 2rem;
            }
            
            .splash-video-wrapper {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                max-width: 500px;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 25px 50px -12px rgba(79, 124, 255, 0.3),
                            0 0 100px -20px rgba(34, 197, 94, 0.2);
                border: 2px solid rgba(79, 124, 255, 0.2);
                background: linear-gradient(135deg, rgba(79, 124, 255, 0.1), rgba(34, 197, 94, 0.1));
                animation: splash-pulse 2s ease-in-out infinite;
            }
            
            @keyframes splash-pulse {
                0%, 100% {
                    box-shadow: 0 25px 50px -12px rgba(79, 124, 255, 0.3),
                                0 0 100px -20px rgba(34, 197, 94, 0.2);
                }
                50% {
                    box-shadow: 0 25px 50px -12px rgba(79, 124, 255, 0.5),
                                0 0 100px -10px rgba(34, 197, 94, 0.4);
                }
            }
            
            .splash-video-wrapper video {
                width: 100%;
                height: auto;
                display: block;
            }
            
            .splash-logo {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                animation: fade-in 0.8s ease-out;
            }
            
            .splash-logo-icon {
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #4f7cff, #22c55e);
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Syne, sans-serif;
                font-weight: 800;
                font-size: 32px;
                color: #fff;
                box-shadow: 0 10px 25px rgba(79, 124, 255, 0.4);
            }
            
            .splash-text {
                text-align: center;
                color: #e8eaf0;
                animation: fade-in 1s ease-out;
            }
            
            .splash-text h1 {
                font-family: Syne, sans-serif;
                font-size: 36px;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(135deg, #4f7cff, #22c55e);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .splash-text p {
                font-size: 14px;
                color: #9aa0b4;
                margin: 8px 0 0 0;
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }
            
            .splash-progress {
                margin-top: 2rem;
                width: 60px;
                height: 2px;
                background: rgba(79, 124, 255, 0.1);
                border-radius: 1px;
                overflow: hidden;
            }
            
            .splash-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #4f7cff, #22c55e);
                border-radius: 1px;
                animation: progress-load 5s ease-in-out forwards;
                box-shadow: 0 0 10px rgba(79, 124, 255, 0.5);
            }
            
            @keyframes progress-load {
                0% { width: 0%; }
                100% { width: 100%; }
            }
            
            @keyframes fade-in {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.markdown("""
            <div class="splash-container">
                <div class="splash-logo">
                    <div class="splash-logo-icon">S</div>
                </div>
                <div class="splash-video-wrapper">
            """, unsafe_allow_html=True)
            
            video_file = open('splash_video.mp4', 'rb')
            st.video(video_file)
            
            st.markdown("""
                </div>
                <div class="splash-text">
                    <h1>SLotX</h1>
                    <p>Smart Parking System</p>
                </div>
                <div class="splash-progress">
                    <div class="splash-progress-bar"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-redirect after 5 seconds
        time.sleep(0.5)
        st.rerun()
    else:
        # Mark splash as shown and redirect to login
        st.session_state.splash_shown = True
        st.session_state.splash_start_time = None
        st.rerun()

# ── Router ───────────────────────────────────
if st.session_state.logged_in:
    if st.session_state.role == "admin":
        try:
            from pages.admin_ui_updated import render_admin
            render_admin()
        except ImportError:
            st.error("Admin module not found. Please ensure pages/admin_ui.py exists.")
    else:
        try:
            from pages.user_ui_updated import render_user
            render_user()
        except ImportError:
            st.error("User module not found. Please ensure pages/user_ui.py exists.")
else:
    # ── LOGIN PAGE ───────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        # Logo
        st.markdown("<div style='text-align:center;padding:1.2rem 0 1rem'>", unsafe_allow_html=True)
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=165)
        st.markdown("""
          <div style='font-family:Syne,sans-serif;font-size:42px;font-weight:900;letter-spacing:6px;
                      background:linear-gradient(135deg,#00f5ff,#22c55e,#4f7cff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>SLOTX</div>
          <div style='font-size:14px;color:#b9fff8;letter-spacing:1.5px;margin-top:6px'>Smart Parking. Smarter Future.</div>
        </div>
        """, unsafe_allow_html=True)

        # Theme toggle
        dark_toggle = st.toggle("Dark mode", value=st.session_state.dark, key="login_theme")
        if dark_toggle != st.session_state.dark:
            st.session_state.dark = dark_toggle
            st.rerun()

        st.divider()

        auth_mode = st.radio("Account", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
        st.session_state.auth_mode = "register" if auth_mode == "Create Account" else "login"

        if st.session_state.auth_mode == "register":
            with st.form("register_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Your name")
                new_username = st.text_input("Username", placeholder="choose username")
                email = st.text_input("Email", placeholder="you@example.com")
                phone = st.text_input("Phone", placeholder="+91...")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button("Create Account →", use_container_width=True)
            if reg_submit:
                if new_password != confirm_password:
                    st.error("Password and confirm password do not match.")
                else:
                    ok, msg = register_user(new_username, new_password, full_name, email, phone)
                    if ok:
                        st.success(msg)
                        st.session_state.auth_mode = "login"
                    else:
                        st.error(msg)
            st.info("Admin account is fixed: admin / admin123")
            st.stop()

        role = st.radio(
            "Sign in as",
            ["👤  User", "🛡️  Admin"],
            horizontal=True,
            label_visibility="collapsed",
        )
        role_key = "user" if role.startswith("👤") else "admin"

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="admin" if role_key == "admin" else "user1",
            )
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = authenticate(username, password)
                if user and user["role"] == role_key:
                    st.session_state.logged_in = True
                    st.session_state.user       = user
                    st.session_state.role       = user["role"]
                    st.rerun()
                elif user and user["role"] != role_key:
                    st.error(f"This account is not an {role_key}. Choose the correct role.")
                else:
                    st.error("Invalid username or password.")

        st.markdown(
            f"<div style='text-align:center;font-size:12px;color:#5c6278;margin-top:1.5rem'>"
            f"<strong>Demo Credentials:</strong><br>"
            f"👤 <code>user1 / pass123</code><br>"
            f"🛡️ <code>admin / admin123</code>"
            f"</div>",
            unsafe_allow_html=True,
        )
    
    # ── SIDEBAR: ABOUT & CONTACT ─────────────
    with st.sidebar:
        st.markdown("""
        <div style='display:flex;align-items:center;gap:10px;padding:6px 0 16px'>
          <div style='width:36px;height:36px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-family:Syne,sans-serif;font-weight:800;font-size:18px;color:#fff'>S</div>
          <div>
            <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700'>SLotX</div>
            <div style='font-size:11px;color:#9aa0b4'>Smart Parking</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        sidebar_option = st.radio(
            "Menu",
            ["🏠 Home", "ℹ️ About Us", "📞 Contact Us"],
            label_visibility="collapsed",
        )
        
        st.divider()
        
        if sidebar_option == "ℹ️ About Us":
            st.markdown("### 👥 Meet Our Team")
            
            st.markdown("""
            <div style='background:#111318;border:1px solid #2a2f3d;border-radius:12px;padding:1.5rem;margin:1rem 0'>
              <div style='margin-bottom:1.5rem'>
                <div style='font-weight:700;font-size:14px;color:#4f7cff'>👩‍💻 Sneha Dutta</div>
                <div style='font-size:12px;color:#9aa0b4;margin-top:4px'>Code and Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>Full-stack development, UI/UX design, and system architecture</div>
              </div>
              
              <div style='margin-bottom:1.5rem'>
                <div style='font-weight:700;font-size:14px;color:#4f7cff'>👩‍💻 Sangita Malakar</div>
                <div style='font-size:12px;color:#9aa0b4;margin-top:4px'>Code and Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>Backend systems, database design, and code optimization</div>
              </div>
              
              <div>
                <div style='font-weight:700;font-size:14px;color:#4f7cff'>👩‍🎨 Mousumi Haldar</div>
                <div style='font-size:12px;color:#9aa0b4;margin-top:4px'>Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>User interface, visual design, and user experience optimization</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background:rgba(79,124,255,.08);border:1px solid rgba(79,124,255,.25);
                        border-radius:8px;padding:1.25rem;margin-top:1.5rem;font-size:13px;color:#4f7cff'>
            <strong>✨ About SLotX</strong><br><br>
            SLotX is a next-generation smart parking management system designed to revolutionize urban parking. 
            Built with cutting-edge technology, our platform provides real-time slot availability, intelligent 
            booking, advanced analytics, and seamless entry/exit management.
            </div>
            """, unsafe_allow_html=True)
        
        elif sidebar_option == "📞 Contact Us":
            st.markdown("### 📞 Get In Touch")
            
            st.markdown("""
            <div style='background:#111318;border:1px solid #2a2f3d;border-radius:12px;padding:1.5rem;margin:1rem 0'>
              
              <div style='margin-bottom:1.25rem'>
                <div style='font-size:12px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px'>📱 Phone Numbers</div>
                <div style='font-size:14px;color:#e8eaf0;margin-bottom:8px;font-weight:500'>+91-8765-432-109</div>
                <div style='font-size:14px;color:#e8eaf0;font-weight:500'>+91-9876-543-210</div>
              </div>
              
              <div style='border-top:1px solid #2a2f3d;padding-top:1.25rem'>
                <div style='font-size:12px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px'>✉️ Email</div>
                <div style='font-size:14px;color:#4f7cff;word-break:break-all;font-weight:500'>
                  support@slotx.in
                </div>
              </div>
              
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);
                        border-radius:8px;padding:1.25rem;margin-top:1.5rem;font-size:13px;color:#22c55e'>
            <strong>⏰ Business Hours</strong><br><br>
            Monday - Friday: 9:00 AM - 6:00 PM<br>
            Saturday: 9:00 AM - 2:00 PM<br>
            Sunday: Closed<br><br>
            <strong>Response Time:</strong> Within 2 hours
            </div>
            """, unsafe_allow_html=True)
        
        else:  # Home
            st.markdown("""
            <div style='background:rgba(79,124,255,.08);border:1px solid rgba(79,124,255,.25);
                        border-radius:8px;padding:1.5rem;margin:1rem 0;font-size:13px'>
            <strong>👋 Welcome to SLotX</strong><br><br>
            Sign in above to access:<br>
            ✓ Real-time parking availability<br>
            ✓ Smart slot booking system<br>
            ✓ QR code generation<br>
            ✓ Entry/Exit tracking<br>
            ✓ Advanced analytics<br>
            ✓ Waitlist management<br><br>
            <strong>New users?</strong> Use demo credentials to explore!
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        dark = st.toggle("Dark mode", value=st.session_state.dark, key="login_sidebar_theme")
        if dark != st.session_state.dark:
            st.session_state.dark = dark
            st.rerun()
