"""
SLotX Chatbot Utilities - FIXED VERSION
Provides intelligent responses for parking-related queries
Floating widget now works properly across all pages
"""

import json
import logging
import random
from datetime import datetime

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import streamlit.components.v1 as components
except ImportError:
    components = None

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None


logger = logging.getLogger("slotx.chatbot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_handler)
    logger.propagate = False


SYSTEM_PROMPT = (
    "You are XARA, the intelligent assistant for SLotX, a smart parking management system. "
    "Answer user questions about booking parking slots, payments, QR code entry/exit, real-time "
    "slot availability, waitlists, accounts, pricing, and support. Keep answers concise, friendly, "
    "and specific to the SLotX parking experience. If a question is unrelated to parking, politely "
    "redirect the user to parking-related topics."
)


class ParkingChatbot:
    """Smart chatbot for SLotX parking management system"""

    def __init__(self):
        self.azure_client, self.azure_deployment = self._init_azure_client()
        self.knowledge_base = {
            "booking": {
                "keywords": ["book", "reserve", "slot", "parking space"],
                "responses": [
                    "You can book a parking slot directly from your dashboard. Click on 'Available Slots' and select your preferred time and location.",
                    "To book a slot: 1) View available slots on the map 2) Select your preferred slot 3) Choose time duration 4) Complete payment. Your booking is confirmed!",
                    "Booking is easy! Just navigate to the booking section, select your preferred parking slot, and proceed to payment. Your QR code will be generated immediately."
                ]
            },
            "payment": {
                "keywords": ["pay", "payment", "price", "cost", "fee", "credit card", "debit card"],
                "responses": [
                    "We accept both credit and debit cards for payments. Payment is secure and processed instantly.",
                    "Payment can be made using your credit or debit card. Check your demo payment options in the payments folder for test card details.",
                    "All payments are processed securely. You'll receive a receipt immediately after successful payment."
                ]
            },
            "qr": {
                "keywords": ["qr code", "qr", "entry", "exit", "scan"],
                "responses": [
                    "Your QR code is generated automatically after booking. Show it at the parking entry gate or scan it for seamless entry/exit.",
                    "The QR code is your digital parking ticket. It contains all your booking details and is required for entry and exit.",
                    "Simply present your QR code at the gate. The system will validate your booking and allow you to enter. Same process for exit!"
                ]
            },
            "slots": {
                "keywords": ["slot", "availability", "available", "free", "occupied", "vacant"],
                "responses": [
                    "You can view all available parking slots in real-time on the map in your dashboard. Green indicates available, red indicates occupied.",
                    "Real-time slot availability is updated continuously. Check the availability map to find the perfect spot for your vehicle.",
                    "Available slots are displayed with color coding for easy identification. Use filters to find slots matching your preferences."
                ]
            },
            "waitlist": {
                "keywords": ["waitlist", "waiting", "queue", "notify", "availability alert"],
                "responses": [
                    "If all slots are full, you can join the waitlist. You'll be notified automatically when a slot becomes available.",
                    "The waitlist feature helps when parking is full. You'll receive a notification as soon as a slot is free in your selected location.",
                    "Can't find a slot? Join the waitlist! The system will alert you when a suitable slot becomes available."
                ]
            },
            "account": {
                "keywords": ["account", "profile", "user", "registration", "sign up", "login"],
                "responses": [
                    "To create an account, click on 'Create Account' on the login page and fill in your details. You'll get instant access!",
                    "Visit the registration page to create your account. You'll need to provide your name, email, phone, and create a password.",
                    "Already have an account? Sign in with your username and password. New users can register in seconds!"
                ]
            },
            "admin": {
                "keywords": ["admin", "manage", "analytics", "reports", "dashboard"],
                "responses": [
                    "Admin features include real-time slot management, analytics, user management, and detailed reports. Sign in as admin to access.",
                    "Admins can view comprehensive analytics, manage parking slots, track payments, and generate detailed reports.",
                    "The admin dashboard provides full control over parking operations, including occupancy rates, revenue tracking, and user management."
                ]
            },
            "location": {
                "keywords": ["location", "address", "map", "area", "zone"],
                "responses": [
                    "SLotX operates in multiple locations. Use the map view to select your preferred parking area.",
                    "You can view all parking locations on the interactive map. Each location shows real-time availability and pricing.",
                    "Browse different parking zones on the map and book slots based on your destination."
                ]
            },
            "pricing": {
                "keywords": ["price", "rate", "hourly", "daily", "monthly", "cost", "charge"],
                "responses": [
                    "Pricing varies by location and time. Check the rates displayed when you select a parking slot.",
                    "Rates are displayed clearly before you book. You can see hourly, daily, and monthly pricing options.",
                    "SLotX offers competitive pricing with transparent rate cards. No hidden charges!"
                ]
            },
            "contact": {
                "keywords": ["contact", "support", "help", "phone", "email", "customer service"],
                "responses": [
                    "Contact us at support@slotx.in or call +91-8765-432-109. Our team is available Monday-Friday, 9 AM - 6 PM.",
                    "For support, reach out via email (support@slotx.in) or phone (+91-9876-543-210). We respond within 2 hours.",
                    "Need help? Visit the Contact Us section in the sidebar or email support@slotx.in with your query."
                ]
            },
            "hours": {
                "keywords": ["hours", "timing", "open", "close", "business hours"],
                "responses": [
                    "SLotX support is available: Monday-Friday 9 AM-6 PM, Saturday 9 AM-2 PM. Parking facilities are 24/7.",
                    "Parking is available round the clock. Our support team operates during business hours.",
                    "Parking slots are available 24/7, but our customer support team works Monday-Friday 9-6 and Saturday 9-2."
                ]
            }
        }

    @staticmethod
    def _init_azure_client():
        """Set up the Azure OpenAI (Microsoft Copilot) client from Streamlit secrets, if configured"""
        if AzureOpenAI is None:
            logger.info("Azure OpenAI SDK not installed - chatbot will use rule-based KB only")
            return None, None
        if st is None:
            logger.info("Streamlit not available - chatbot will use rule-based KB only")
            return None, None

        try:
            endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
            api_key = st.secrets["AZURE_OPENAI_API_KEY"]
            deployment = st.secrets["AZURE_OPENAI_DEPLOYMENT"]
            api_version = st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        except Exception:
            logger.info("Azure OpenAI secrets not configured - chatbot will use rule-based KB only")
            return None, None

        try:
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
            )
            logger.info("Azure OpenAI client initialized (deployment=%s) - Copilot responses enabled", deployment)
            return client, deployment
        except Exception:
            logger.exception("Failed to initialize Azure OpenAI client - chatbot will use rule-based KB only")
            return None, None

    def _get_copilot_response(self, user_message):
        """Ask Microsoft Copilot (Azure OpenAI) for a response. Returns None on any failure."""
        if not self.azure_client:
            return None

        try:
            completion = self.azure_client.chat.completions.create(
                model=self.azure_deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=300,
                temperature=0.5,
            )
            logger.info("Response served by Azure OpenAI (deployment=%s)", self.azure_deployment)
            return completion.choices[0].message.content.strip()
        except Exception:
            logger.exception("Azure OpenAI call failed - falling back to rule-based KB")
            return None

    def get_response(self, user_message):
        """Generate appropriate response based on user query"""
        copilot_response = self._get_copilot_response(user_message)
        if copilot_response:
            return copilot_response

        logger.info("Response served by rule-based KB")
        return self._get_rule_based_response(user_message)

    def _get_rule_based_response(self, user_message):
        """Fallback keyword-matching response when Copilot is unavailable"""
        user_message = user_message.lower().strip()

        # Check for exact matches in knowledge base
        for category, content in self.knowledge_base.items():
            for keyword in content["keywords"]:
                if keyword in user_message:
                    return random.choice(content["responses"])

        # Default responses for common queries
        if any(word in user_message for word in ["hi", "hello", "hey", "greetings"]):
            return "👋 Hello! I'm XARA, your intelligent SlotX parking assistant. How can I help you today? You can ask me about booking, payments, slots, or any parking-related queries!"

        if any(word in user_message for word in ["thank", "thanks", "appreciate"]):
            return "You're welcome! Is there anything else I can help you with regarding your parking experience?"

        if any(word in user_message for word in ["how", "what", "where", "when", "why"]):
            return "That's a great question! I'd be happy to help. Could you be more specific? Ask me about: booking slots, payments, QR codes, availability, pricing, or account details."

        # Fallback response
        return "I'm here to help with parking-related questions. Try asking about booking slots, payments, real-time availability, QR codes, waitlists, or pricing. What would you like to know?"

    def format_conversation(self, user_message, bot_response):
        """Format conversation for display"""
        return {
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }


