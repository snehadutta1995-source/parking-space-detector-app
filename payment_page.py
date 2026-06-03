"""
SLotX — Payment Gateway
Handle payments via Credit/Debit Cards, UPI, and other methods
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import re

from utils.database import (
    get_booking_by_ref, activate_booking, get_payment_by_booking_ref,
    create_payment, update_payment_status, send_notification, get_user
)
from utils.styles import apply_theme


def validate_credit_card(card_number):
    """Validate credit card using Luhn algorithm."""
    card_number = card_number.replace(" ", "").replace("-", "")
    if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn algorithm
    digits = [int(d) for d in card_number]
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def validate_cvv(cvv):
    """Validate CVV (3-4 digits)."""
    return bool(re.match(r'^\d{3,4}$', cvv))


def validate_upi(upi_id):
    """Validate UPI ID format."""
    return bool(re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z]+$', upi_id))


def render_payment():
    """Main payment gateway page."""
    st.markdown(apply_theme(st.session_state.dark), unsafe_allow_html=True)
    
    # Get booking reference from query params
    booking_ref = st.query_params.get("booking_ref", None)
    
    if not booking_ref:
        st.error("❌ No booking reference found. Please start a new booking.")
        if st.button("← Go Back to Bookings"):
            st.switch_page("pages/user_ui_updated.py")
        return
    
    # Get booking details
    booking = get_booking_by_ref(booking_ref)
    
    if not booking:
        st.error(f"❌ Booking '{booking_ref}' not found.")
        if st.button("← Go Back to Bookings"):
            st.switch_page("pages/user_ui_updated.py")
        return
    
    if booking["status"] == "active":
        st.warning(f"⚠️ This booking is already paid and active!")
        if st.button("← Go Back to My Bookings"):
            st.switch_page("pages/user_ui_updated.py")
        return
    
    # Header
    st.markdown("""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>💳</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Secure Payment</h1>
        <div style='font-size:13px;color:#9aa0b4'>Complete your parking booking payment</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    # Left column: Payment form
    with col1:
        st.markdown("### Booking Summary")
        summary_cols = st.columns(2)
        with summary_cols[0]:
            st.metric("Booking Ref", booking["booking_ref"])
            st.metric("Slot", booking["slot_code"])
        with summary_cols[1]:
            st.metric("Date", booking["from_date"])
            st.metric("Duration", f"{booking['duration_hr']}h")
        
        st.divider()
        
        # Payment method selection
        st.markdown("### Select Payment Method")
        payment_method = st.radio(
            "Choose how you'd like to pay:",
            ["💳 Credit/Debit Card", "📱 UPI", "💰 Other Methods"],
            key="payment_method"
        )
        
        st.divider()
        
        # Payment form based on method
        if payment_method.startswith("💳"):
            _render_card_payment(booking)
        elif payment_method.startswith("📱"):
            _render_upi_payment(booking)
        else:
            _render_other_payment(booking)
    
    # Right column: Order summary
    with col2:
        st.markdown("### Amount Due")
        st.markdown(f"""
        <div style='background:#1e222c;border-radius:8px;padding:16px;border:1px solid #2a2f3d'>
            <div style='font-size:13px;color:#9aa0b4;margin-bottom:8px'>
                <div style='display:flex;justify-content:space-between;padding:4px 0'>
                    <span>Base Amount</span>
                    <span>₹{booking['amount']:.2f}</span>
                </div>
            </div>
            <div style='border-top:1px solid #2a2f3d;padding-top:8px;margin-top:8px'>
                <div style='display:flex;justify-content:space-between;padding:4px 0;font-size:16px;font-weight:700'>
                    <span>Total</span>
                    <span style='color:#22c55e'>₹{booking['amount']:.2f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🔒 Your payment is secure and encrypted.")


def _render_card_payment(booking):
    """Render credit/debit card payment form."""
    st.markdown("#### Card Details")
    
    with st.form("card_payment_form"):
        cardholder = st.text_input("Cardholder Name", placeholder="John Doe")
        card_number = st.text_input(
            "Card Number",
            placeholder="1234 5678 9012 3456",
            max_chars=19
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            expiry = st.text_input("MM/YY", placeholder="12/25", max_chars=5)
        with col2:
            cvv = st.text_input("CVV", placeholder="123", max_chars=4, type="password")
        with col3:
            st.write("")
            st.write("")
        
        st.markdown("---")
        
        # Billing address
        st.markdown("#### Billing Address")
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City")
        with col2:
            pincode = st.text_input("Pincode")
        
        submit = st.form_submit_button("💳 Pay ₹" + f"{booking['amount']:.2f}", use_container_width=True)
        
        if submit:
            # Validation
            errors = []
            if not cardholder:
                errors.append("Cardholder name is required")
            
            card_num = card_number.replace(" ", "").replace("-", "")
            if not validate_credit_card(card_num):
                errors.append("Invalid card number")
            
            if not expiry or "/" not in expiry:
                errors.append("Invalid expiry date format (use MM/YY)")
            
            if not validate_cvv(cvv):
                errors.append("Invalid CVV (3-4 digits)")
            
            if not city:
                errors.append("City is required")
            
            if not pincode or len(pincode) != 6:
                errors.append("Valid 6-digit pincode required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                _process_card_payment(booking, cardholder, card_num[-4:])


def _render_upi_payment(booking):
    """Render UPI payment form."""
    st.markdown("#### UPI Payment")
    st.info("📱 Enter your UPI ID to proceed with payment")
    
    with st.form("upi_payment_form"):
        upi_id = st.text_input(
            "UPI ID",
            placeholder="yourname@bankname",
            help="E.g., john@paytm or rahul@googlepay"
        )
        
        st.markdown("---")
        st.markdown("**Popular UPI Apps:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("📲 Google Pay", disabled=True, use_container_width=True)
        with col2:
            st.button("📲 PhonePe", disabled=True, use_container_width=True)
        with col3:
            st.button("📲 Paytm", disabled=True, use_container_width=True)
        with col4:
            st.button("📲 WhatsApp Pay", disabled=True, use_container_width=True)
        
        st.markdown("---")
        
        submit = st.form_submit_button("📱 Pay with UPI ₹" + f"{booking['amount']:.2f}", use_container_width=True)
        
        if submit:
            if not upi_id or not validate_upi(upi_id):
                st.error("❌ Please enter a valid UPI ID (e.g., yourname@bankname)")
            else:
                _process_upi_payment(booking, upi_id)


def _render_other_payment(booking):
    """Render other payment methods."""
    st.markdown("#### Alternative Payment Methods")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏦 Net Banking", use_container_width=True):
            st.info("Net Banking integration coming soon!")
    with col2:
        if st.button("📲 Wallet", use_container_width=True):
            st.info("Digital Wallet integration coming soon!")
    with col3:
        if st.button("🎫 EMI", use_container_width=True):
            st.info("EMI options coming soon!")


def _process_card_payment(booking, cardholder, card_last4):
    """Process card payment."""
    with st.spinner("🔄 Processing payment..."):
        time.sleep(2)  # Simulate payment processing
        
        try:
            # Create payment record
            payment_id = create_payment(
                booking["id"],
                booking["user_id"],
                booking["amount"],
                f"Credit Card (****{card_last4})"
            )
            
            # Simulate successful payment
            transaction_ref = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{booking['id']}"
            update_payment_status(payment_id, "completed", transaction_ref)
            
            # Activate the booking
            activate_booking(booking["booking_ref"])
            
            # Send notification
            user = get_user(booking["user_id"])
            send_notification(
                booking["user_id"],
                "payment_confirmed",
                "Payment Successful ✅",
                f"Your parking booking {booking['booking_ref']} is confirmed for {booking['from_date']}",
                "push"
            )
            
            # Success message
            st.success("✅ Payment Successful!")
            st.balloons()
            
            st.markdown(f"""
            <div style='background:#1e222c;border-radius:8px;padding:16px;margin-top:1rem;border:1px solid #22c55e'>
                <div style='color:#22c55e;font-weight:700;margin-bottom:8px'>Payment Confirmed</div>
                <div style='font-size:13px;color:#9aa0b4;line-height:1.6'>
                    <div>✅ Booking Reference: <code>{booking["booking_ref"]}</code></div>
                    <div>✅ Amount: ₹{booking["amount"]:.2f}</div>
                    <div>✅ Slot: {booking["slot_code"]} (Floor {booking["floor"]})</div>
                    <div>✅ Date: {booking["from_date"]}</div>
                    <div>✅ Time: {booking["from_time"]} - {booking["to_time"]}</div>
                    <div style='margin-top:8px;font-size:11px'>Transaction ID: {transaction_ref}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 View Booking", use_container_width=True):
                    st.switch_page("pages/user_ui_updated.py")
            with col2:
                if st.button("📥 Download Receipt", use_container_width=True):
                    st.info("Receipt download feature coming soon!")
        
        except Exception as e:
            st.error(f"❌ Payment failed: {str(e)}")
            st.info("Please try again or contact support.")


def _process_upi_payment(booking, upi_id):
    """Process UPI payment."""
    with st.spinner("🔄 Redirecting to UPI app..."):
        time.sleep(2)  # Simulate UPI redirect
        
        try:
            # Create payment record
            payment_id = create_payment(
                booking["id"],
                booking["user_id"],
                booking["amount"],
                f"UPI ({upi_id})"
            )
            
            # Simulate successful UPI payment
            transaction_ref = f"UPI{datetime.now().strftime('%Y%m%d%H%M%S')}{booking['id']}"
            update_payment_status(payment_id, "completed", transaction_ref)
            
            # Activate the booking
            activate_booking(booking["booking_ref"])
            
            # Send notification
            user = get_user(booking["user_id"])
            send_notification(
                booking["user_id"],
                "payment_confirmed",
                "Payment Successful ✅",
                f"Your parking booking {booking['booking_ref']} is confirmed for {booking['from_date']}",
                "push"
            )
            
            # Success message
            st.success("✅ UPI Payment Successful!")
            st.balloons()
            
            st.markdown(f"""
            <div style='background:#1e222c;border-radius:8px;padding:16px;margin-top:1rem;border:1px solid #22c55e'>
                <div style='color:#22c55e;font-weight:700;margin-bottom:8px'>Payment Confirmed via UPI</div>
                <div style='font-size:13px;color:#9aa0b4;line-height:1.6'>
                    <div>✅ Booking Reference: <code>{booking["booking_ref"]}</code></div>
                    <div>✅ UPI ID: {upi_id}</div>
                    <div>✅ Amount: ₹{booking["amount"]:.2f}</div>
                    <div>✅ Slot: {booking["slot_code"]} (Floor {booking["floor"]})</div>
                    <div>✅ Date: {booking["from_date"]}</div>
                    <div style='margin-top:8px;font-size:11px'>Transaction ID: {transaction_ref}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 View Booking", use_container_width=True):
                    st.switch_page("pages/user_ui_updated.py")
            with col2:
                if st.button("📥 Download Receipt", use_container_width=True):
                    st.info("Receipt download feature coming soon!")
        
        except Exception as e:
            st.error(f"❌ Payment failed: {str(e)}")
            st.info("Please try again or contact support.")
