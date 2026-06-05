"""
ParkSync — Enhanced Database layer (SQLite via sqlite3)
Includes waitlist, entry/exit logs, notifications, overstay alerts, and payment processing.
"""

import sqlite3
import hashlib
import os
import uuid
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "parksync.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    UNIQUE NOT NULL,
    password    TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    email       TEXT,
    phone       TEXT,
    role        TEXT    NOT NULL DEFAULT 'user',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS parking_slots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_code   TEXT    UNIQUE NOT NULL,
    floor       TEXT    NOT NULL,
    type        TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'vacant',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_ref TEXT    UNIQUE NOT NULL,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    slot_id     INTEGER NOT NULL REFERENCES parking_slots(id),
    vehicle_no  TEXT    NOT NULL,
    from_time   TEXT    NOT NULL,
    to_time     TEXT    NOT NULL,
    from_date   TEXT    NOT NULL DEFAULT (date('now')),
    duration_hr INTEGER NOT NULL DEFAULT 1,
    amount      REAL    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    booked_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id      INTEGER NOT NULL REFERENCES bookings(id),
    payment_id      TEXT    UNIQUE NOT NULL,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    amount          REAL    NOT NULL,
    payment_method  TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
    transaction_ref TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS rates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_type TEXT   UNIQUE NOT NULL,
    rate_per_hr  REAL   NOT NULL
);

