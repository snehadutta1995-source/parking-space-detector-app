"""
SLotX Chatbot Utilities - FIXED VERSION
Provides intelligent responses for parking-related queries
Floating widget now works properly across all pages
"""

import random
from datetime import datetime


class ParkingChatbot:
    """Smart chatbot for SLotX parking management system"""

    def __init__(self):
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

    def get_response(self, user_message):
        """Generate appropriate response based on user query"""
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


def get_xara_floating_widget():
    """Return HTML/JS that injects the XARA floating chatbot into the parent Streamlit document."""
    return """
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
            <button id="xara-close" type="button">✕</button>
        </div>

        <div id="xara-messages">
            <div class="xara-msg xara-bot">
                <strong>XARA:</strong> 👋 Hi! I'm <strong>XARA</strong> — your intelligent parking assistant from SlotX. Ask me anything about booking, payments, slots, or QR codes!
            </div>
        </div>

        <div id="xara-chips">
            <span class="xara-chip" data-question="How do I book a slot?">📍 Book a slot</span>
            <span class="xara-chip" data-question="What payment methods?">💳 Payment</span>
            <span class="xara-chip" data-question="How does the QR code work?">🎯 QR code</span>
        </div>

        <div id="xara-input-row">
            <input id="xara-input" type="text" placeholder="Ask XARA anything..." />
            <button id="xara-send" type="button">➤</button>
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
    
    // Knowledge base embedded
    const KB = {
        booking: { kw: ["book", "reserv", "slot", "parking space"], r: ["You can book a parking slot from your dashboard. Click 'Available Slots', select your preferred time and location, then complete payment. Your QR code is generated instantly!", "To book: 1) View available slots 2) Select your preferred slot 3) Choose duration 4) Pay. Done — your booking is confirmed! ✅", "Booking is easy! Navigate to the booking section, pick your slot, and proceed to payment."] },
        payment: { kw: ["pay", "payment", "price", "cost", "fee", "credit", "debit"], r: ["We accept both credit and debit cards. Payment is secure and processed instantly. 💳", "Payments are processed securely. You'll receive a receipt immediately after success!", "Check the demo payment options for test card details. All real payments are end-to-end encrypted."] },
        qr: { kw: ["qr", "entry", "exit", "scan", "ticket"], r: ["Your QR code is generated automatically after booking. Show it at the entry gate for seamless access! 📱", "The QR code is your digital parking ticket — required for entry and exit. Keep it handy!", "Present your QR code at the gate. The system validates your booking and lets you in. Same for exit!"] },
        slots: { kw: ["slot", "availab", "free", "occupied", "vacant", "space"], r: ["Real-time slot availability is on the map in your dashboard. 🟢 Green = available, 🔴 Red = occupied.", "Slot availability updates continuously. Use the map to find the perfect spot!", "Available slots are color-coded for easy identification. Use filters to find slots that match your needs."] },
        waitlist: { kw: ["waitlist", "waiting", "queue", "notify", "alert"], r: ["If all slots are full, join the waitlist! You'll be notified automatically when a slot opens. 🔔", "The waitlist feature alerts you as soon as a suitable slot is free in your selected location.", "Can't find a slot? Join the waitlist and we'll alert you the moment one opens up!"] },
        account: { kw: ["account", "profile", "user", "register", "sign up", "login"], r: ["Create an account via 'Create Account' on the login page — instant access! 🚀", "You'll need your name, email, phone, and a password to register.", "Already registered? Sign in with your username and password. New users can register in seconds!"] },
        contact: { kw: ["contact", "support", "help", "phone", "email", "customer"], r: ["Reach us at support@slotx.in or +91-8765-432-109. Mon–Fri 9 AM – 6 PM. 📧", "For support email support@slotx.in or call +91-9876-543-210. We respond within 2 hours!", "Visit the Contact Us section in the sidebar or email us anytime!"] },
        pricing: { kw: ["pric", "rate", "hourly", "daily", "monthly", "cost", "charge"], r: ["Pricing varies by location and time. Rates are displayed before you confirm your booking — no surprises! 💰", "Hourly, daily, and monthly options available. Check rates when selecting your slot.", "Competitive and transparent pricing with no hidden charges. See rates at booking time!"] }
    };

    function getResponse(msg) {
        const m = msg.toLowerCase().trim();
        
        if (/\\b(hi|hello|hey|greet)\\b/.test(m)) {
            return "👋 Hello! I'm XARA, your SlotX assistant. Ask me about booking, payments, slots, QR codes, or anything parking-related!";
        }
        if (/thank/.test(m)) {
            return "You're welcome! 😊 Is there anything else I can help you with?";
        }
        
        for (const [_, v] of Object.entries(KB)) {
            if (v.kw.some(k => m.includes(k))) {
                return v.r[Math.floor(Math.random() * v.r.length)];
            }
        }
        
        return "Great question! I can help with booking slots, payments, real-time availability, QR codes, waitlists, and pricing. What would you like to know? 🅿️";
    }

    // ── Inject widget into PARENT document (Streamlit runs components in iframes) ──
    function injectIntoParent() {
        try {
            const parentDoc = window.parent.document;

            // Avoid duplicate injection
            if (parentDoc.getElementById('xara-container')) {
                initXara(parentDoc);
                return;
            }

            // Clone widget HTML into parent
            const container = document.getElementById('xara-container');
            if (!container) return;

            const clone = parentDoc.createElement('div');
            clone.id = 'xara-root-host';
            clone.innerHTML = container.outerHTML;
            parentDoc.body.appendChild(clone);

            // Inject styles into parent
            const styleEl = document.querySelector('style');
            if (styleEl) {
                const parentStyle = parentDoc.createElement('style');
                parentStyle.id = 'xara-styles';
                parentStyle.textContent = styleEl.textContent;
                parentDoc.head.appendChild(parentStyle);
            }

            initXara(parentDoc);
        } catch (e) {
            // Fallback: same-document mode (when not in iframe)
            initXara(document);
        }
    }

    function initXara(doc) {
        doc = doc || document;
        const button = doc.getElementById('xara-button');
        const panel = doc.getElementById('xara-panel');
        const closeBtn = doc.getElementById('xara-close');
        const sendBtn = doc.getElementById('xara-send');
        const input = doc.getElementById('xara-input');
        const messagesBox = doc.getElementById('xara-messages');
        const chips = doc.querySelectorAll ? doc.querySelectorAll('.xara-chip') : [];

        if (!button || !panel) return;

        // Mark as initialized to prevent double-binding
        if (button.dataset.xaraInit === '1') return;
        button.dataset.xaraInit = '1';

        let isOpen = false;

        function toggleChat() {
            isOpen = !isOpen;
            panel.classList.toggle('open', isOpen);
            if (isOpen && input) {
                input.focus();
                const badge = doc.getElementById('xara-badge');
                if (badge) badge.style.display = 'none';
            }
        }

        function addMessage(text, sender) {
            if (!messagesBox) return;
            const div = doc.createElement('div');
            div.className = 'xara-msg ' + (sender === 'bot' ? 'xara-bot' : 'xara-user');
            div.innerHTML = '<strong>' + (sender === 'bot' ? 'XARA' : 'You') + ':</strong> ' + text;
            messagesBox.appendChild(div);
            messagesBox.scrollTop = messagesBox.scrollHeight;
        }

        function sendMessage() {
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, 'user');

            const typing = doc.createElement('div');
            typing.className = 'xara-msg xara-bot';
            typing.id = 'typing-indicator';
            typing.innerHTML = '<strong>XARA:</strong> <span style="opacity:0.6">●●●</span>';
            if (messagesBox) { messagesBox.appendChild(typing); messagesBox.scrollTop = messagesBox.scrollHeight; }

            setTimeout(() => {
                if (typing.parentNode) typing.remove();
                addMessage(getResponse(text), 'bot');
            }, 600 + Math.random() * 400);
        }

        button.addEventListener('click', toggleChat);
        if (closeBtn) closeBtn.addEventListener('click', toggleChat);
        if (sendBtn) sendBtn.addEventListener('click', sendMessage);
        if (input) input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });

        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                if (input) input.value = chip.dataset.question;
                sendMessage();
            });
        });
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectIntoParent);
    } else {
        injectIntoParent();
    }
    setTimeout(injectIntoParent, 200);
})();
</script>
"""
