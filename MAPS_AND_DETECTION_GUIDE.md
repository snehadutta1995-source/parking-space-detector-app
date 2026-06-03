# SLotX - Maps Integration & Auto-Detection Guide

## 1️⃣ FREE GOOGLE MAPS ALTERNATIVE

### ❌ Why NOT Google Maps?
- Google Maps API requires **credit card registration**
- Free tier: $200/month credit (often exhausted quickly)
- Beyond that: $0.005 per request (expensive)
- Not truly "free"

---

## ✅ BEST FREE ALTERNATIVES

### Option 1: **Leaflet + OpenStreetMap** (RECOMMENDED)
**Cost:** Completely FREE ✓
**Installation:**
```bash
pip install folium streamlit-folium
```

**Why Choose:**
- Zero cost (forever)
- Open-source
- Community-supported
- Professional quality maps
- Works offline if needed

**Example:**
```python
import folium
from streamlit_folium import st_folium

# Create map centered on parking lot
m = folium.Map(location=[19.0760, 72.8777], zoom_start=15)

# Add parking slots as markers
folium.Marker(
    [19.0760, 72.8777],
    popup="Slot S01",
    tooltip="Vacant Slot",
    icon=folium.Icon(color='green', icon='info-sign')
).add_to(m)

st_folium(m, width=700, height=500)
```

---

### Option 2: **Folium (Python-based)**
**Cost:** Completely FREE ✓
**Best for:** Quick map creation

```python
import folium

map_center = [19.0760, 72.8777]  # Mumbai coordinates
m = folium.Map(location=map_center, zoom_start=15)

# Add heat map layer for occupancy
# Add cluster markers for slots
# Add polygon areas for floors

m.save('parking_map.html')
st.components.v1.html(open('parking_map.html', 'r').read(), height=600)
```

---

### Option 3: **Mapbox GL (Free tier available)**
**Cost:** Free for development + low traffic
**Features:** Beautiful 3D maps

```bash
pip install mapbox-gl
```

---

### Option 4: **Here Maps (Recently made free)**
**Cost:** Limited free tier (15K transactions/month)
**Features:** Good alternative to Google

```bash
pip install here-api
```

---

## 🗺️ RECOMMENDED IMPLEMENTATION FOR SLOTX

### Use: **Leaflet + OpenStreetMap**

**Features for Parking:**
1. Show parking lot floor plan
2. Color-code slots (green=vacant, red=occupied)
3. Real-time occupancy heatmap
4. Entry/exit gate locations
5. Parking rate zones

**Code Example:**
```python
import folium
from streamlit_folium import st_folium

def show_parking_map():
    # Parking lot location (example: Mumbai parking)
    parking_location = [19.0760, 72.8777]
    
    m = folium.Map(
        location=parking_location,
        zoom_start=18,
        tiles='OpenStreetMap'
    )
    
    # Add gates
    folium.Marker(
        location=[19.0760, 72.8777],
        popup="Main Gate",
        icon=folium.Icon(color='blue', icon='arrow-right')
    ).add_to(m)
    
    # Add vacant slots
    folium.CircleMarker(
        location=[19.0761, 72.8778],
        radius=8,
        popup="S01 - Vacant",
        color='green',
        fill=True,
        fillColor='green'
    ).add_to(m)
    
    # Add occupied slots
    folium.CircleMarker(
        location=[19.0762, 72.8779],
        radius=8,
        popup="S02 - Occupied",
        color='red',
        fill=True,
        fillColor='red'
    ).add_to(m)
    
    st_folium(m, width=1200, height=600)

show_parking_map()
```

---

---

# 2️⃣ AUTO-DETECTION OF VEHICLE ENTRY/EXIT

## 🚗 How to Implement Vehicle Detection

### Option 1: **ANPR (Automatic Number Plate Recognition)** ⭐ BEST
**How it works:**
- Camera captures vehicle
- OCR reads license plate
- Database lookup matches booking
- Automatic entry/exit logging

**Integration:**
```bash
pip install easyocr opencv-python
```

