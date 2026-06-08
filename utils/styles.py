"""
ParkSync — Premium Adaptive UI with Vibrant Colors, Unique Animations & Professional Design
Works flawlessly in both dark and light mode OS settings with sophisticated micro-interactions
"""

ADAPTIVE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

/* ════════════════════════════════════════════════════════════════ */
/* HIDE STREAMLIT CHROME                                            */
/* ════════════════════════════════════════════════════════════════ */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="StyledFullScreenButton"],
button[title="View fullscreen"],
button[title="Exit fullscreen"] { display: none !important; }
button[data-testid="stToolbarButtonLangOptions"],
button[data-testid="stToolbarButtonMoreOptions"],
[data-testid="stToolbar"] { display: none !important; }
button[title*="menu"],button[title*="settings"],
button[title*="More options"],button[aria-label*="menu"],
button[aria-label*="More options"] { display: none !important; }

/* ════════════════════════════════════════════════════════════════ */
/* COLOR VARIABLES — LIGHT MODE (DEFAULT)                           */
/* ════════════════════════════════════════════════════════════════ */
:root {
    --bg:              #f8f9fc;
    --bg2:             #ffffff;
    --bg3:             #f0f3fa;
    --bg4:             #e8ecf6;
    --border:          #d5dce8;
    --text:            #0f1419;
    --text2:           #5a6375;
    --text3:           #8a92a3;
    
    /* ── Primary Colors ── */
    --accent:          #4f7cff;      /* Electric Blue */
    --accent-light:    #6b8fff;
    --accent-dark:     #3a5fd4;
    
    /* ── Accent Colors ── */
    --green:           #10b981;      /* Emerald */
    --green-light:     #34d399;
    --purple:          #a855f7;      /* Royal Purple */
    --pink:            #ec4899;      /* Hot Pink */
    --orange:          #f97316;      /* Vibrant Orange */
    --cyan:            #06b6d4;      /* Cyan */
    --amber:           #f59e0b;      /* Warm Amber */
    --red:             #ef4444;      /* Bright Red */
    
    /* ── Shadows & Effects ── */
    --shadow-sm:       0 2px 8px rgba(0,0,0,0.08);
    --shadow-md:       0 4px 16px rgba(0,0,0,0.12);
    --shadow-lg:       0 12px 32px rgba(0,0,0,0.16);
    --shadow-hover:    0 16px 40px rgba(79,124,255,0.18);
    
    --glow-blue:       0 0 24px rgba(79,124,255,0.35);
    --glow-green:      0 0 20px rgba(16,185,129,0.3);
    --glow-purple:     0 0 24px rgba(168,85,247,0.3);
}

/* ════════════════════════════════════════════════════════════════ */
/* COLOR VARIABLES — DARK MODE (via @media)                        */
/* ════════════════════════════════════════════════════════════════ */
@media (prefers-color-scheme: dark) {
    :root {
        --bg:              #0d0f14;
        --bg2:             #131720;
        --bg3:             #1a1f2e;
        --bg4:             #232b3e;
        --border:          #3a4454;
        --text:            #e8eef8;
        --text2:           #a1aac0;
        --text3:           #7a8399;
        
        --accent:          #5a8fff;
        --accent-light:    #7ba3ff;
        --accent-dark:     #4073e6;
        
        --green:           #22c55e;
        --green-light:     #4ade80;
        --purple:          #c084fc;
        --pink:            #f472b6;
        --orange:          #fb923c;
        --cyan:            #22d3ee;
        --amber:           #fbbf24;
        --red:             #f87171;
        
        --shadow-sm:       0 2px 12px rgba(0,0,0,0.4);
        --shadow-md:       0 4px 24px rgba(0,0,0,0.5);
        --shadow-lg:       0 12px 40px rgba(0,0,0,0.6);
        --shadow-hover:    0 16px 48px rgba(79,124,255,0.25);
        
        --glow-blue:       0 0 30px rgba(90,143,255,0.4);
        --glow-green:      0 0 24px rgba(34,197,95,0.35);
        --glow-purple:     0 0 28px rgba(192,132,252,0.35);
    }
}