def create_chatbot():
    """Factory function to create chatbot instance"""
    return ParkingChatbot()


DEFAULT_XARA_GREETING = (
    "👋 Hi! I'm XARA — your intelligent parking assistant from SlotX. "
    "Ask me anything about booking, payments, slots, or QR codes!"
)


def render_xara_widget():
    """
    Render the XARA floating widget on the current page, wired to ParkingChatbot
    (Azure OpenAI Copilot with rule-based KB fallback).
    When Azure OpenAI is NOT configured the widget responds instantly from an
    embedded JavaScript knowledge base — no Python round-trip required.
    Call this once near the top of every page script.
    """
    if st is None or components is None:
        return

    if "xara_messages" not in st.session_state:
        st.session_state.xara_messages = [{"role": "bot", "content": DEFAULT_XARA_GREETING}]
    if "xara_instance" not in st.session_state:
        st.session_state.xara_instance = create_chatbot()

    azure_available = st.session_state.xara_instance.azure_client is not None

    if azure_available:
        # Hide the bridge form completely via robust CSS selectors
        st.markdown(
            """
            <style>
            div[data-testid="stForm"]:has(.st-key-xara_bridge_input),
            div[data-testid="stForm"]:has(input[aria-label="XARA bridge"]),
            div[data-testid="element-container"]:has(.st-key-xara_bridge_input),
            .element-container:has(.st-key-xara_bridge_input),
            .st-key-xara_bridge_form,
            .st-key-xara_bridge_input {
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                visibility: hidden !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("xara_bridge_form", clear_on_submit=True):
            bridge_message = st.text_input(
                "XARA bridge", key="xara_bridge_input", label_visibility="collapsed"
            )
            bridge_submitted = st.form_submit_button("Send")

        if bridge_submitted and bridge_message:
            st.session_state.xara_messages.append({"role": "user", "content": bridge_message})
            response = st.session_state.xara_instance.get_response(bridge_message)
            st.session_state.xara_messages.append({"role": "bot", "content": response})

    components.html(
        get_xara_floating_widget(st.session_state.xara_messages, azure_available),
        height=0,
        scrolling=False,
    )


def get_xara_floating_widget(messages=None, azure_available=False):
    """Return HTML/JS that injects the XARA floating chatbot into the parent Streamlit document.

    When *azure_available* is False (the common case) the widget answers immediately
    from an embedded JS knowledge base — no Python round-trip is needed so the chat
    never hangs.  When *azure_available* is True the JS submits to the hidden
    Streamlit bridge form and waits for the Python-side Azure OpenAI response.
    """
    messages_json = json.dumps(messages or [])
    azure_flag = "true" if azure_available else "false"
    html = """
<div id="xara-container">
    <!-- Floating Button -->
    <button id="xara-button" type="button">
        <span id="xara-badge">1</span>
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="3" width="20" height="16" rx="5" fill="#020712" opacity=".85"/>
            <circle cx="10" cy="11" r="2.2" fill="#00E5B8"/>
            <circle cx="18" cy="11" r="2.2" fill="#00E5B8"/>
            <rect x="10" y="17" width="8" height="2.5" rx="1.25" fill="#00E5B8" opacity=".8"/>
            <line x1="14" y1="3" x2="14" y2="1" stroke="#00E5B8" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="14" cy="1" r="1" fill="#4f7cff"/>
            <rect x="9" y="19" width="4" height="6" rx="2" fill="#020712" opacity=".7" stroke="#00E5B8" stroke-width="1"/>
            <rect x="15" y="19" width="4" height="6" rx="2" fill="#020712" opacity=".7" stroke="#00E5B8" stroke-width="1"/>
            <text x="11.5" y="14.5" font-family="Arial Black,sans-serif" font-weight="900" font-size="8" fill="#fff">X</text>
        </svg>
    </button>

    <!-- Chat Panel -->
    <div id="xara-panel">
        <div id="xara-header">
            <div id="xara-avatar">🅿</div>
            <div id="xara-info">
                <div id="xara-name">XARA</div>
                <div id="xara-status"><span id="xara-dot"></span>Online · SlotX Assistant</div>
            </div>
            <button id="xara-reset" type="button" title="Clear Chat History">🗑️</button>
            <button id="xara-close" type="button">✕</button>
        </div>

        <div id="xara-messages"></div>

        <div id="xara-chips">
            <span class="xara-chip" data-question="How do I book a slot?">📍 Book a slot</span>
            <span class="xara-chip" data-question="What payment methods?">💳 Payment</span>
            <span class="xara-chip" data-question="How does the QR code work?">🎯 QR code</span>
        </div>

        <div id="xara-input-row">
            <input id="xara-input" type="text" placeholder="Ask XARA anything..." />
            <button id="xara-send" type="button">➤</button>
        </div>

        <div id="xara-powered-by">
            <span id="xara-pb-label">Powered by</span>
            <span class="xara-pb-badge">
                <svg class="xara-pb-icon" viewBox="0 0 1322.9 1147.5" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path fill="#0078D4" d="m711.19 265.2c-27.333 0-46.933 3.07-58.8 9.33 27.067-80.267 47.6-210.13 168-210.13 114.93 0 108.4 138.27 157.87 200.8zm107.33 112.93c-35.467 125.2-70 251.2-110.13 375.33-12.133 36.4-45.733 61.6-84 61.6h-136.27c9.3333-14 16.8-28.933 21.467-45.733 35.467-125.07 70-251.07 110.13-375.33 12.133-36.4 45.733-61.6 84-61.6h136.27c-9.3333 14-16.8 28.934-21.467 45.734m-316.13 704.8c-114.93 0-108.4-138.13-157.87-200.67h267.07c27.467 0 47.067-3.07 58.8-9.33-27.067 80.266-47.6 210-168 210m777.47-758.93h0.93c-32.667-38.266-82.267-57.866-146.67-57.866h-36.4c-34.533-2.8-65.333-26.134-76.533-58.8l-36.4-103.6c-21.463-61.737-80.263-103.74-145.73-103.74h-475.07c-175.6 0-251.2 225.07-292.27 361.33-38.267 127.07-126 341.73-24.267 462.13 46.667 55.067 116.67 57.867 183.07 57.867 34.533 2.8 65.333 26.133 76.533 58.8l36.4 103.6c21.467 61.733 80.267 103.73 145.6 103.73h475.2c175.47 0 251.07-225.07 292.27-361.33 30.8-100.8 68.133-224.93 66.267-324.8 0-50.534-11.2-100-42.933-137.33"/>
                </svg>
                <span>Microsoft Copilot</span>
            </span>
            <span id="xara-pb-sep">&amp;</span>
            <span class="xara-pb-badge">
                <svg class="xara-pb-icon" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <defs>
                        <linearGradient id="xaraAzureA" x1="-1032.172" x2="-1059.213" y1="145.312" y2="65.426" gradientTransform="matrix(1 0 0 -1 1075 158)" gradientUnits="userSpaceOnUse">
                            <stop offset="0" stop-color="#114a8b"/>
                            <stop offset="1" stop-color="#0669bc"/>
                        </linearGradient>
                        <linearGradient id="xaraAzureB" x1="-1023.725" x2="-1029.98" y1="108.083" y2="105.968" gradientTransform="matrix(1 0 0 -1 1075 158)" gradientUnits="userSpaceOnUse">
                            <stop offset="0" stop-opacity=".3"/>
                            <stop offset=".071" stop-opacity=".2"/>
                            <stop offset=".321" stop-opacity=".1"/>
                            <stop offset=".623" stop-opacity=".05"/>
                            <stop offset="1" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="xaraAzureC" x1="-1027.165" x2="-997.482" y1="147.642" y2="68.561" gradientTransform="matrix(1 0 0 -1 1075 158)" gradientUnits="userSpaceOnUse">
                            <stop offset="0" stop-color="#3ccbf4"/>
                            <stop offset="1" stop-color="#2892df"/>
                        </linearGradient>
                    </defs>
                    <path fill="url(#xaraAzureA)" d="M33.338 6.544h26.038l-27.03 80.087a4.152 4.152 0 0 1-3.933 2.824H8.149a4.145 4.145 0 0 1-3.928-5.47L29.404 9.368a4.152 4.152 0 0 1 3.934-2.825z"/>
                    <path fill="#0078d4" d="M71.175 60.261h-41.29a1.911 1.911 0 0 0-1.305 3.309l26.532 24.764a4.171 4.171 0 0 0 2.846 1.121h23.38z"/>
                    <path fill="url(#xaraAzureB)" d="M33.338 6.544a4.118 4.118 0 0 0-3.943 2.879L4.252 83.917a4.14 4.14 0 0 0 3.908 5.538h20.787a4.443 4.443 0 0 0 3.41-2.9l5.014-14.777 17.91 16.705a4.237 4.237 0 0 0 2.666.972H81.24L71.024 60.261l-29.781.007L59.47 6.544z"/>
                    <path fill="url(#xaraAzureC)" d="M66.595 9.364a4.145 4.145 0 0 0-3.928-2.82H33.648a4.146 4.146 0 0 1 3.928 2.82l25.184 74.62a4.146 4.146 0 0 1-3.928 5.472h29.02a4.146 4.146 0 0 0 3.927-5.472z"/>
                </svg>
                <span>Azure AI</span>
            </span>
        </div>
    </div>
</div>

<style>
/* ── XARA Floating Chatbot Container ── */
#xara-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
}

