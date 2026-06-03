"""
ParkSync — Enhanced CSS with animations and new components
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:      #0b0c0f;
    --bg2:     #111318;
    --bg3:     #181b22;
    --bg4:     #1e222c;
    --border:  #2a2f3d;
    --text:    #e8eaf0;
    --text2:   #9aa0b4;
    --accent:  #4f7cff;
    --green:   #22c55e;
    --red:     #ef4444;
    --amber:   #f59e0b;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 10px rgba(34,197,94,.3); }
    50% { box-shadow: 0 0 20px rgba(34,197,94,.6); }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

@keyframes colorShift {
    0% { background: rgba(34,197,94,.08); border-color: #22c55e; }
    50% { background: rgba(34,197,94,.15); border-color: #22c55e; }
    100% { background: rgba(34,197,94,.08); border-color: #22c55e; }
}

* { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: var(--bg) !important;
}

section[data-testid="stSidebar"] {
    background: #111318 !important;
    border-right: 1px solid #2a2f3d !important;
}

.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1200px !important;
}

/* ANIMATIONS */
[data-testid="stMetric"] {
    background: #111318;
    border: 1px solid #2a2f3d;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    animation: slideUp 0.5s ease-out;
}
[data-testid="stMetricLabel"] { color: #9aa0b4 !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="stMetricValue"] { color: #e8eaf0 !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

.stButton > button {
    background: #4f7cff !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton > button:hover { 
    opacity: .85 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(79,124,255,.2) !important;
}
.stButton > button[kind="secondary"] {
    background: #1e222c !important;
    border: 1px solid #2a2f3d !important;
    color: #e8eaf0 !important;
}

/* INPUTS */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTimeInput > div > div > input,
.stDateInput > div > div > input {
    background: #181b22 !important;
    border: 1px solid #2a2f3d !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all .2s !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus,
.stNumberInput > div > div > input:focus,
.stTimeInput > div > div > input:focus {
    border-color: #4f7cff !important;
    box-shadow: 0 0 0 3px rgba(79,124,255,.1) !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border: 1px solid #2a2f3d !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #111318 !important;
    border-bottom: 1px solid #2a2f3d !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #9aa0b4 !important;
    border-radius: 6px 6px 0 0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    color: #4f7cff !important;
    border-bottom: 2px solid #4f7cff !important;
}

/* EXPANDER */
.streamlit-expanderHeader {
    background: #181b22 !important;
    border: 1px solid #2a2f3d !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    transition: all .2s !important;
}
.streamlit-expanderHeader:hover {
    background: #1e222c !important;
    border-color: #4f7cff !important;
}

/* RADIO */
.stRadio label { color: #e8eaf0 !important; }

/* SIDEBAR HEADING */
[data-testid="stSidebarContent"] h1,
[data-testid="stSidebarContent"] h2,
[data-testid="stSidebarContent"] h3 {
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* PAGE HEADINGS */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e8eaf0 !important;
    animation: slideUp 0.5s ease-out;
}

/* DIVIDER */
hr { border-color: #2a2f3d !important; }

/* ALERTS */
.stAlert {
    border-radius: 8px !important;
    border: none !important;
    animation: slideUp 0.3s ease-out !important;
}

/* FORM */
[data-testid="stForm"] {
    background: #111318 !important;
    border: 1px solid #2a2f3d !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

/* UPLOAD */
[data-testid="stFileUploader"] {
    background: #181b22 !important;
    border: 2px dashed #2a2f3d !important;
    border-radius: 12px !important;
}

/* SLOT GRID ANIMATIONS */
.slot-card {
    animation: slideUp 0.4s ease-out;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.slot-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0,0,0,.3);
}

.slot-vacant {
    animation: colorShift 3s ease-in-out infinite;
}

.slot-occupied {
    animation: pulse 2s ease-in-out infinite;
}

/* QR CODE */
.qr-container {
    background: #111318;
    border: 1px solid #2a2f3d;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    animation: slideUp 0.5s ease-out;
}

.qr-code {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    animation: float 3s ease-in-out infinite;
}

/* FLOOR MAP */
.floor-map {
    background: #181b22;
    border: 1px solid #2a2f3d;
    border-radius: 12px;
    padding: 2rem;
    animation: slideUp 0.5s ease-out;
}

.floor-label {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    color: #4f7cff;
    margin-bottom: 1.5rem;
    font-size: 18px;
}

/* REVENUE CHART */
.chart-container {
    background: #111318;
    border: 1px solid #2a2f3d;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* WAITLIST */
.waitlist-item {
    background: #181b22;
    border-left: 3px solid #4f7cff;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    animation: slideUp 0.4s ease-out;
}

.waitlist-position {
    display: inline-block;
    background: #4f7cff;
    color: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    line-height: 32px;
    text-align: center;
    font-weight: 700;
    margin-right: 1rem;
}

/* NOTIFICATIONS */
.notification {
    background: #1e222c;
    border: 1px solid #2a2f3d;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideUp 0.3s ease-out;
}

.notification-unread {
    border-left: 3px solid #4f7cff;
    background: rgba(79,124,255,.05);
}

/* PROFILE CARD */
.profile-card {
    background: #111318;
    border: 1px solid #2a2f3d;
    border-radius: 12px;
    padding: 2rem;
    animation: slideUp 0.5s ease-out;
}

.profile-avatar {
    width: 80px;
    height: 80px;
    background: #4f7cff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 800;
    color: white;
    margin-bottom: 1rem;
}
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

* { font-family: 'DM Sans', sans-serif; }

.stApp { background: #f4f5f7 !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #d1d5e0 !important;
}

.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1200px !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d1d5e0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    animation: slideUp 0.5s ease-out;
}
[data-testid="stMetricLabel"] { font-size: 12px !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

.stButton > button {
    background: #3b6aff !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    opacity: .85 !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="secondary"] {
    background: #e5e8f0 !important;
    border: 1px solid #d1d5e0 !important;
    color: #1a1d27 !important;
}

h1, h2, h3 { font-family: 'Syne', sans-serif !important; animation: slideUp 0.5s ease-out; }

[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #d1d5e0 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

.slot-card {
    animation: slideUp 0.4s ease-out;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.slot-card:hover {
    transform: translateY(-8px);
}
</style>
"""