/* ════════════════════════════════════════════════════════════════ */
/* ANIMATIONS — Advanced & Sophisticated                            */
/* ════════════════════════════════════════════════════════════════ */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.65; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-8px); }
}

@keyframes float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50%       { transform: translateY(-8px) rotate(2deg); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 12px rgba(79,124,255,.3), inset 0 0 8px rgba(79,124,255,.1); }
    50%       { box-shadow: 0 0 24px rgba(79,124,255,.6), inset 0 0 12px rgba(79,124,255,.2); }
}

@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes borderFlow {
    0%   { border-image-slice: 1; border-image-source: linear-gradient(90deg, var(--accent), var(--purple), var(--pink)); }
    100% { border-image-slice: 1; border-image-source: linear-gradient(90deg, var(--pink), var(--accent), var(--purple)); }
}

@keyframes colorShift {
    0%   { background: rgba(16,185,129,.12); border-color: var(--green); }
    50%  { background: rgba(16,185,129,.2); border-color: var(--green-light); }
    100% { background: rgba(16,185,129,.12); border-color: var(--green); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.92); }
    to   { opacity: 1; transform: scale(1); }
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

/* ════════════════════════════════════════════════════════════════ */
/* BASE STYLES                                                      */
/* ════════════════════════════════════════════════════════════════ */
* { 
    font-family: 'Inter', 'DM Sans', sans-serif;
    box-sizing: border-box;
}

.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    transition: background 0.4s, color 0.4s;
}

body { background: var(--bg); }

section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    animation: slideInLeft 0.5s ease-out;
}

.block-container {
    padding: 1.75rem 2.25rem !important;
    max-width: 1280px !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* METRICS — Colorful & Animated                                    */
/* ════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.04) 100%) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.3rem 1.6rem !important;
    box-shadow: var(--shadow-md) !important;
    animation: slideUp 0.5s ease-out;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    position: relative;
    overflow: hidden;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 100px; height: 100px;
    background: radial-gradient(circle, rgba(79,124,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: var(--shadow-hover) !important;
    border-color: var(--accent) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text2) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 28px !important;
    background: linear-gradient(135deg, var(--accent), var(--purple)) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* BUTTONS — Premium Interactive                                    */
/* ════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--purple) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 650 !important;
    padding: 0.65rem 1.5rem !important;
    font-size: 13px !important;
    letter-spacing: 0.01em !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    box-shadow: 0 4px 16px rgba(79,124,255,0.35), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.15) 50%, transparent 70%);
    transform: translateX(-100%);
    transition: transform 0.5s ease-out;
}

.stButton > button:hover::before { transform: translateX(100%); }

.stButton > button:hover {
    transform: translateY(-4px) scale(1.05) !important;
    box-shadow: 0 12px 28px rgba(79,124,255,0.45), inset 0 1px 0 rgba(255,255,255,0.3) !important;
}

.stButton > button:active { transform: translateY(-1px) !important; }

.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, var(--bg3) 0%, var(--bg4) 100%) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, var(--accent) 0%, var(--purple) 100%) !important;
    color: white !important;
    border-color: var(--accent) !important;
    box-shadow: var(--glow-blue) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* INPUTS — Modern & Colorful                                       */
/* ════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTimeInput > div > div > input,
.stDateInput > div > div > input {
    background: var(--bg3) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s !important;
    font-size: 14px !important;
}

.stTextInput > div > div > input::placeholder,
.stNumberInput > div > div > input::placeholder {
    color: var(--text3) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(79,124,255,0.15), inset 0 2px 4px rgba(0,0,0,0.05) !important;
    background: linear-gradient(135deg, rgba(79,124,255,0.03), rgba(168,85,247,0.03)) !important;
}

.stSelectbox > div > div {
    background: var(--bg3) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    transition: all 0.3s !important;
}

.stSelectbox > div > div:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(79,124,255,0.15) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* DATAFRAME — Vibrant Tables                                       */
/* ════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-md) !important;
    animation: slideUp 0.5s ease-out;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: linear-gradient(90deg, rgba(79,124,255,0.08), rgba(168,85,247,0.05)) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* TABS — Animated & Modern                                         */
/* ════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 8px !important;
    padding-bottom: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text2) !important;
    border-radius: 10px 10px 0 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 550 !important;
    font-size: 13px !important;
    transition: all 0.3s !important;
    padding: 10px 16px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent) !important;
    background: rgba(79,124,255,0.08) !important;
}

.stTabs [aria-selected="true"] {
    color: white !important;
    background: linear-gradient(135deg, var(--accent), var(--purple)) !important;
    border-bottom: none !important;
    box-shadow: var(--glow-blue) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* EXPANDER — Smooth Reveal                                         */
/* ════════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, var(--bg2), rgba(79,124,255,0.05)) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    transition: all 0.3s !important;
    font-weight: 550 !important;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, var(--bg2), rgba(79,124,255,0.1)) !important;
    border-color: var(--accent) !important;
    transform: translateX(4px);
}

.streamlit-expanderContent { animation: slideUp 0.4s ease-out; }

/* ════════════════════════════════════════════════════════════════ */
/* HEADINGS & TEXT — Hierarchy & Color                              */
/* ════════════════════════════════════════════════════════════════ */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 36px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, var(--accent), var(--purple), var(--pink)) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: slideUp 0.5s ease-out;
    letter-spacing: -0.02em;
}