CREATE TABLE IF NOT EXISTS media_uploads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT    NOT NULL,
    file_type   TEXT    NOT NULL,
    slot_id     INTEGER REFERENCES parking_slots(id),
    uploaded_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS waitlist (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    vehicle_type TEXT   NOT NULL,
    floor       TEXT,
    requested_date TEXT NOT NULL,
    requested_time TEXT,
    preferred_duration INTEGER DEFAULT 1,
    status      TEXT    NOT NULL DEFAULT 'pending',
    position    INTEGER,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entry_exit_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id  INTEGER NOT NULL REFERENCES bookings(id),
    entry_time  TEXT,
    exit_time   TEXT,
    gate        TEXT DEFAULT 'Main',
    vehicle_photo_path TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    type        TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    channel     TEXT    NOT NULL DEFAULT 'push',
    status      TEXT    NOT NULL DEFAULT 'sent',
    sent_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS overstay_alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id  INTEGER NOT NULL REFERENCES bookings(id),
    user_id     INTEGER NOT NULL REFERENCES users(id),
    overstay_minutes INTEGER,
    penalty_amount REAL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def generate_unique_booking_ref():
    """Generate a truly unique booking reference using UUID + timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"BK{timestamp}{unique_id}"


def init_db():
    """Create tables and seed demo data if empty."""
    conn = get_conn()
    conn.executescript(SCHEMA)

    # Seed admin
    if not conn.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        conn.execute(
            "INSERT INTO users (username, password, name, email, phone, role) VALUES (?,?,?,?,?,?)",
            ("admin", hash_password("admin123"), "Admin User", "admin@parksync.in", "+91-9876543210", "admin"),
        )

    # Seed demo users
    demo_users = [
        ("user1", "pass123", "Rahul Sharma", "rahul@example.com", "+91-9123456789"),
        ("user2", "pass123", "Priya Nair",   "priya@example.com", "+91-9987654321"),
        ("user3", "pass123", "Amit Singh",   "amit@example.com",  "+91-9876543211"),
    ]
    for uname, pw, name, email, phone in demo_users:
        if not conn.execute("SELECT 1 FROM users WHERE username=?", (uname,)).fetchone():
            conn.execute(
                "INSERT INTO users (username, password, name, email, phone, role) VALUES (?,?,?,?,?,?)",
                (uname, hash_password(pw), name, email, phone, "user"),
            )

    # Seed parking slots
    import random
    random.seed(42)
    if not conn.execute("SELECT 1 FROM parking_slots").fetchone():
        slots = []
        idx = 1
        for floor in ["G", "1", "2"]:
            for pos in range(1, 9):
                slot_code = f"S{idx:02d}"
                vtype = "4-wheeler" if pos <= 5 else "2-wheeler"
                status = "vacant" if random.random() > 0.45 else "occupied"
                slots.append((slot_code, floor, vtype, status))
                idx += 1
        conn.executemany(
            "INSERT INTO parking_slots (slot_code, floor, type, status) VALUES (?,?,?,?)",
            slots,
        )

    # Seed rates
    if not conn.execute("SELECT 1 FROM rates").fetchone():
        conn.executemany(
            "INSERT INTO rates (vehicle_type, rate_per_hr) VALUES (?,?)",
            [("4-wheeler", 30.0), ("2-wheeler", 10.0)],
        )

    # Seed sample bookings (with active status)
    if not conn.execute("SELECT 1 FROM bookings").fetchone():
        u1 = conn.execute("SELECT id FROM users WHERE username='user1'").fetchone()["id"]
        u2 = conn.execute("SELECT id FROM users WHERE username='user2'").fetchone()["id"]
        s3 = conn.execute("SELECT id FROM parking_slots WHERE slot_code='S03'").fetchone()["id"]
        s14 = conn.execute("SELECT id FROM parking_slots WHERE slot_code='S14'").fetchone()["id"]
        conn.executemany(
            "INSERT INTO bookings (booking_ref, user_id, slot_id, vehicle_no, from_time, to_time, from_date, duration_hr, amount, status) VALUES (?,?,?,?,?,?,?,?,?,?)",
            [
                ("BK20250529ABC12345", u1, s3,  "MH12AB1234", "09:00", "12:00", "2025-05-29", 3, 90.0,  "active"),
                ("BK20250529DEF67890", u2, s14, "KA05CD5678", "10:00", "14:00", "2025-05-29", 4, 40.0,  "active"),
            ],
        )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def authenticate(username: str, password: str):
    """Return user row dict or None."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def register_user(username: str, password: str, full_name: str, email: str, phone: str):
    """Register a new user. Returns (ok, message)."""
    # Validate inputs
    if not username or not username.strip():
        return False, "Username cannot be empty."
    if not password or not password.strip():
        return False, "Password cannot be empty."
    if not full_name or not full_name.strip():
        return False, "Full name cannot be empty."
    
    username = username.strip()
    
    # Check if username already exists
    conn = get_conn()
    existing = conn.execute(
        "SELECT 1 FROM users WHERE username=?",
        (username,)
    ).fetchone()
    
    if existing:
        conn.close()
        return False, f"Username '{username}' is already taken."
    
    # Insert new user with role='user'
    try:
        conn.execute(
            "INSERT INTO users (username, password, name, email, phone, role) VALUES (?,?,?,?,?,?)",
            (username, hash_password(password), full_name, email or None, phone or None, "user"),
        )
        conn.commit()
        conn.close()
        return True, f"Account created successfully! You can now sign in."
    except Exception as e:
        conn.close()
        return False, f"Error creating account: {str(e)}"


def get_user(user_id: int):
    """Get user by ID."""
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id: int, name: str, email: str, phone: str):
    """Update user profile."""
    conn = get_conn()
    conn.execute(
        "UPDATE users SET name=?, email=?, phone=? WHERE id=?",
        (name, email, phone, user_id),
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# SLOTS
# ─────────────────────────────────────────────

def get_all_slots():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM parking_slots ORDER BY slot_code").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_slot_by_code(code: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM parking_slots WHERE slot_code=?", (code,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_slot(slot_code: str, floor: str, vtype: str, status: str = "vacant"):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO parking_slots (slot_code, floor, type, status) VALUES (?,?,?,?)",
            (slot_code.upper(), floor, vtype, status),
        )
        conn.commit()
        return True, "Slot added successfully."
    except sqlite3.IntegrityError:
        return False, f"Slot code '{slot_code}' already exists."
    finally:
        conn.close()


def update_slot(slot_id: int, floor: str, vtype: str, status: str):
    conn = get_conn()
    conn.execute(
        "UPDATE parking_slots SET floor=?, type=?, status=? WHERE id=?",
        (floor, vtype, status, slot_id),
    )
    conn.commit()
    conn.close()


def delete_slot(slot_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM parking_slots WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()


def toggle_slot_status(slot_id: int):
    current = get_conn().execute("SELECT status FROM parking_slots WHERE id=?", (slot_id,)).fetchone()
    if current:
        conn = get_conn()
        new_status = "vacant" if current["status"] == "occupied" else "occupied"
        conn.execute("UPDATE parking_slots SET status=? WHERE id=?", (new_status, slot_id))
        conn.commit()
        conn.close()


# ─────────────────────────────────────────────
# BOOKINGS
# ─────────────────────────────────────────────

def get_all_bookings():
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.*, u.name AS user_name, u.username, u.email, u.phone,
               p.slot_code, p.floor, p.type AS slot_type
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN parking_slots p ON b.slot_id = p.id
        ORDER BY b.booked_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_bookings(user_id: int):
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.*, p.slot_code, p.floor, p.type AS slot_type
        FROM bookings b
        JOIN parking_slots p ON b.slot_id = p.id
        WHERE b.user_id = ?
        ORDER BY b.booked_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_booking(user_id: int, slot_id: int, vehicle_no: str,
                   from_time: str, to_time: str, from_date: str, duration_hr: int, amount: float):
    """Create a booking with a unique booking reference."""
    ref = generate_unique_booking_ref()
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO bookings (booking_ref, user_id, slot_id, vehicle_no, from_time, to_time, from_date, duration_hr, amount, status) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ref, user_id, slot_id, vehicle_no.upper(), from_time, to_time, from_date, duration_hr, amount, "pending"),
        )
        conn.commit()
        return ref
    except sqlite3.IntegrityError as e:
        conn.rollback()
        # Retry with a new unique reference if collision occurs
        return create_booking(user_id, slot_id, vehicle_no, from_time, to_time, from_date, duration_hr, amount)
    finally:
        conn.close()