def apply_theme(dark: bool = True) -> str:
    return DARK_CSS if dark else LIGHT_CSS


def badge_html(text: str, color: str) -> str:
    """
    color: 'green' | 'red' | 'amber' | 'blue'
    """
    colors = {
        "green": ("#22c55e", "rgba(34,197,94,.12)"),
        "red":   ("#ef4444", "rgba(239,68,68,.12)"),
        "amber": ("#f59e0b", "rgba(245,158,11,.12)"),
        "blue":  ("#4f7cff", "rgba(79,124,255,.12)"),
    }
    fg, bg = colors.get(color, colors["blue"])
    return (
        f"<span style='display:inline-block;padding:2px 10px;border-radius:20px;"
        f"font-size:12px;font-weight:500;color:{fg};background:{bg}'>{text}</span>"
    )


def animated_slot_card_html(slot: dict, clickable: bool = False, index: int = 0) -> str:
    """Animated slot card with staggered animation."""
    is_vacant = slot["status"] == "vacant"
    color     = "#22c55e" if is_vacant else "#ef4444"
    bg        = "rgba(34,197,94,.08)" if is_vacant else "rgba(239,68,68,.08)"
    icon      = "🚗" if slot["type"] == "4-wheeler" else "🏍️"
    label     = "Free" if is_vacant else "Taken"
    cursor    = "pointer" if clickable and is_vacant else "default"
    animation = "colorShift 3s ease-in-out infinite" if is_vacant else "pulse 2s ease-in-out infinite"
    delay     = f"{index * 0.05}s"
    
    return (
        f"<div class='slot-card' style='background:{bg};border:1.5px solid {color};border-radius:10px;"
        f"padding:12px 8px;text-align:center;cursor:{cursor};transition:.2s;animation:{animation};animation-delay:{delay}'>"
        f"<div style='font-size:22px'>{icon}</div>"
        f"<div style='font-size:12px;font-weight:700;color:{color};margin-top:4px'>{slot['slot_code']}</div>"
        f"<div style='font-size:10px;color:{color};opacity:.7'>{label}</div>"
        f"</div>"
    )


def rate_card_html(rates: dict) -> str:
    four = rates.get("4-wheeler", 30)
    two  = rates.get("2-wheeler", 10)
    return f"""
<div style='display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0'>
  <div style='flex:1;min-width:150px;background:#111318;border:1px solid #2a2f3d;
              border-radius:12px;padding:1.25rem;text-align:center;animation:slideUp 0.5s ease-out'>
    <div style='font-size:28px;margin-bottom:4px'>🚗</div>
    <div style='font-size:11px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em'>4-Wheeler</div>
    <div style='font-family:Syne,sans-serif;font-size:30px;font-weight:800;color:#f59e0b'>₹{four}</div>
    <div style='font-size:11px;color:#9aa0b4'>per hour</div>
  </div>
  <div style='flex:1;min-width:150px;background:#111318;border:1px solid #2a2f3d;
              border-radius:12px;padding:1.25rem;text-align:center;animation:slideUp 0.6s ease-out'>
    <div style='font-size:28px;margin-bottom:4px'>🏍️</div>
    <div style='font-size:11px;color:#9aa0b4;text-transform:uppercase;letter-spacing:.06em'>2-Wheeler</div>
    <div style='font-family:Syne,sans-serif;font-size:30px;font-weight:800;color:#4f7cff'>₹{two}</div>
    <div style='font-size:11px;color:#9aa0b4'>per hour</div>
  </div>
</div>"""


TIME_SLOTS = [
    ("Morning Peak",  "06:00 – 10:00", "🔴 High Demand"),
    ("Afternoon",     "10:00 – 16:00", "🟡 Moderate"),
    ("Evening Peak",  "16:00 – 21:00", "🔴 High Demand"),
    ("Night",         "21:00 – 06:00", "🟢 Low Demand"),
]

# In styles.py, add this new function:

def get_slotx_logo():
    """Return SLotX logo HTML"""
    return """
    <div style='display:inline-flex;align-items:center;gap:12px'>
        <div style='width:50px;height:50px;background:linear-gradient(135deg,#4f7cff,#22c55e);
                    border-radius:12px;display:flex;align-items:center;justify-content:center;
                    font-family:Syne,sans-serif;font-weight:800;font-size:24px;color:#fff;
                    box-shadow:0 8px 16px rgba(79,124,255,0.3)'>S</div>
        <div>
            <div style='font-family:Syne,sans-serif;font-size:28px;font-weight:800;
                        background:linear-gradient(135deg,#4f7cff,#22c55e);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text'>SLotX</div>
            <div style='font-size:11px;color:#9aa0b4;letter-spacing:1px'>SMART PARKING SYSTEM</div>
        </div>
    </div>
    """