/* ── Floating Button ── */
#xara-button {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 9998;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00E5B8, #4f7cff);
    border: 2px solid rgba(0, 229, 184, 0.4);
    box-shadow: 0 8px 32px rgba(0, 229, 184, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.34, 0.69, 0.57, 1);
    padding: 0;
    outline: none;
}

#xara-button:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 48px rgba(0, 229, 184, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.15);
    border-color: rgba(0, 229, 184, 0.8);
}

#xara-button:active {
    transform: scale(0.95);
}

#xara-button::before {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: 2px solid rgba(0, 229, 184, 0.3);
    animation: xara-pulse 2s ease-in-out infinite;
}

@keyframes xara-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0; transform: scale(1.2); }
}

/* ── Badge ── */
#xara-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    width: 24px;
    height: 24px;
    background: #ff4757;
    border: 2px solid white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 800;
    color: white;
    z-index: 10000;
}

/* ── Chat Panel ── */
#xara-panel {
    position: fixed;
    bottom: 110px;
    right: 30px;
    z-index: 9998;
    width: 360px;
    height: 520px;
    background: var(--bg2, #0d1829);
    border: 1px solid var(--border, rgba(0, 229, 184, 0.2));
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 1px rgba(0, 229, 184, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transform: scale(0.8) translateY(20px);
    opacity: 0;
    pointer-events: none;
    transition: all 0.3s cubic-bezier(0.34, 0.69, 0.57, 1);
    font-family: inherit;
}

#xara-panel.open {
    transform: scale(1) translateY(0);
    opacity: 1;
    pointer-events: auto;
}