def get_booking_by_ref(booking_ref: str):
    """Get booking details by reference."""
    conn = get_conn()
    row = conn.execute("""
        SELECT b.*, p.slot_code, p.floor, u.name, u.email, u.phone
        FROM bookings b
        JOIN parking_slots p ON b.slot_id = p.id
        JOIN users u ON b.user_id = u.id
        WHERE b.booking_ref = ?
    """, (booking_ref,)).fetchone()
    conn.close()
    return dict(row) if row else None


def activate_booking(booking_ref: str):
    """Activate a booking after payment is completed."""
    conn = get_conn()
    row = conn.execute("SELECT slot_id FROM bookings WHERE booking_ref=?", (booking_ref,)).fetchone()
    if row:
        conn.execute("UPDATE bookings SET status='active' WHERE booking_ref=?", (booking_ref,))
        conn.execute("UPDATE parking_slots SET status='occupied' WHERE id=?", (row["slot_id"],))
        conn.commit()
    conn.close()


def cancel_booking(booking_id: int):
    conn = get_conn()
    row = conn.execute("SELECT slot_id FROM bookings WHERE id=?", (booking_id,)).fetchone()
    if row:
        conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        conn.execute("UPDATE parking_slots SET status='vacant' WHERE id=?", (row["slot_id"],))
        conn.commit()
    conn.close()


def complete_booking(booking_id: int):
    conn = get_conn()
    row = conn.execute("SELECT slot_id FROM bookings WHERE id=?", (booking_id,)).fetchone()
    if row:
        conn.execute("UPDATE bookings SET status='completed' WHERE id=?", (booking_id,))
        conn.execute("UPDATE parking_slots SET status='vacant' WHERE id=?", (row["slot_id"],))
        conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# PAYMENTS
# ─────────────────────────────────────────────

def create_payment(booking_id: int, user_id: int, amount: float, payment_method: str):
    """Create a payment record."""
    payment_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO payments (booking_id, payment_id, user_id, amount, payment_method, status) VALUES (?,?,?,?,?,?)",
        (booking_id, payment_id, user_id, amount, payment_method, "pending"),
    )
    conn.commit()
    conn.close()
    return payment_id


