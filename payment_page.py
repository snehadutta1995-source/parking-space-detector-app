"""
SLotX — Payment Gateway (Mock)
Card-only payment system. Payments are accepted ONLY for cards present in:
    payments/valid-credit-card.csv   (Credit cards)
    payments/valid-debit-card.csv    (Debit cards)
CSV format (pipe delimited):  cardNumber|cvv|expiry|cardHolderName|otp
"""

import csv
import streamlit as st
from datetime import datetime
import time
from pathlib import Path

from utils.database import (
    get_booking_by_ref, activate_booking, extend_booking,
    create_payment, update_payment_status, send_notification, get_user,
    now_ist,
)
from utils.email_service import send_payment_otp_email
from utils.styles import apply_theme

BASE_DIR = Path(__file__).resolve().parent
CREDIT_CARD_CSV = BASE_DIR / "payments" / "valid-credit-card.csv"
DEBIT_CARD_CSV = BASE_DIR / "payments" / "valid-debit-card.csv"


# ─────────────────────────────────────────────
# Mock card store
# ─────────────────────────────────────────────
def _load_valid_cards(csv_path: Path):
    """Load valid cards from a pipe-delimited CSV into a dict keyed by card number."""
    cards = {}
    if not csv_path.exists():
        return cards
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            number = (row.get("cardNumber") or "").strip()
            if not number:
                continue
            cards[number] = {
                "cvv": (row.get("cvv") or "").strip(),
                "expiry": (row.get("expiry") or "").strip(),
                "cardHolderName": (row.get("cardHolderName") or "").strip(),
                "otp": (row.get("otp") or "").strip(),
            }
    return cards


def _load_card_rows(csv_path: Path):
    """Load valid card rows from a pipe-delimited CSV for tabular display."""
    rows = []
    if not csv_path.exists():
        return rows

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            rows.append({
                "Card Number": (row.get("cardNumber") or "").strip(),
                "CVV": (row.get("cvv") or "").strip(),
                "Expiry": (row.get("expiry") or "").strip(),
                "Cardholder Name": (row.get("cardHolderName") or "").strip(),
            })
    return rows


def _normalize_number(card_number: str) -> str:
    return (card_number or "").replace(" ", "").replace("-", "").strip()


def verify_card_details(card_type, cardholder, card_number, expiry, cvv):
    """
    Validate the entered card against the mock store.
    Returns (ok, message, expected_otp).
    """
    csv_path = CREDIT_CARD_CSV if card_type == "Credit Card" else DEBIT_CARD_CSV
    cards = _load_valid_cards(csv_path)
    number = _normalize_number(card_number)

    if not number:
        return False, "Please enter a card number.", None

    record = cards.get(number)
    if record is None:
        return False, "Card not recognized. This card is not authorized for payments.", None

    if cvv.strip() != record["cvv"]:
        return False, "Invalid CVV for this card.", None

    if expiry.strip() != record["expiry"]:
        return False, "Invalid expiry date for this card.", None

    if cardholder.strip().lower() != record["cardHolderName"].lower():
        return False, "Cardholder name does not match our records.", None

    return True, "Card verified. An OTP has been sent to your registered email address.", record["otp"]