h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    animation: slideUp 0.5s ease-out;
}

h3 {
    font-family: 'Syne', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

p, li, label { color: var(--text) !important; }

/* ════════════════════════════════════════════════════════════════ */
/* DIVIDER & HR                                                     */
/* ════════════════════════════════════════════════════════════════ */
hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, var(--accent), transparent) !important;
    animation: slideInRight 0.6s ease-out !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* ALERTS & MESSAGES                                                */
/* ════════════════════════════════════════════════════════════════ */
.stAlert {
    border-radius: 14px !important;
    border: none !important;
    animation: slideUp 0.4s ease-out !important;
    backdrop-filter: blur(10px);
}

/* Success */
[data-testid="stAlert"]:has(.st-bx) {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.06)) !important;
    border: 1.5px solid rgba(16,185,129,0.3) !important;
    box-shadow: var(--glow-green) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* FORMS                                                             */
/* ════════════════════════════════════════════════════════════════ */
[data-testid="stForm"] {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.04) 100%) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    box-shadow: var(--shadow-lg) !important;
    animation: slideUp 0.5s ease-out;
}

[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, var(--bg3) 0%, rgba(168,85,247,0.05) 100%) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    transition: all 0.3s !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: linear-gradient(135deg, var(--bg3) 0%, rgba(79,124,255,0.1) 100%) !important;
}

/* ════════════════════════════════════════════════════════════════ */
/* SLOT CARDS — Vibrant Status Indicators                           */
/* ════════════════════════════════════════════════════════════════ */
.slot-card {
    animation: slideUp 0.4s ease-out;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
    border-radius: 12px;
    position: relative;
    overflow: hidden;
}

.slot-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

.slot-card:hover::before { opacity: 1; }

.slot-card:hover {
    transform: translateY(-10px) scale(1.08);
    box-shadow: 0 12px 32px rgba(0,0,0,0.2);
}

/* ════════════════════════════════════════════════════════════════ */
/* QR CODE CONTAINER                                                */
/* ════════════════════════════════════════════════════════════════ */
.qr-container {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.08) 100%);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    animation: slideUp 0.5s ease-out;
    box-shadow: var(--shadow-lg);
}

.qr-code {
    background: white;
    padding: 1.25rem;
    border-radius: 12px;
    margin: 1.5rem auto;
    animation: float 3s ease-in-out infinite;
    box-shadow: 0 8px 24px rgba(79,124,255,0.2);
}