**Code:**
```python
import easyocr
import cv2

def detect_vehicle_entry():
    reader = easyocr.Reader(['en'])
    cap = cv2.VideoCapture(0)  # Webcam
    
    while True:
        ret, frame = cap.read()
        results = reader.readtext(frame)
        
        vehicle_no = results[0][1]  # Extract license plate
        confidence = results[0][2]
        
        if confidence > 0.8:
            # Check database for matching booking
            booking = db.get_booking_by_vehicle(vehicle_no)
            
            if booking:
                log_entry(booking['id'], gate='Main')
                st.success(f"✅ Vehicle {vehicle_no} entered")
            else:
                st.warning(f"⚠️ Unknown vehicle {vehicle_no}")
```

---

### Option 2: **QR Code Scanning** ✓ EASY
**How it works:**
- User scans QR code at gate
- Entry/exit automatically logged
- No cameras needed

```python
import qrcode
from pyzbar import pyzbar

def scan_qr_at_gate():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        decoded = pyzbar.decode(frame)
        
        for obj in decoded:
            booking_ref = obj.data.decode('utf-8')
            log_entry_by_qr(booking_ref)
            st.success(f"Entry logged: {booking_ref}")
```

---

### Option 3: **IoT Sensors** 💰
**Hardware needed:**
- Infrared motion sensors
- Magnetic door sensors
- RFID readers

**Data Flow:**
```
IoT Sensor → MQTT Broker → Database → SLotX Display
```

**Python Integration:**
```python
import paho.mqtt.client as mqtt

def on_sensor_trigger(msg):
    gate = msg['gate']
    vehicle_presence = msg['motion']
    
    if vehicle_presence:
        log_entry(gate=gate, timestamp=datetime.now())
    else:
        log_exit(gate=gate, timestamp=datetime.now())
```

---

### Option 4: **Mock/Simulation** ✓ FOR DEMO
**Best for testing without hardware:**

```python
def simulate_vehicle_entry_exit():
    st.write("### Simulate Vehicle Entry/Exit")
    
    action = st.radio("Select Action", ["Entry", "Exit"])
    booking_ref = st.selectbox("Select Booking", get_all_active_bookings())
    
    if st.button("📍 Log " + action):
        if action == "Entry":
            log_entry(booking_ref, gate='Main')
            st.success(f"✅ {booking_ref} - Entry Logged")
        else:
            log_exit(booking_ref)
            st.success(f"✅ {booking_ref} - Exit Logged")
```

---

## 🎯 RECOMMENDED APPROACH FOR SLOTX

### **Hybrid Solution (Best):**

1. **Primary:** QR Code scanning (easy, accurate, no hardware)
2. **Secondary:** Manual entry/exit logging (backup)
3. **Optional:** ANPR integration (future enhancement)
4. **Testing:** Mock simulation (development)

---

---

# 3️⃣ IMPLEMENTATION SUMMARY

### Maps Integration:
```python
# In admin_ui.py, add new page:
def _parking_map_page():
    st.markdown("## Parking Lot Map")
    show_parking_map_with_leaflet()
```

### Auto-Detection:
```python
# In admin_ui.py entry/exit page, add:
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Auto-Detection (QR Scan)")
    st.write("Scan booking QR code at gate")
    # QR scanning implementation

with col2:
    st.markdown("### Manual Entry/Exit")
    st.write("Manually log if QR fails")
    # Manual logging form
```

---

## 📦 Installation Commands

```bash
# For free maps
pip install folium streamlit-folium

# For ANPR (optional)
pip install easyocr opencv-python

# For QR scanning (optional)
pip install pyzbar

# Update requirements.txt
pip install -r requirements.txt
```

---

## 💡 Cost Comparison

| Solution | Cost | Ease | Quality |
|----------|------|------|---------|
| Google Maps | ❌ $200+/month | Easy | Excellent |
| Leaflet + OSM | ✅ Free | Medium | Very Good |
| Folium | ✅ Free | Easy | Good |
| Mapbox | ✅ Free (15K/mo) | Medium | Excellent |
| ANPR | ✅ Free (code) | Hard | Excellent |
| QR Scanning | ✅ Free | Easy | Excellent |

---

## 🎯 BEST CHOICE FOR SLOTX:
✅ **Leaflet + OpenStreetMap** (Maps)
✅ **QR Code Scanning** (Auto-Detection)
✅ **Zero Cost** ∞

---