/* ── Header ── */
#xara-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-bottom: 1px solid var(--border, rgba(0, 229, 184, 0.15));
    background: linear-gradient(135deg, rgba(0, 229, 184, 0.08), rgba(79, 124, 255, 0.08));
    flex-shrink: 0;
}

#xara-avatar {
    font-size: 32px;
    flex-shrink: 0;
}

#xara-info {
    flex: 1;
    min-width: 0;
}

#xara-name {
    font-weight: 800;
    color: var(--text, white);
    font-size: 15px;
    margin: 0;
}

#xara-status {
    font-size: 12px;
    color: var(--text2, #00E5B8);
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 2px;
}

#xara-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    animation: xara-blink 1.5s ease-in-out infinite;
}

@keyframes xara-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

#xara-reset {
    background: none;
    border: none;
    color: var(--text2, #888);
    font-size: 14px;
    cursor: pointer;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
    padding: 0;
    outline: none;
    flex-shrink: 0;
}

#xara-reset:hover {
    color: #ff4757;
}

#xara-close {
    background: none;
    border: none;
    color: var(--text2, #888);
    font-size: 18px;
    cursor: pointer;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
    padding: 0;
    outline: none;
    flex-shrink: 0;
}

#xara-close:hover {
    color: var(--text, white);
}