/* ════════════════════════════════════════════════════════════════ */
/* FLOOR MAP                                                        */
/* ════════════════════════════════════════════════════════════════ */
.floor-map {
    background: linear-gradient(135deg, var(--bg3) 0%, rgba(168,85,247,0.08) 100%);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    animation: slideUp 0.5s ease-out;
    box-shadow: var(--shadow-md);
}

.floor-label {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
    font-size: 20px;
}

/* ════════════════════════════════════════════════════════════════ */
/* CHARTS & ANALYTICS                                               */
/* ════════════════════════════════════════════════════════════════ */
.chart-container {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.06) 100%);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
    animation: slideUp 0.5s ease-out;
}

/* ════════════════════════════════════════════════════════════════ */
/* WAITLIST & NOTIFICATIONS                                         */
/* ════════════════════════════════════════════════════════════════ */
.waitlist-item {
    background: linear-gradient(135deg, var(--bg3) 0%, rgba(79,124,255,0.06) 100%);
    border-left: 4px solid var(--accent);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.9rem;
    animation: slideUp 0.4s ease-out;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.waitlist-item::before {
    content: '';
    position: absolute;
    right: -50%;
    top: -50%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(79,124,255,0.1), transparent);
    pointer-events: none;
}

.waitlist-item:hover {
    transform: translateX(6px);
    box-shadow: var(--glow-blue);
}

.waitlist-position {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), var(--purple));
    color: white;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    line-height: 36px;
    text-align: center;
    font-weight: 800;
    margin-right: 1rem;
    box-shadow: 0 4px 12px rgba(79,124,255,0.4);
    animation: bounce 2s ease-in-out infinite;
}

.notification {
    background: linear-gradient(135deg, var(--bg3) 0%, rgba(168,85,247,0.06) 100%);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem;
    margin-bottom: 0.7rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideUp 0.3s ease-out;
    transition: all 0.3s;
}

.notification:hover {
    transform: translateX(4px);
    box-shadow: var(--glow-blue);
}

.notification-unread {
    border-left: 4px solid var(--accent);
    background: linear-gradient(135deg, rgba(79,124,255,0.12), rgba(79,124,255,0.06)) !important;
    box-shadow: var(--glow-blue);
}

/* ════════════════════════════════════════════════════════════════ */
/* PROFILE CARD                                                     */
/* ════════════════════════════════════════════════════════════════ */
.profile-card {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.08) 100%);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 2.2rem;
    animation: slideUp 0.5s ease-out;
    box-shadow: var(--shadow-lg);
}

.profile-avatar {
    width: 90px;
    height: 90px;
    background: linear-gradient(135deg, var(--accent), var(--purple), var(--pink));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 800;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 24px rgba(79,124,255,0.4);
    position: relative;
    animation: float 3s ease-in-out infinite;
}

.profile-avatar::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--purple), var(--pink));
    opacity: 0.2;
    animation: rotate 4s linear infinite;
    z-index: -1;
}

/* ════════════════════════════════════════════════════════════════ */
/* RATE CARD                                                        */
/* ════════════════════════════════════════════════════════════════ */
.rate-card {
    background: linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.08) 100%);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem;
    text-align: center;
    box-shadow: var(--shadow-md);
    animation: slideUp 0.5s ease-out;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
    position: relative;
    overflow: hidden;
}

.rate-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.05), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

.rate-card:hover::before { opacity: 1; }

.rate-card:hover {
    transform: translateY(-8px) scale(1.04);
    box-shadow: var(--shadow-hover);
    border-color: var(--accent);
}

.rate-icon {
    font-size: 36px;
    margin-bottom: 8px;
    animation: bounce 2s ease-in-out infinite;
}

.rate-value {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--orange), var(--amber));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ════════════════════════════════════════════════════════════════ */
/* SECTION HEADER ANIMATION                                         */
/* ════════════════════════════════════════════════════════════════ */
.section-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent), var(--purple));
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: var(--glow-blue);
    animation: float 3s ease-in-out infinite;
}