# ─────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────
def render_payment(booking_ref: str = None):
    """Main payment gateway page. booking_ref falls back to session state.

    Also handles overstay-extension payments: when st.session_state['pay_extension']
    is set (booking_ref, alert_id, hours, cost, new_end), the page charges the
    extension cost instead of the booking's base amount, and on success extends
    the booking's schedule (extend_booking) instead of activating it."""
    st.markdown(apply_theme(), unsafe_allow_html=True)

    extension = st.session_state.get("pay_extension")
    if booking_ref is None:
        booking_ref = (extension or {}).get("booking_ref") or st.session_state.get("pay_booking_ref")

    def _go_back(to_my_bookings: bool = False):
        st.session_state.pop("pay_booking_ref", None)
        st.session_state.pop("pay_extension", None)
        st.session_state.pop("pay_otp_stage", None)
        st.session_state.pop("pay_expected_otp", None)
        st.session_state.pop("pay_card_meta", None)
        if to_my_bookings:
            st.session_state["user_current_page"] = "bookings"

    if not booking_ref:
        st.error("❌ No booking reference found. Please start a new booking.")
        if st.button("← Go Back to Bookings"):
            _go_back()
            st.rerun()
        return

    booking = get_booking_by_ref(booking_ref)
    if not booking:
        st.error(f"❌ Booking '{booking_ref}' not found.")
        if st.button("← Go Back to Bookings"):
            _go_back()
            st.rerun()
        return

    if not extension and booking["status"] in ("active", "overstay"):
        # Payment already completed — route straight to My Bookings.
        _go_back(to_my_bookings=True)
        st.rerun()
        return

    amount_due = extension["cost"] if extension else booking["amount"]

    # Header
    subtitle = "Pay to extend your parking booking" if extension else "Complete your parking booking payment"
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#4f7cff,#22c55e);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:20px'>💳</div>
      <div>
        <h1 style='margin:0;font-family:Syne,sans-serif'>Secure Payment</h1>
        <div style='font-size:13px;color:var(--text2)'>{subtitle}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Bookings"):
        _go_back()
        st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Booking Summary")
        summary_cols = st.columns(2)
        with summary_cols[0]:
            st.metric("Booking Ref", booking["booking_ref"])
            st.metric("Slot", booking["slot_code"])
        with summary_cols[1]:
            if extension:
                new_end_dt = datetime.fromisoformat(extension["new_end"])
                st.metric("Extend by", f"{extension['hours']}h")
                st.metric("New checkout", new_end_dt.strftime("%H:%M"))
            else:
                st.metric("Date", booking["from_date"])
                st.metric("Duration", f"{booking['duration_hr']}h")

        st.divider()
        _render_card_payment(booking, amount_due, extension)

    with col2:
        st.markdown("### Amount Due")
        amount_label = "Extension Charge" if extension else "Base Amount"
        st.markdown(f"""
        <div style='background:var(--bg3);border-radius:10px;padding:16px;border:1px solid var(--border)'>
            <div style='font-size:13px;color:var(--text2);margin-bottom:8px'>
                <div style='display:flex;justify-content:space-between;padding:4px 0'>
                    <span>{amount_label}</span>
                    <span>₹{amount_due:.2f}</span>
                </div>
            </div>
            <div style='border-top:1px solid var(--border);padding-top:8px;margin-top:8px'>
                <div style='display:flex;justify-content:space-between;padding:4px 0;font-size:16px;font-weight:700'>
                    <span>Total</span>
                    <span style='color:#22c55e'>₹{amount_due:.2f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.info("🔒 Your payment is secure and encrypted.")


def _render_card_payment(booking, amount_due, extension=None):
    """Render credit/debit card payment form with OTP verification."""
    st.markdown("### Pay with Card")

    otp_stage = st.session_state.get("pay_otp_stage", False)

    # ── Step 2: OTP verification ──────────────
    if otp_stage:
        meta = st.session_state.get("pay_card_meta", {})
        card_type = meta.get("card_type", st.session_state.get("pay_card_type", "Credit Card"))
        st.success(f"✅ Card ending **{meta.get('last4', '----')}** verified.")
        st.info("📲 Enter the 6-digit OTP sent to your registered email address.")
        _render_available_cards_table(card_type)

        with st.form("otp_form"):
            otp = st.text_input("OTP", placeholder="6-digit code", max_chars=6, type="password")
            cols = st.columns(2)
            with cols[0]:
                verify = st.form_submit_button(
                    f"🔒 Verify & Pay ₹{amount_due:.2f}", use_container_width=True
                )
            with cols[1]:
                cancel = st.form_submit_button("↩ Use a different card", use_container_width=True)

        if cancel:
            st.session_state.pop("pay_otp_stage", None)
            st.session_state.pop("pay_expected_otp", None)
            st.session_state.pop("pay_card_meta", None)
            st.rerun()

        if verify:
            expected = st.session_state.get("pay_expected_otp")
            if not otp.strip():
                st.error("❌ Please enter the OTP.")
            elif otp.strip() != expected:
                st.error("❌ Incorrect OTP. Please try again.")
            else:
                _process_card_payment(booking, meta.get("cardholder", ""),
                                      meta.get("last4", ""), meta.get("card_type", "Card"),
                                      amount_due, extension)
        return

    # ── Step 1: card details ──────────────────
    card_type = st.radio(
        "Card Type", ["Credit Card", "Debit Card"], horizontal=True, key="pay_card_type"
    )
    _render_available_cards_table(card_type)

    with st.form("card_payment_form"):
        cardholder = st.text_input("Cardholder Name", placeholder="Name as on card")
        card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456", max_chars=23)

        c1, c2 = st.columns(2)
        with c1:
            expiry = st.text_input("Expiry (MM/YY)", placeholder="12/27", max_chars=5)
        with c2:
            cvv = st.text_input("CVV", placeholder="123", max_chars=4, type="password")

        submit = st.form_submit_button(
            f"Continue to Pay ₹{amount_due:.2f}", use_container_width=True
        )

    if submit:
        if not cardholder.strip():
            st.error("❌ Cardholder name is required.")
            return
        if not expiry.strip() or "/" not in expiry:
            st.error("❌ Invalid expiry date format (use MM/YY).")
            return
        if not cvv.strip():
            st.error("❌ CVV is required.")
            return

        ok, msg, expected_otp = verify_card_details(
            card_type, cardholder, card_number, expiry, cvv
        )
        if not ok:
            st.error(f"❌ {msg}")
        else:
            number = _normalize_number(card_number)
            email_booking = dict(booking)
            email_booking["amount"] = amount_due
            sent, email_msg = send_payment_otp_email(expected_otp, email_booking, card_type, number[-4:])
            if not sent:
                st.error(f"Email OTP failed: {email_msg}")
                st.info("Configure config/email.ini or config/email.local.ini, then try again.")
                return

            st.session_state["pay_otp_stage"] = True
            st.session_state["pay_expected_otp"] = expected_otp
            st.session_state["pay_card_meta"] = {
                "cardholder": cardholder.strip(),
                "last4": number[-4:],
                "card_type": card_type,
            }
            st.rerun()


def _render_available_cards_table(card_type):
    """Render the stored cards that match the selected card type."""
    csv_path = CREDIT_CARD_CSV if card_type == "Credit Card" else DEBIT_CARD_CSV
    rows = _load_card_rows(csv_path)
    table_title = "Valid Credit Cards" if card_type == "Credit Card" else "Valid Debit Cards"

    st.markdown(f"#### {table_title}")
    if not rows:
        st.warning(f"No {card_type.lower()} details found.")
        return

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _process_card_payment_legacy(booking, cardholder, card_last4, card_type):
    """Legacy payment processing flow kept for reference."""
    with st.spinner("🔄 Processing payment..."):
        time.sleep(1.5)
        try:
            payment_id = create_payment(
                booking["id"],
                booking["user_id"],
                booking["amount"],
                f"{card_type} (****{card_last4})",
            )

            transaction_ref = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{booking['id']}"
            update_payment_status(payment_id, "completed", transaction_ref)
            activate_booking(booking["booking_ref"])

            send_notification(
                booking["user_id"],
                "payment_confirmed",
                "Payment Successful ✅",
                f"Your parking booking {booking['booking_ref']} is confirmed for {booking['from_date']}",
                "push",
            )

            # Clear payment session flags
            st.session_state.pop("pay_otp_stage", None)
            st.session_state.pop("pay_expected_otp", None)
            st.session_state.pop("pay_card_meta", None)

            st.success("✅ Payment Successful!")

            st.markdown(f"""
            <div style='background:#1e222c;border-radius:8px;padding:16px;margin-top:1rem;border:1px solid #22c55e'>
                <div style='color:#22c55e;font-weight:700;margin-bottom:8px'>Payment Confirmed</div>
                <div style='font-size:13px;color:var(--text2);line-height:1.6'>
                    <div>✅ Booking Reference: <code>{booking["booking_ref"]}</code></div>
                    <div>✅ Paid via: {card_type} (****{card_last4})</div>
                    <div>✅ Amount: ₹{booking["amount"]:.2f}</div>
                    <div>✅ Slot: {booking["slot_code"]} (Floor {booking["floor"]})</div>
                    <div>✅ Date: {booking["from_date"]}</div>
                    <div>✅ Time: {booking["from_time"]} - {booking["to_time"]}</div>
                    <div style='margin-top:8px;font-size:11px'>Transaction ID: {transaction_ref}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📋 View My Bookings", use_container_width=True):
                st.session_state.pop("pay_booking_ref", None)
                st.session_state["user_current_page"] = "bookings"
                st.rerun()

        except Exception as e:
            st.error(f"❌ Payment failed: {str(e)}")
            st.info("Please try again or contact support.")


def _render_payment_processing_animation(amount):
    """Show a short payment-gateway style processing animation."""
    placeholder = st.empty()
    placeholder.markdown(f"""
    <style>
      .payment-processing-panel {{
        position: fixed;
        inset: 0;
        z-index: 999999;
        min-height: 100vh;
        width: 100vw;
        background:
          radial-gradient(circle at center, rgba(34,197,94,.16), transparent 34%),
          linear-gradient(135deg, rgba(2,6,23,.98), rgba(15,23,42,.98));
        padding: 32px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }}
      .payment-orbit {{
        position: relative;
        width: 78px;
        height: 78px;
        margin: 0 auto 16px;
        border-radius: 50%;
        background: rgba(79,124,255,.1);
        display: flex;
        align-items: center;
        justify-content: center;
      }}
      .payment-orbit::before {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 3px solid rgba(255,255,255,.12);
        border-top-color: #4f7cff;
        border-right-color: #22c55e;
        animation: paymentSpin .9s linear infinite;
      }}
      .payment-card-icon {{
        width: 42px;
        height: 28px;
        border-radius: 6px;
        background: linear-gradient(135deg, #4f7cff, #22c55e);
        box-shadow: 0 10px 24px rgba(34,197,94,.2);
      }}
      .payment-card-icon::before {{
        content: "";
        display: block;
        height: 5px;
        margin-top: 6px;
        background: rgba(2,6,23,.42);
      }}
      .payment-processing-title {{
        color: #f8fafc;
        font-weight: 800;
        font-size: 18px;
        margin-bottom: 6px;
      }}
      .payment-processing-copy {{
        color: #cbd5e1;
        font-size: 13px;
        margin-bottom: 16px;
      }}
      .payment-steps {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        width: min(460px, calc(100vw - 40px));
        max-width: 460px;
        margin: 0 auto;
      }}
      .payment-step {{
        border: 1px solid rgba(148,163,184,.22);
        border-radius: 8px;
        padding: 9px 8px;
        color: #dbeafe;
        font-size: 12px;
        background: rgba(15,23,42,.72);
        animation: paymentPulse 1.4s ease-in-out infinite;
      }}
      .payment-step:nth-child(2) {{ animation-delay: .18s; }}
      .payment-step:nth-child(3) {{ animation-delay: .36s; }}
      @media (max-width: 560px) {{
        .payment-processing-panel {{ padding: 20px; }}
        .payment-steps {{ grid-template-columns: 1fr; }}
      }}
      @keyframes paymentSpin {{
        to {{ transform: rotate(360deg); }}
      }}
      @keyframes paymentPulse {{
        0%, 100% {{ transform: translateY(0); border-color: rgba(148,163,184,.22); }}
        50% {{ transform: translateY(-2px); border-color: rgba(34,197,94,.6); }}
      }}
    </style>
    <div class="payment-processing-panel">
      <div class="payment-orbit"><div class="payment-card-icon"></div></div>
      <div class="payment-processing-title">Processing payment</div>
      <div class="payment-processing-copy">Authorizing Rs. {amount:.2f}. Please do not refresh this page.</div>
      <div class="payment-steps">
        <div class="payment-step">Validating card</div>
        <div class="payment-step">Contacting bank</div>
        <div class="payment-step">Confirming booking</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    return placeholder


def _process_card_payment(booking, cardholder, card_last4, card_type, amount_due, extension=None):
    """Process card payment after OTP verification, then route to My Bookings.

    For a normal booking payment, activates the booking (pending -> active).
    For an overstay extension payment, extends the booking's schedule instead
    (extend_booking) — the booking's own duration_hr/to_time are updated so the
    new checkout time is reflected everywhere the booking is displayed."""
    processing_panel = _render_payment_processing_animation(amount_due)
    try:
        payment_method = f"{card_type} (****{card_last4})"
        if extension:
            payment_method += f" — Overstay Extension ({extension['hours']}h)"
        payment_id = create_payment(
            booking["id"],
            booking["user_id"],
            amount_due,
            payment_method,
        )

        transaction_ref = f"TXN{now_ist().strftime('%Y%m%d%H%M%S')}{booking['id']}"
        update_payment_status(payment_id, "completed", transaction_ref)

        if extension:
            extend_booking(booking["id"], extension["alert_id"], extension["new_end"], amount_due)
            new_end_dt = datetime.fromisoformat(extension["new_end"])
            confirm_line = f"Booking <code>{booking['booking_ref']}</code> extended to {new_end_dt.strftime('%H:%M')} with transaction <code>{transaction_ref}</code>."
            notif_title = "Booking Extended"
            notif_msg = f"Your parking booking {booking['booking_ref']} has been extended to {new_end_dt.strftime('%H:%M')} on {new_end_dt.strftime('%Y-%m-%d')}"
        else:
            activate_booking(booking["booking_ref"])
            confirm_line = f"Booking <code>{booking['booking_ref']}</code> confirmed with transaction <code>{transaction_ref}</code>."
            notif_title = "Payment Successful"
            notif_msg = f"Your parking booking {booking['booking_ref']} is confirmed for {booking['from_date']}"

        send_notification(
            booking["user_id"],
            "payment_confirmed",
            notif_title,
            notif_msg,
            "push",
        )

        processing_panel.markdown(f"""
        <div style='position:fixed;inset:0;z-index:999999;min-height:100vh;width:100vw;background:linear-gradient(135deg,rgba(2,6,23,.98),rgba(16,35,26,.98));display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:32px'>
            <div style='width:78px;height:78px;border-radius:50%;background:#22c55e;color:#052e16;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;margin-bottom:18px'>✓</div>
            <div style='color:#22c55e;font-size:28px;font-weight:900;margin-bottom:8px'>Payment Successful</div>
            <div style='color:#d1fae5;font-size:13px;line-height:1.6;max-width:520px'>
                {confirm_line}<br>
                Redirecting to My Bookings...
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1.4)

        st.session_state["scroll_to_booking_ref"] = booking["booking_ref"]
        st.session_state.pop("pay_booking_ref", None)
        st.session_state.pop("pay_extension", None)
        st.session_state.pop("pay_otp_stage", None)
        st.session_state.pop("pay_expected_otp", None)
        st.session_state.pop("pay_card_meta", None)
        st.session_state["user_current_page"] = "bookings"
        st.rerun()

    except Exception as e:
        processing_panel.empty()
        st.error(f"Payment failed: {str(e)}")
        st.info("Please try again or contact support.")