/* ── Messages ── */
#xara-messages {
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
}

#xara-messages::-webkit-scrollbar {
    width: 4px;
}

#xara-messages::-webkit-scrollbar-track {
    background: transparent;
}

#xara-messages::-webkit-scrollbar-thumb {
    background: rgba(0, 229, 184, 0.2);
    border-radius: 4px;
}

.xara-msg {
    font-size: 13px;
    line-height: 1.5;
    padding: 10px 12px;
    border-radius: 10px;
    word-break: break-word;
    max-width: 85%;
    animation: xara-fadein 0.2s ease;
}

@keyframes xara-fadein {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.xara-bot {
    background: rgba(0, 229, 184, 0.1);
    border: 1px solid rgba(0, 229, 184, 0.2);
    color: var(--text, #d8eaf8);
    align-self: flex-start;
    border-radius: 4px 10px 10px 10px;
}

.xara-user {
    background: linear-gradient(135deg, rgba(79, 124, 255, 0.15), rgba(0, 229, 184, 0.08));
    border: 1px solid rgba(79, 124, 255, 0.25);
    color: var(--text, white);
    align-self: flex-end;
    border-radius: 10px 4px 10px 10px;
}

/* ── Quick Chips ── */
#xara-chips {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding: 12px;
    border-top: 1px solid var(--border, rgba(0, 229, 184, 0.15));
    border-bottom: 1px solid var(--border, rgba(0, 229, 184, 0.15));
    flex-shrink: 0;
}

.xara-chip {
    padding: 6px 12px;
    border-radius: 20px;
    background: rgba(79, 124, 255, 0.1);
    border: 1px solid rgba(79, 124, 255, 0.25);
    color: var(--text, white);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    outline: none;
}

.xara-chip:hover {
    background: rgba(79, 124, 255, 0.2);
    border-color: rgba(79, 124, 255, 0.5);
    transform: translateY(-2px);
}

/* ── Input Row ── */
#xara-input-row {
    display: flex;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid var(--border, rgba(0, 229, 184, 0.15));
    flex-shrink: 0;
    background: var(--bg, #020712);
}

#xara-input {
    flex: 1;
    background: var(--bg2, #0d1829);
    border: 1px solid var(--border, rgba(0, 229, 184, 0.15));
    border-radius: 20px;
    padding: 8px 14px;
    color: var(--text, white);
    font-size: 13px;
    outline: none;
    transition: all 0.2s;
    font-family: inherit;
}

#xara-input:focus {
    border-color: rgba(0, 229, 184, 0.4);
    box-shadow: 0 0 12px rgba(0, 229, 184, 0.15);
}

#xara-input::placeholder {
    color: var(--text2, #666);
}

#xara-send {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00E5B8, #4f7cff);
    border: none;
    color: white;
    font-weight: 800;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    padding: 0;
    outline: none;
    flex-shrink: 0;
}

#xara-send:hover {
    box-shadow: 0 6px 20px rgba(0, 229, 184, 0.3);
    transform: translateY(-2px);
}

#xara-send:active {
    transform: scale(0.9);
}

/* ── Powered By footer ── */
#xara-powered-by {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px 12px 10px;
    flex-shrink: 0;
    background: var(--bg, #020712);
    font-size: 10px;
    color: var(--text2, #7c8798);
}

#xara-pb-label {
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    opacity: 0.75;
}

#xara-pb-sep {
    opacity: 0.5;
}

.xara-pb-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-weight: 600;
    color: var(--text, #d8eaf8);
}

