"""
SLotX — Smart Parking Management System
Next-Generation Parking Slot Management

Run: streamlit run app.py
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import base64

from utils.database import init_db, authenticate, register_user
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
st.markdown(apply_theme(), unsafe_allow_html=True)

# ── XARA Floating Chatbot ─────────────────────
import streamlit.components.v1 as components
from utils.chatbot_utils import create_chatbot, get_xara_floating_widget
components.html(get_xara_floating_widget(), height=0, scrolling=False)
if "xara_messages" not in st.session_state:
    st.session_state.xara_messages = []
if "xara_instance" not in st.session_state:
    st.session_state.xara_instance = create_chatbot()

# ── Splash screen ────────────────────────────
# Initialize session state variables
# ── Splash screen / Intro page ────────────────────────────
# Added splash video code only. Existing login/dashboard code below remains unchanged.
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


def _video_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def _image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def intro_page():
    """Full-screen splash video. Clicking Enter App opens the auth page."""
    st.markdown("""
    <style>
    .block-container {padding:0 !important; max-width:100% !important;}
    [data-testid="stHeader"], footer {display:none !important;}
    .intro-shell{position:fixed; inset:0; overflow:hidden; background:#020712;}
    .intro-video{position:absolute; inset:0; width:100vw; height:100vh; object-fit:contain; background:#020712;}
    .intro-overlay{position:absolute; inset:0; background:linear-gradient(90deg,rgba(2,7,18,.72),rgba(2,7,18,.18),rgba(2,7,18,.72));}
    .intro-content{position:fixed; z-index:2; inset:0; min-height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:30px;}
    .intro-badge{padding:8px 18px; border-radius:999px; background:rgba(0,229,184,.12); border:1px solid rgba(0,229,184,.32); color:#00E5B8; font-weight:800; letter-spacing:.10em; font-size:12px; text-transform:uppercase;}
    .intro-title{font-family:'Syne',sans-serif; font-size:70px; line-height:1.05; font-weight:900; color:white; margin:18px 0 12px; letter-spacing:-.05em;}
    .intro-title span{color:#00E5B8;}
    .intro-sub{color:#B8C7D9; font-size:18px; max-width:720px; line-height:1.7; margin-bottom:32px;}
    /* Center only one Enter App button over the video */
    .stButton{position:fixed !important; left:50% !important; top:85% !important; transform:translateX(-50%) !important; z-index:10 !important; width:230px !important;}
    .stButton>button{height:56px !important; border-radius:999px !important; font-weight:900 !important; font-size:17px !important; border:1px solid rgba(0,229,184,.45) !important; background:linear-gradient(135deg,#00E5B8,#38C8F8) !important; color:#020712 !important; box-shadow:0 12px 40px rgba(0,229,184,.34) !important;}
    @media (max-width: 768px){
        .intro-title{font-size:48px;}
        .intro-sub{font-size:15px;}
        .stButton{top:72% !important; width:210px !important;}
    }
    </style>
    """, unsafe_allow_html=True)

    v64 = _video_base64(SPLASH_VIDEO_PATH)
    if v64:
        video_html = f'<video class="intro-video" autoplay muted loop playsinline><source src="data:video/mp4;base64,{v64}" type="video/mp4"></video>'
    else:
        video_html = '<div class="intro-video" style="background:radial-gradient(circle at center,rgba(0,229,184,.18),transparent 45%),linear-gradient(135deg,#020712,#071827);"></div>'

    st.markdown(f"""
    <div class="intro-shell">
        {video_html}
        <div class="intro-overlay"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚗 Park Your Vehicle", key="intro_enter_app", use_container_width=True):
        st.session_state.intro_done = True
        st.session_state.auth_mode = "login"
        st.rerun()


if not st.session_state.intro_done:
    intro_page()
    st.stop()
    
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
            <div style='font-size:11px;color:var(--text2)'>Smart Parking</div>
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
            <div style='background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin:1rem 0'>
              <div style='margin-bottom:1.5rem'>
                <div style='font-weight:700;font-size:14px;color:var(--accent)'>👩‍💻 Sneha Dutta</div>
                <div style='font-size:12px;color:var(--text2);margin-top:4px'>Code and Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>Full-stack development, UI/UX design, and system architecture</div>
              </div>
              
              <div style='margin-bottom:1.5rem'>
                <div style='font-weight:700;font-size:14px;color:var(--accent)'>👩‍💻 Sangita Malakar</div>
                <div style='font-size:12px;color:var(--text2);margin-top:4px'>Code and Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>Backend systems, database design, and code optimization</div>
              </div>
              
              <div>
                <div style='font-weight:700;font-size:14px;color:var(--accent)'>👩‍🎨 Mousumi Haldar</div>
                <div style='font-size:12px;color:var(--text2);margin-top:4px'>Design Expert</div>
                <div style='font-size:11px;color:#5c6278;margin-top:8px'>User interface, visual design, and user experience optimization</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background:rgba(79,124,255,.08);border:1px solid rgba(79,124,255,.25);
                        border-radius:8px;padding:1.25rem;margin-top:1.5rem;font-size:13px;color:var(--accent)'>
            <strong>✨ About SLotX</strong><br><br>
            SLotX is a next-generation smart parking management system designed to revolutionize urban parking. 
            Built with cutting-edge technology, our platform provides real-time slot availability, intelligent 
            booking, advanced analytics, and seamless entry/exit management.
            </div>
            
            <div style='background:linear-gradient(135deg,rgba(0,229,184,.12),rgba(79,124,255,.1));
                        border:1px solid rgba(0,229,184,.35);
                        border-radius:8px;padding:1.25rem;margin-top:1rem;font-size:13px;
                        color:#00E5B8;text-align:center;line-height:1.6'>
            🤖 <strong>Meet XARA</strong> — the intelligent assistant that makes parking effortless with SlotX.
            </div>
            """, unsafe_allow_html=True)
        
        elif sidebar_option == "📞 Contact Us":
            st.markdown("### 📞 Get In Touch")
            
            st.markdown("""
            <div style='background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin:1rem 0'>
              
              <div style='margin-bottom:1.25rem'>
                <div style='font-size:12px;color:var(--text2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px'>📱 Phone Numbers</div>
                <div style='font-size:14px;color:var(--text);margin-bottom:8px;font-weight:500'>+91-8765-432-109</div>
                <div style='font-size:14px;color:var(--text);font-weight:500'>+91-9876-543-210</div>
              </div>
              
              <div style='border-top:1px solid var(--border);padding-top:1.25rem'>
                <div style='font-size:12px;color:var(--text2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px'>✉️ Email</div>
                <div style='font-size:14px;color:var(--accent);word-break:break-all;font-weight:500'>
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