/* ════════════════════════════════════════════════════════════════ */
/* GRADIENT MESH BACKGROUND (optional for special sections)         */
/* ════════════════════════════════════════════════════════════════ */
.gradient-bg {
    background: linear-gradient(
        135deg,
        rgba(79,124,255,0.08),
        rgba(168,85,247,0.06),
        rgba(236,72,153,0.04)
    );
    border-radius: 16px;
    padding: 2rem;
    animation: slideUp 0.5s ease-out;
}

/* ════════════════════════════════════════════════════════════════ */
/* MISC UTILITIES                                                   */
/* ════════════════════════════════════════════════════════════════ */
[data-testid="stSidebarContent"] h1,
[data-testid="stSidebarContent"] h2,
[data-testid="stSidebarContent"] h3 {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 12px !important;
}

.stMarkdown p { color: var(--text) !important; }

/* ════════════════════════════════════════════════════════════════ */
/* RESPONSIVE ADJUSTMENTS                                           */
/* ════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1.25rem 1.5rem !important; }
    h1 { font-size: 28px !important; }
    .profile-avatar { width: 70px; height: 70px; }
}
</style>
"""

# Keep legacy variables for compatibility
DARK_CSS = ADAPTIVE_CSS
LIGHT_CSS = ADAPTIVE_CSS


def apply_theme(dark: bool = True) -> str:
    """Return adaptive CSS that works in both light and dark modes."""
    return ADAPTIVE_CSS


def badge_html(text: str, color: str) -> str:
    """Colorful badge with gradient background."""
    colors = {
        "green":  ("var(--green)",    "rgba(16,185,129,.15)", "1.5px solid rgba(16,185,129,.4)"),
        "red":    ("var(--red)",      "rgba(239,68,68,.15)",   "1.5px solid rgba(239,68,68,.4)"),
        "amber":  ("var(--amber)",    "rgba(245,158,11,.15)",  "1.5px solid rgba(245,158,11,.4)"),
        "blue":   ("var(--accent)",   "rgba(79,124,255,.15)",  "1.5px solid rgba(79,124,255,.4)"),
        "purple": ("var(--purple)",   "rgba(168,85,247,.15)",  "1.5px solid rgba(168,85,247,.4)"),
    }
    fg, bg, border = colors.get(color, colors["blue"])
    return (
        f"<span style='display:inline-block;padding:4px 14px;border-radius:20px;"
        f"font-size:12px;font-weight:650;color:{fg};background:{bg};border:{border};"
        f"animation:slideUp 0.4s ease-out'>{text}</span>"
    )


def animated_slot_card_html(slot: dict, clickable: bool = False, index: int = 0) -> str:
    """Animated slot card with vibrant status colors."""
    is_vacant = slot["status"] == "vacant"
    color_var  = "var(--green)" if is_vacant else "var(--red)"
    bg_grad    = "linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.06))" if is_vacant else "linear-gradient(135deg, rgba(239,68,68,0.12), rgba(239,68,68,0.06))"
    icon       = "🚗" if slot["type"] == "4-wheeler" else "🏍️"
    label      = "Free" if is_vacant else "Taken"
    cursor     = "pointer" if clickable and is_vacant else "default"
    delay      = f"{index * 0.05}s"

    return (
        f"<div class='slot-card' style='"
        f"background:{bg_grad};"
        f"border:2px solid {color_var};"
        f"border-radius:12px;padding:14px 10px;text-align:center;"
        f"cursor:{cursor};"
        f"animation:colorShift 3s ease-in-out infinite;"
        f"animation-delay:{delay};"
        f"transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1)'>"
        f"<div style='font-size:28px;margin-bottom:6px;animation:bounce 2s ease-in-out infinite'>{icon}</div>"
        f"<div style='font-size:13px;font-weight:750;color:{color_var};margin-top:4px'>{slot['slot_code']}</div>"
        f"<div style='font-size:11px;color:{color_var};opacity:.8;font-weight:500'>{label}</div>"
        f"</div>"
    )


def rate_card_html(rates: dict) -> str:
    """Vibrant, gradient-enhanced rate cards."""
    four = rates.get("4-wheeler", 30)
    two  = rates.get("2-wheeler", 10)
    return f"""
<div style='display:flex;gap:1.5rem;flex-wrap:wrap;margin:1.5rem 0;animation:slideUp 0.5s ease-out'>
  <div class='rate-card' style='flex:1;min-width:180px;background:linear-gradient(135deg, rgba(249,115,22,0.1), rgba(245,158,11,0.05));border:1.5px solid rgba(249,115,22,0.3);box-shadow:0 0 20px rgba(249,115,22,0.15)'>
    <div class='rate-icon'>🚗</div>
    <div style='font-size:12px;color:var(--text2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;font-weight:650'>4-Wheeler</div>
    <div style='font-family:Syne,sans-serif;font-size:36px;font-weight:800;background:linear-gradient(135deg, var(--orange), var(--amber));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px'>₹{four}</div>
    <div style='font-size:12px;color:var(--text3);font-weight:500'>per hour</div>
  </div>
  <div class='rate-card' style='flex:1;min-width:180px;background:linear-gradient(135deg, rgba(79,124,255,0.1), rgba(168,85,247,0.05));border:1.5px solid rgba(79,124,255,0.3);box-shadow:0 0 24px rgba(79,124,255,0.2)'>
    <div class='rate-icon'>🏍️</div>
    <div style='font-size:12px;color:var(--text2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;font-weight:650'>2-Wheeler</div>
    <div style='font-family:Syne,sans-serif;font-size:36px;font-weight:800;background:linear-gradient(135deg, var(--accent), var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px'>₹{two}</div>
    <div style='font-size:12px;color:var(--text3);font-weight:500'>per hour</div>
  </div>
</div>"""


TIME_SLOTS = [
    ("Morning Peak",  "06:00 – 10:00", "🔴 High Demand"),
    ("Afternoon",     "10:00 – 16:00", "🟡 Moderate"),
    ("Evening Peak",  "16:00 – 21:00", "🔴 High Demand"),
    ("Night",         "21:00 – 06:00", "🟢 Low Demand"),
]


def get_slotx_logo():
    """Animated SLotX logo with vibrant gradient."""
    return """
    <div style='display:inline-flex;align-items:center;gap:14px;animation:slideInLeft 0.6s ease-out'>
        <div class='section-icon' style='animation:float 3s ease-in-out infinite'>S</div>
        <div>
            <div style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;
                        background:linear-gradient(135deg,#4f7cff,#22c55e,#a855f7);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;letter-spacing:-0.02em;'>SLotX</div>
            <div style='font-size:11px;color:var(--text2);letter-spacing:1.5px;text-transform:uppercase;font-weight:600'>SMART PARKING SYSTEM</div>
        </div>
    </div>
    """


def section_header_html(icon: str, title: str, subtitle: str) -> str:
    """Premium animated section header with gradient icon."""
    return f"""
<div style='display:flex;align-items:center;gap:16px;margin-bottom:2rem;
            animation:slideUp 0.5s ease-out'>
  <div class='section-icon'>{icon}</div>
  <div>
    <h1 style='margin:0;font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:var(--text)'>{title}</h1>
    <div style='font-size:14px;color:var(--text2);font-weight:500;margin-top:4px'>{subtitle}</div>
  </div>
</div>
"""


def card_html(content: str, extra_style: str = "") -> str:
    """Premium gradient card wrapper."""
    return (
        f"<div style='background:linear-gradient(135deg, var(--bg2) 0%, rgba(79,124,255,0.06) 100%);"
        f"border:1.5px solid var(--border);border-radius:16px;"
        f"padding:1.8rem;box-shadow:var(--shadow-lg);animation:slideUp 0.5s ease-out;{extra_style}'>"
        f"{content}</div>"
    )