def get_payment(payment_id: str):
    """Get payment details."""
    conn = get_conn()
    row = conn.execute(
        "SELECT p.*, b.booking_ref FROM payments p JOIN bookings b ON p.booking_id=b.id WHERE p.payment_id=?",
        (payment_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_payment_status(payment_id: str, status: str, transaction_ref: str = None):
    """Update payment status."""
    conn = get_conn()
    completed_at = datetime.now().isoformat() if status == "completed" else None
    conn.execute(
        "UPDATE payments SET status=?, transaction_ref=?, completed_at=? WHERE payment_id=?",
        (status, transaction_ref, completed_at, payment_id),
    )
    conn.commit()
    conn.close()


def get_payment_by_booking_ref(booking_ref: str):
    """Get payment info by booking reference."""
    conn = get_conn()
    row = conn.execute(
        "SELECT p.* FROM payments p JOIN bookings b ON p.booking_id=b.id WHERE b.booking_ref=?",
        (booking_ref,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─────────────────────────────────────────────
# RATES
# ─────────────────────────────────────────────

def get_rates():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM rates").fetchall()
    conn.close()
    return {r["vehicle_type"]: r["rate_per_hr"] for r in rows}


def update_rate(vehicle_type: str, rate: float):
    conn = get_conn()
    conn.execute(
        "UPDATE rates SET rate_per_hr=? WHERE vehicle_type=?",
        (rate, vehicle_type),
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# WAITLIST
# ─────────────────────────────────────────────

def add_to_waitlist(user_id: int, vehicle_type: str, requested_date: str,
                    requested_time: Optional[str] = None, floor: Optional[str] = None, duration_hr: int = 1):
    """Add user to waitlist."""
    conn = get_conn()
    
    # Get the next position
    result = conn.execute("SELECT MAX(position) as max_pos FROM waitlist WHERE status='pending'").fetchone()
    next_pos = (result["max_pos"] or 0) + 1
    
    conn.execute(
        "INSERT INTO waitlist (user_id, vehicle_type, floor, requested_date, requested_time, preferred_duration, position, status) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, vehicle_type, floor, requested_date, requested_time, duration_hr, next_pos, "pending"),
    )
    conn.commit()
    conn.close()
    return next_pos


def get_user_waitlist_position(user_id: int):
    """Get user's position in waitlist."""
    conn = get_conn()
    row = conn.execute(
        "SELECT position FROM waitlist WHERE user_id=? AND status='pending' ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["position"] if row else None


def get_waitlist(status: str = "pending"):
    """Get all waitlist entries."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT w.*, u.name, u.email, u.phone FROM waitlist w JOIN users u ON w.user_id=u.id WHERE w.status=? ORDER BY w.position",
        (status,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_from_waitlist(waitlist_id: int):
    """Remove user from waitlist."""
    conn = get_conn()
    conn.execute("UPDATE waitlist SET status='fulfilled' WHERE id=?", (waitlist_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# ENTRY/EXIT LOGS
# ─────────────────────────────────────────────

def log_entry(booking_id: int, gate: str = "Main"):
    """Log vehicle entry."""
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM entry_exit_logs WHERE booking_id=?",
        (booking_id,),
    ).fetchone()
    
    if not row:
        conn.execute(
            "INSERT INTO entry_exit_logs (booking_id, entry_time, gate) VALUES (?,?,?)",
            (booking_id, datetime.now().isoformat(), gate),
        )
    else:
        conn.execute(
            "UPDATE entry_exit_logs SET entry_time=? WHERE booking_id=?",
            (datetime.now().isoformat(), booking_id),
        )
    conn.commit()
    conn.close()


def log_exit(booking_id: int):
    """Log vehicle exit."""
    conn = get_conn()
    conn.execute(
        "UPDATE entry_exit_logs SET exit_time=? WHERE booking_id=?",
        (datetime.now().isoformat(), booking_id),
    )
    conn.commit()
    conn.close()


def log_entry_by_ref(booking_ref: str, gate: str = "Main"):
    """Log vehicle entry using a booking reference. Returns (ok, message)."""
    booking_ref = (booking_ref or "").strip()
    if not booking_ref:
        return False, "Please enter a booking reference."
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM bookings WHERE booking_ref=?", (booking_ref,)
    ).fetchone()
    conn.close()
    if not row:
        return False, f"No booking found for reference '{booking_ref}'."
    log_entry(row["id"], gate)
    return True, f"Entry logged for {booking_ref} at {gate} gate."


def log_exit_by_ref(booking_ref: str):
    """Log vehicle exit using a booking reference. Returns (ok, message)."""
    booking_ref = (booking_ref or "").strip()
    if not booking_ref:
        return False, "Please enter a booking reference."
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM bookings WHERE booking_ref=?", (booking_ref,)
    ).fetchone()
    if not row:
        conn.close()
        return False, f"No booking found for reference '{booking_ref}'."
    entry = conn.execute(
        "SELECT id FROM entry_exit_logs WHERE booking_id=?", (row["id"],)
    ).fetchone()
    conn.close()
    if not entry:
        return False, f"No entry recorded for '{booking_ref}'. Log entry first."
    log_exit(row["id"])
    return True, f"Exit logged for {booking_ref}."


def get_entry_exit_logs(days: int = 7):
    """Get recent entry/exit logs."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT l.*, b.vehicle_no, b.slot_id, p.slot_code, u.name
        FROM entry_exit_logs l
        JOIN bookings b ON l.booking_id = b.id
        JOIN parking_slots p ON b.slot_id = p.id
        JOIN users u ON b.user_id = u.id
        WHERE date(l.created_at) >= date('now', '-' || ? || ' days')
        ORDER BY l.created_at DESC
    """, (days,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

def send_notification(user_id: int, notification_type: str, title: str, message: str, channel: str = "push"):
    """Send notification to user."""
    conn = get_conn()
    conn.execute(
        "INSERT INTO notifications (user_id, type, title, message, channel) VALUES (?,?,?,?,?)",
        (user_id, notification_type, title, message, channel),
    )
    conn.commit()
    conn.close()


def get_user_notifications(user_id: int, limit: int = 10):
    """Get user notifications."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY sent_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notification_read(notification_id: int):
    """Mark notification as read."""
    conn = get_conn()
    conn.execute("UPDATE notifications SET status='read' WHERE id=?", (notification_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# OVERSTAY ALERTS
# ─────────────────────────────────────────────

def create_overstay_alert(booking_id: int, user_id: int, overstay_minutes: int):
    """Create overstay alert and calculate penalty."""
    penalty_rate = 5.0  # ₹5 per minute overstay
    penalty_amount = (overstay_minutes * penalty_rate)
    
    conn = get_conn()
    conn.execute(
        "INSERT INTO overstay_alerts (booking_id, user_id, overstay_minutes, penalty_amount) VALUES (?,?,?,?)",
        (booking_id, user_id, overstay_minutes, penalty_amount),
    )
    conn.commit()
    conn.close()
    return penalty_amount


def get_overstay_alerts(status: str = "pending"):
    """Get overstay alerts."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT a.*, b.vehicle_no, b.booking_ref, u.name, u.email FROM overstay_alerts a JOIN bookings b ON a.booking_id=b.id JOIN users u ON a.user_id=u.id WHERE a.status=? ORDER BY a.created_at DESC",
        (status,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resolve_overstay_alert(alert_id: int):
    """Mark overstay alert as resolved."""
    conn = get_conn()
    conn.execute("UPDATE overstay_alerts SET status='resolved' WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# MEDIA
# ─────────────────────────────────────────────

def save_media_record(filename: str, file_type: str, slot_id=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO media_uploads (filename, file_type, slot_id) VALUES (?,?,?)",
        (filename, file_type, slot_id),
    )
    conn.commit()
    conn.close()


def get_all_media():
    conn = get_conn()
    rows = conn.execute("""
        SELECT m.*, p.slot_code
        FROM media_uploads m
        LEFT JOIN parking_slots p ON m.slot_id = p.id
        ORDER BY m.uploaded_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# ANALYTICS HELPERS
# ─────────────────────────────────────────────

def get_analytics():
    conn = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM parking_slots").fetchone()[0]
    vacant  = conn.execute("SELECT COUNT(*) FROM parking_slots WHERE status='vacant'").fetchone()[0]
    occ     = conn.execute("SELECT COUNT(*) FROM parking_slots WHERE status='occupied'").fetchone()[0]
    t_books = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    active  = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='active'").fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM bookings WHERE status!='cancelled'").fetchone()[0]
    today   = datetime.now().strftime("%Y-%m-%d")
    today_r = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM bookings WHERE from_date=? AND status!='cancelled'",
        (today,),
    ).fetchone()[0]
    by_floor = conn.execute("""
        SELECT floor,
               COUNT(*) as total,
               SUM(CASE WHEN status='vacant' THEN 1 ELSE 0 END) as vacant
        FROM parking_slots GROUP BY floor
    """).fetchall()
    by_type = conn.execute("""
        SELECT type,
               COUNT(*) as total,
               SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) as occupied
        FROM parking_slots GROUP BY type
    """).fetchall()
    conn.close()
    return {
        "total": total, "vacant": vacant, "occupied": occ,
        "total_bookings": t_books, "active_bookings": active,
        "total_revenue": revenue, "today_revenue": today_r,
        "by_floor": [dict(r) for r in by_floor],
        "by_type":  [dict(r) for r in by_type],
    }


def get_revenue_by_period(period: str = "week"):
    """Get revenue grouped by day or week."""
    conn = get_conn()
    
    if period == "day":
        query = """
        SELECT DATE(booked_at) as period, SUM(amount) as revenue, COUNT(*) as bookings
        FROM bookings WHERE status!='cancelled'
        GROUP BY DATE(booked_at) ORDER BY period DESC LIMIT 30
        """
    elif period == "week":
        query = """
        SELECT strftime('%Y-W%W', booked_at) as period, SUM(amount) as revenue, COUNT(*) as bookings
        FROM bookings WHERE status!='cancelled'
        GROUP BY strftime('%Y-W%W', booked_at) ORDER BY period DESC LIMIT 12
        """
    else:  # month
        query = """
        SELECT strftime('%Y-%m', booked_at) as period, SUM(amount) as revenue, COUNT(*) as bookings
        FROM bookings WHERE status!='cancelled'
        GROUP BY strftime('%Y-%m', booked_at) ORDER BY period DESC LIMIT 12
        """
    
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]
