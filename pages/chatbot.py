"""
SLotX Chatbot UI Page
Interactive chatbot interface for parking management assistance
"""

import streamlit as st
from utils.chatbot_utils import create_chatbot


def render_chatbot():
    """Render the chatbot interface"""

    st.markdown("""
    <style>
    .chatbot-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        display: flex;
        gap: 10px;
        align-items: flex-start;
    }
    .user-message {
        background: linear-gradient(135deg, rgba(0, 229, 184, 0.15), rgba(79, 124, 255, 0.1));
        border: 1px solid rgba(0, 229, 184, 0.25);
        margin-left: auto;
        max-width: 80%;
        justify-content: flex-end;
    }
    .bot-message {
        background: var(--bg2);
        border: 1px solid var(--border);
        max-width: 80%;
    }
    .message-avatar {
        font-size: 24px;
        flex-shrink: 0;
    }
    .message-content {
        flex: 1;
        color: var(--text);
        font-size: 14px;
        line-height: 1.5;
    }
    .message-time {
        font-size: 11px;
        color: var(--text2);
        margin-top: 4px;
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent);
        animation: typing 1.4s infinite;
    }
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing {
        0%, 60%, 100% {
            opacity: 0.3;
            transform: translateY(0);
        }
        30% {
            opacity: 1;
            transform: translateY(-10px);
        }
    }
    .input-section {
        display: flex;
        gap: 8px;
        margin-top: 1.5rem;
    }
    .quick-buttons {
        display: flex;
        gap: 8px;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .quick-btn {
        padding: 6px 12px;
        font-size: 12px;
        border-radius: 20px;
        background: var(--bg2);
        border: 1px solid var(--border);
        color: var(--text);
        cursor: pointer;
        transition: all 0.2s;
    }
    .quick-btn:hover {
        background: rgba(0, 229, 184, 0.15);
        border-color: rgba(0, 229, 184, 0.4);
        color: var(--accent);
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state for chatbot
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []
    if "chatbot_instance" not in st.session_state:
        st.session_state.chatbot_instance = create_chatbot()

    # Header
    st.markdown("""
    <div style='text-align:center;margin-bottom:2rem'>
        <div style='font-family:Syne,sans-serif;font-size:32px;font-weight:900;
                    background:linear-gradient(135deg,#00f5ff,#22c55e);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>
            XARA — SlotX Intelligent Assistant
        </div>
        <div style='font-size:14px;color:var(--text2);margin-top:8px'>
            24/7 AI-powered assistance for all your parking needs
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Quick question buttons
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📍 How to book?", use_container_width=True, key="quick_book"):
            user_input = "How do I book a parking slot?"
            st.session_state.chatbot_messages.append({
                "role": "user",
                "content": user_input
            })
            response = st.session_state.chatbot_instance.get_response(user_input)
            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    with col2:
        if st.button("💳 Payment info?", use_container_width=True, key="quick_pay"):
            user_input = "What payment methods do you accept?"
            st.session_state.chatbot_messages.append({
                "role": "user",
                "content": user_input
            })
            response = st.session_state.chatbot_instance.get_response(user_input)
            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    with col3:
        if st.button("🎯 View slots?", use_container_width=True, key="quick_slots"):
            user_input = "How can I view available parking slots?"
            st.session_state.chatbot_messages.append({
                "role": "user",
                "content": user_input
            })
            response = st.session_state.chatbot_instance.get_response(user_input)
            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": response
            })
            st.rerun()

    st.divider()

    # Chat history display
    st.markdown("**Conversation:**")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chatbot_messages:
            st.info("👋 👋 Hi! I'm XARA, your intelligent parking assistant from SlotX. Ask me anything about parking, bookings, payments, or use the quick buttons above!")
        else:
            for message in st.session_state.chatbot_messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class='chat-message user-message'>
                        <div style='flex: 1;'>
                            <div class='message-content'>{message["content"]}</div>
                        </div>
                        <div class='message-avatar'>👤</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-message bot-message'>
                        <div class='message-avatar'>🅿️</div>
                        <div style='flex: 1;'>
                            <div class='message-content'>{message["content"]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.divider()

    # Input section
    user_input = st.text_input(
        "Your question:",
        placeholder="Ask me about booking, payments, slots, QR codes, or any parking-related question...",
        label_visibility="collapsed",
        key="chatbot_input"
    )

    if user_input:
        # Add user message
        st.session_state.chatbot_messages.append({
            "role": "user",
            "content": user_input
        })

        # Get bot response
        response = st.session_state.chatbot_instance.get_response(user_input)
        st.session_state.chatbot_messages.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

    # Clear conversation button
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.chatbot_messages = []
            st.rerun()

    st.markdown("""
    <div style='margin-top:2rem;padding-top:1rem;border-top:1px solid var(--border);
                font-size:12px;color:var(--text2);text-align:center'>
        <div>For urgent support, contact us:</div>
        <div style='margin-top:8px'>
            📧 support@slotx.in | 📱 +91-8765-432-109<br>
            Monday-Friday: 9 AM - 6 PM | Saturday: 9 AM - 2 PM
        </div>
    </div>
    """, unsafe_allow_html=True)