.xara-pb-icon {
    width: 13px;
    height: 13px;
    flex-shrink: 0;
}

@media (max-width: 480px) {
    #xara-panel {
        width: calc(100vw - 40px);
        max-width: 360px;
        right: 20px;
        bottom: 100px;
    }
}
</style>

<script>
(function() {
    'use strict';

    // ── Configuration injected from Python ──────────────────────────────────────
    const SERVER_MESSAGES  = __XARA_MESSAGES_JSON__;
    const AZURE_AVAILABLE  = __AZURE_AVAILABLE__;   // true → use Python bridge; false → JS KB

    // ── Embedded rule-based knowledge base (mirrors Python KB) ──────────────────
    const XARA_KB = [
        { keywords: ["book", "reserve", "parking space"],
          responses: [
            "You can book a parking slot directly from your dashboard. Click on 'Available Slots' and select your preferred time and location.",
            "To book a slot: 1) View available slots on the map 2) Select your preferred slot 3) Choose time duration 4) Complete payment. Your booking is confirmed!"
          ]},
        { keywords: ["pay", "payment", "price", "cost", "fee", "credit card", "debit card"],
          responses: [
            "We accept both credit and debit cards for payments. Payment is secure and processed instantly.",
            "All payments are processed securely. You'll receive a receipt immediately after successful payment."
          ]},
        { keywords: ["qr code", "qr", "entry", "exit", "scan"],
          responses: [
            "Your QR code is generated automatically after booking. Show it at the parking entry gate for seamless entry/exit.",
            "The QR code is your digital parking ticket. It contains all your booking details and is required for entry and exit."
          ]},
        { keywords: ["slot", "availability", "available", "free", "occupied", "vacant"],
          responses: [
            "You can view all available parking slots in real-time on the map in your dashboard. Green = available, red = occupied.",
            "Real-time slot availability is updated continuously. Check the availability map to find the perfect spot for your vehicle."
          ]},
        { keywords: ["waitlist", "waiting", "queue", "notify", "availability alert"],
          responses: [
            "If all slots are full, you can join the waitlist. You'll be notified automatically when a slot becomes available.",
            "Can't find a slot? Join the waitlist! The system will alert you when a suitable slot becomes available."
          ]},
        { keywords: ["account", "profile", "user", "registration", "sign up", "login"],
          responses: [
            "To create an account, click on 'Create Account' on the login page and fill in your details. You'll get instant access!",
            "Already have an account? Sign in with your username and password. New users can register in seconds!"
          ]},
        { keywords: ["admin", "manage", "analytics", "reports", "dashboard"],
          responses: [
            "Admin features include real-time slot management, analytics, user management, and detailed reports. Sign in as admin to access.",
            "The admin dashboard provides full control over parking operations, including occupancy rates, revenue tracking, and user management."
          ]},
        { keywords: ["location", "address", "map", "area", "zone"],
          responses: [
            "SLotX operates in multiple locations. Use the map view to select your preferred parking area.",
            "Browse different parking zones on the map and book slots based on your destination."
          ]},
        { keywords: ["price", "rate", "hourly", "daily", "monthly", "charge"],
          responses: [
            "Pricing varies by location and time. Check the rates displayed when you select a parking slot.",
            "SLotX offers competitive pricing with transparent rate cards. No hidden charges!"
          ]},
        { keywords: ["contact", "support", "help", "phone", "email", "customer service"],
          responses: [
            "Contact us at support@slotx.in or call +91-8765-432-109. Our team is available Monday–Friday, 9 AM–6 PM.",
            "Need help? Email support@slotx.in with your query. We respond within 2 hours."
          ]},
        { keywords: ["hours", "timing", "open", "close", "business hours"],
          responses: [
            "SLotX support is available: Monday–Friday 9 AM–6 PM, Saturday 9 AM–2 PM. Parking facilities are 24/7.",
            "Parking slots are available 24/7, but our customer support team works Monday–Friday 9–6 and Saturday 9–2."
          ]}
    ];

    function getLocalResponse(text) {
        const lower = text.toLowerCase().trim();
        if (/\b(hi|hello|hey|greetings)\b/.test(lower))
            return "👋 Hello! I'm XARA, your intelligent SlotX parking assistant. How can I help you today? Ask me about booking, payments, slots, or QR codes!";
        if (/\b(thank|thanks|appreciate)\b/.test(lower))
            return "You're welcome! Is there anything else I can help you with regarding your parking experience?";
        for (const cat of XARA_KB) {
            for (const kw of cat.keywords) {
                if (lower.includes(kw))
                    return cat.responses[Math.floor(Math.random() * cat.responses.length)];
            }
        }
        if (/\b(how|what|where|when|why)\b/.test(lower))
            return "That's a great question! Could you be more specific? Ask me about: booking slots, payments, QR codes, availability, pricing, or account details.";
        return "I'm here to help with parking-related questions. Try asking about booking slots, payments, real-time availability, QR codes, waitlists, or pricing. What would you like to know?";
    }

    // ── Get window reference where state is stored ─────────────────────────────
    function getTopWindow() {
        try {
            return (window.parent && window.parent.document) ? window.parent : window;
        } catch(e) {
            return window;
        }
    }

    const topWin = getTopWindow();

    // Initialize top-level history if not present
    if (!topWin.__xara_history || topWin.__xara_history.length === 0) {
        topWin.__xara_history = SERVER_MESSAGES.length > 0 ? SERVER_MESSAGES : [
            { role: "bot", content: "👋 Hi! I'm XARA — your intelligent parking assistant from SlotX. Ask me anything about booking, payments, slots, or QR codes!" }
        ];
        topWin.__xara_rendered_count = SERVER_MESSAGES.length;
    }
    if (typeof topWin.__xara_is_open === 'undefined') {
        topWin.__xara_is_open = false;
    }

    // ── Message rendering ────────────────────────────────────────────────────────
    function renderHistory(doc) {
        const messagesBox = doc.getElementById('xara-messages');
        if (!messagesBox) return;
        messagesBox.innerHTML = '';
        const history = topWin.__xara_history || [];
        history.forEach(msg => {
            const div = doc.createElement('div');
            div.className = 'xara-msg ' + (msg.role === 'bot' ? 'xara-bot' : 'xara-user');
            div.innerHTML = '<strong>' + (msg.role === 'bot' ? 'XARA' : 'You') + ':</strong> ' + msg.content;
            messagesBox.appendChild(div);
        });
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    // ── Sync messages from Python (used in Azure mode) ───────────────────────────
    // renderedCount lives on topWin (not on the widget DOM) because injectIntoParent()
    // tears down and rebuilds that DOM on every rerun — a dataset attribute on it would
    // never persist, causing the full SERVER_MESSAGES history to be re-pushed into
    // topWin.__xara_history on every single render and grow unbounded across a session.
    function syncMessages(doc) {
        if (!AZURE_AVAILABLE) return;

        const rendered = topWin.__xara_rendered_count || 0;
        if (SERVER_MESSAGES.length > rendered) {
            const pending = doc.getElementById('xara-pending');
            if (pending) pending.remove();

            for (let i = rendered; i < SERVER_MESSAGES.length; i++) {
                topWin.__xara_history.push(SERVER_MESSAGES[i]);
            }
            topWin.__xara_rendered_count = SERVER_MESSAGES.length;
        }
        renderHistory(doc);
    }

    // ── Python bridge (Azure OpenAI only) ────────────────────────────────────────
    // Streamlit's st.form() renders as a <div data-testid="stForm"> (no native <form>
    // element, and st.form()'s key is not applied as a .st-key-<key> class on that div),
    // so the submit button must be found by walking up from the input to that div.
    function submitToBridge(doc, text) {
        const inputEl = doc.querySelector('.st-key-xara_bridge_input input');
        if (!inputEl) return;

        const formDiv = inputEl.closest('[data-testid="stForm"]');
        if (!formDiv) return;
        const submitBtn = formDiv.querySelector('button[data-testid^="stBaseButton"]');
        if (!submitBtn) return;

        const ownerWindow = inputEl.ownerDocument.defaultView || inputEl.ownerDocument.parentWindow;
        const nativeSetter = Object.getOwnPropertyDescriptor(ownerWindow.HTMLInputElement.prototype, 'value').set;

        nativeSetter.call(inputEl, '');
        inputEl.dispatchEvent(new ownerWindow.Event('input', { bubbles: true }));
        nativeSetter.call(inputEl, text);
        inputEl.dispatchEvent(new ownerWindow.Event('focus',  { bubbles: true }));
        inputEl.dispatchEvent(new ownerWindow.Event('input',  { bubbles: true }));
        inputEl.dispatchEvent(new ownerWindow.Event('change', { bubbles: true }));

        setTimeout(() => submitBtn.click(), 100);
    }

    // ── Force-hide the Streamlit bridge form via direct DOM style manipulation ──
    // CSS selectors are unreliable; JS inline styles with !important always win.
    function hideBridgeForm(doc) {
        try {
            var hide = function(el) {
                if (!el) return;
                el.style.setProperty('display',    'none',   'important');
                el.style.setProperty('height',     '0',      'important');
                el.style.setProperty('min-height', '0',      'important');
                el.style.setProperty('margin',     '0',      'important');
                el.style.setProperty('padding',    '0',      'important');
                el.style.setProperty('overflow',   'hidden', 'important');
                el.style.setProperty('border',     'none',   'important');
            };
            var forms = doc.querySelectorAll('[data-testid="stForm"]');
            forms.forEach(function(form) {
                var inp = form.querySelector('.st-key-xara_bridge_input') ||
                          form.querySelector('input[aria-label="XARA bridge"]');
                if (!inp) return;
                hide(form);
                var el = form.parentElement;
                for (var i = 0; i < 6 && el && el !== doc.body; i++, el = el.parentElement) {
                    if (el.classList.contains('element-container') ||
                        el.getAttribute('data-testid') === 'element-container') {
                        hide(el);
                        break;
                    }
                }
            });
        } catch(e) {}
    }

    // ── Inject widget into PARENT document (Streamlit uses iframes for components)
    function injectIntoParent() {
        var targetDoc = document;
        try {
            if (window.parent && window.parent.document) {
                targetDoc = window.parent.document;
            }
        } catch (e) {
            targetDoc = document;
        }

        // Force-hide the bridge form on every run (CSS alone is not reliable)
        hideBridgeForm(targetDoc);

        // Clean up previous host to prevent stale detached iframe event listeners
        const existingHost = targetDoc.getElementById('xara-root-host');
        if (existingHost) {
            existingHost.remove();
        }
        const existingStyle = targetDoc.getElementById('xara-styles');
        if (existingStyle) {
            existingStyle.remove();
        }

        const container = document.getElementById('xara-container');
        if (!container) return;

        const clone = targetDoc.createElement('div');
        clone.id = 'xara-root-host';
        clone.innerHTML = container.outerHTML;
        targetDoc.body.appendChild(clone);

        const styleEl = document.querySelector('style');
        if (styleEl) {
            const parentStyle = targetDoc.createElement('style');
            parentStyle.id = 'xara-styles';
            parentStyle.textContent = styleEl.textContent;
            targetDoc.head.appendChild(parentStyle);
        }

        initXara(targetDoc);
    }

    function initXara(doc) {
        doc = doc || document;
        const button     = doc.getElementById('xara-button');
        const panel      = doc.getElementById('xara-panel');
        const closeBtn   = doc.getElementById('xara-close');
        const resetBtn   = doc.getElementById('xara-reset');
        const sendBtn    = doc.getElementById('xara-send');
        const input      = doc.getElementById('xara-input');
        const messagesBox = doc.getElementById('xara-messages');
        const chips      = doc.querySelectorAll ? doc.querySelectorAll('.xara-chip') : [];

        if (!button || !panel) return;

        // Restore open state
        if (topWin.__xara_is_open) {
            panel.classList.add('open');
            const badge = doc.getElementById('xara-badge');
            if (badge) badge.style.display = 'none';
        }

        // Render history from window.parent
        renderHistory(doc);
        syncMessages(doc);

        function toggleChat() {
            topWin.__xara_is_open = !topWin.__xara_is_open;
            panel.classList.toggle('open', topWin.__xara_is_open);
            if (topWin.__xara_is_open && input) {
                input.focus();
                const badge = doc.getElementById('xara-badge');
                if (badge) badge.style.display = 'none';
            }
        }

        function resetChat() {
            topWin.__xara_history = [
                { role: "bot", content: "👋 Hi! I'm XARA — your intelligent parking assistant from SlotX. Ask me anything about booking, payments, slots, or QR codes!" }
            ];
            renderHistory(doc);
        }

        function sendMessage() {
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            input.value = '';

            if (AZURE_AVAILABLE) {
                // Azure mode: the user message is added to topWin.__xara_history by
                // syncMessages() once Python echoes it back in SERVER_MESSAGES — pushing
                // it here too would duplicate it. Just show a typing indicator and wait.
                const typing = doc.createElement('div');
                typing.className = 'xara-msg xara-bot';
                typing.id = 'xara-pending';
                typing.innerHTML = '<strong>XARA:</strong> <span style="opacity:0.6">●●●</span>';
                if (messagesBox) { messagesBox.appendChild(typing); messagesBox.scrollTop = messagesBox.scrollHeight; }
                submitToBridge(doc, text);
            } else {
                // Local KB mode: respond immediately
                topWin.__xara_history.push({ role: 'user', content: text });
                const response = getLocalResponse(text);
                topWin.__xara_history.push({ role: 'bot', content: response });
                renderHistory(doc);
            }
        }

        button.addEventListener('click', toggleChat);
        if (closeBtn) closeBtn.addEventListener('click', toggleChat);
        if (resetBtn) resetBtn.addEventListener('click', resetChat);
        if (sendBtn)  sendBtn.addEventListener('click', sendMessage);
        if (input)    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });

        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                if (input) input.value = chip.dataset.question;
                sendMessage();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectIntoParent);
    } else {
        injectIntoParent();
    }
    setTimeout(injectIntoParent, 200);

    // Extra delayed passes to hide the bridge form after Streamlit finishes rendering
    (function() {
        var td = document;
        try { if (window.parent && window.parent.document) td = window.parent.document; } catch(e) {}
        setTimeout(function() { hideBridgeForm(td); }, 300);
        setTimeout(function() { hideBridgeForm(td); }, 900);
    })();
})();
</script>
"""
    return (html
            .replace("__XARA_MESSAGES_JSON__", messages_json)
            .replace("__AZURE_AVAILABLE__", azure_flag))


