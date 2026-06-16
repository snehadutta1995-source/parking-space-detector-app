"""Email helpers for payment OTP delivery."""

import argparse
from configparser import ConfigParser
from email.message import EmailMessage
from pathlib import Path
import os
import smtplib
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
EMAIL_CONFIG_PATH = BASE_DIR / "config" / "email.ini"
EMAIL_LOCAL_CONFIG_PATH = BASE_DIR / "config" / "email.local.ini"
STREAMLIT_SECRET_PATHS = (
    BASE_DIR / ".streamlit" / "secrets.toml",
    Path.home() / ".streamlit" / "secrets.toml",
)
STREAMLIT_CLOUD_MARKERS = (
    "STREAMLIT_CLOUD",
    "STREAMLIT_SHARING_MODE",
    "STREAMLIT_RUNTIME_ENV",
)
_CLI_ARGS = None


def _load_email_config():
    parser = ConfigParser()
    parser.read([EMAIL_CONFIG_PATH, EMAIL_LOCAL_CONFIG_PATH], encoding="utf-8")
    return parser


def _get_cli_args():
    global _CLI_ARGS
    if _CLI_ARGS is not None:
        return _CLI_ARGS

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--smtpUsername")
    parser.add_argument("--smtpPassword")
    parser.add_argument("--emailFrom")
    _CLI_ARGS, _ = parser.parse_known_args(sys.argv[1:])
    return _CLI_ARGS


def _get_cli_value(key):
    value = getattr(_get_cli_args(), key, None)
    return str(value or "").strip()


def _should_try_streamlit_secrets():
    if any(path.exists() for path in STREAMLIT_SECRET_PATHS):
        return True
    return any(os.environ.get(marker) for marker in STREAMLIT_CLOUD_MARKERS)


def _get_streamlit_email_secret(key):
    if not _should_try_streamlit_secrets():
        return ""

    try:
        import streamlit as st

        email_secrets = st.secrets.get("email", {})
        return str(email_secrets.get(key, "") or "").strip()
    except Exception:
        return ""


def _get_runtime_value(*keys):
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value.strip()
    return ""


def _get_config_value(config, section, key, fallback=""):
    return config.get(section, key, fallback=fallback).strip()


def _resolve_secret_value(config, section, key, *env_keys):
    return (
        _get_cli_value(key)
        or _get_runtime_value(*env_keys)
        or _get_streamlit_email_secret(key)
        or _get_config_value(config, section, key)
    )


def _split_recipients(value):
    normalized = (value or "").replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _resolve_recipients(config_value, booking):
    recipients = []
    for recipient in _split_recipients(config_value):
        if recipient.lower() in {"booking_user", "user_email", "registered_user"}:
            booking_email = (booking.get("email") or "").strip()
            if booking_email:
                recipients.append(booking_email)
        else:
            recipients.append(recipient)
    return recipients


def send_payment_otp_email(otp, booking, card_type, card_last4):
    """Send the payment OTP by SMTP using config/email.ini settings."""
    config = _load_email_config()
    if not config.has_section("smtp") or not config.has_section("message"):
        return False, "Email configuration is missing smtp or message settings."

    smtp_host = config.get("smtp", "smtpHost", fallback="").strip()
    smtp_port = config.getint("smtp", "smtpPort", fallback=0)
    smtp_user = _resolve_secret_value(
        config,
        "smtp",
        "smtpUsername",
        "SMTP_USERNAME",
        "SMTP_USER",
        "EMAIL_SMTP_USERNAME",
        "smtpUsername",
    )
    smtp_password = _resolve_secret_value(
        config,
        "smtp",
        "smtpPassword",
        "SMTP_PASSWORD",
        "EMAIL_SMTP_PASSWORD",
        "smtpPassword",
    )
    smtp_use_tls = config.getboolean("smtp", "smtpUseTls", fallback=True)
    smtp_timeout = config.getint("smtp", "smtpTimeoutSeconds", fallback=20)

    email_from = (
        _get_cli_value("emailFrom")
        or _get_runtime_value("EMAIL_FROM", "SMTP_EMAIL_FROM", "emailFrom")
        or _get_streamlit_email_secret("emailFrom")
        or _get_config_value(config, "message", "emailFrom")
        or smtp_user
    )
    email_from_name = config.get("message", "emailFromName", fallback="").strip()
    email_to = _resolve_recipients(config.get("message", "emailTo", fallback=""), booking)
    email_bcc = _split_recipients(config.get("message", "emailBcc", fallback=""))
    subject = config.get("message", "subject", fallback="SlotX Payment OTP").strip()

    missing = []
    if not smtp_host:
        missing.append("smtpHost")
    if not smtp_port:
        missing.append("smtpPort")
    if not smtp_user:
        missing.append("smtpUsername")
    if not smtp_password:
        missing.append("smtpPassword")
    if not email_from:
        missing.append("emailFrom")
    if not email_to:
        missing.append("emailTo")
    if missing:
        return False, f"Email configuration is incomplete: {', '.join(missing)}."

    booking_ref = booking.get("booking_ref", "your booking")
    amount = booking.get("amount", 0)
    msg = EmailMessage()
    msg["Subject"] = f"{subject} with card ending xxx{card_last4}"
    msg["From"] = f"{email_from_name} <{email_from}>" if email_from_name else email_from
    msg["To"] = ", ".join(email_to)
    if email_bcc:
        msg["Bcc"] = ", ".join(email_bcc)
    msg.set_content(
        "\n".join(
            [
                "The Payment OTP is:",
                "",
                str(otp),
                "",
                f"Booking reference: {booking_ref}",
                f"Payment amount: Rs. {amount:.2f}",
                f"Card: {card_type} ending xxx{card_last4}",
                "",
                "Use this OTP to complete your parking payment.",
            ]
        )
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as exc:
        return False, f"Unable to send OTP email: {exc}"

    return True, "OTP email sent successfully."
