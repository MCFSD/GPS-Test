import serial

# Replace 'COM4' with your UM982 COM port
COM_PORT = 'COM4'
BAUD_RATE = 115200

def parse_lat_lon(lat, ns, lon, ew):
    """Convert NMEA lat/lon from ddmm.mmmm format to decimal degrees."""
    try:
        lat_deg = float(lat[:2])
        lat_min = float(lat[2:])
        lon_deg = float(lon[:3])
        lon_min = float(lon[3:])

        lat_dd = lat_deg + lat_min / 60
        lon_dd = lon_deg + lon_min / 60

        if ns == "S":
            lat_dd = -lat_dd
        if ew == "W":
            lon_dd = -lon_dd

        return lat_dd, lon_dd
    except:
        return None, None

def parse_GGA(fields):
    """Parse GGA (fix info) sentence."""
    if len(fields) < 15:
        return None

    time_utc = fields[1]
    lat = fields[2]
    ns = fields[3]
    lon = fields[4]
    ew = fields[5]
    fix_quality = fields[6]
    num_sats = fields[7]
    hdop = fields[8]
    altitude = fields[9]

    lat_dd, lon_dd = parse_lat_lon(lat, ns, lon, ew)

    return {
        "time_utc": time_utc,
        "lat": lat_dd,
        "lon": lon_dd,
        "fix_quality": fix_quality,
        "sats": num_sats,
        "hdop": hdop,
        "altitude_m": altitude,
    }

def parse_RMC(fields):
    """Parse RMC (recommended minimum) sentence."""
    if len(fields) < 12:
        return None

    status = fields[2]
    lat = fields[3]
    ns = fields[4]
    lon = fields[5]
    ew = fields[6]
    speed_knots = fields[7]
    course = fields[8]

    lat_dd, lon_dd = parse_lat_lon(lat, ns, lon, ew)

    return {
        "status": status,
        "lat": lat_dd,
        "lon": lon_dd,
        "speed_knots": speed_knots,
        "course_deg": course,
    }


# ---- MAIN SERIAL LOOP ----

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {COM_PORT} at {BAUD_RATE} baud\n")
except Exception as e:
    print("Failed to connect:", e)
    exit()

while True:
    try:
        line = ser.readline().decode('ascii', errors='ignore').strip()

        if not line:
            continue

        # Only handle GGA and RMC
        if "$GPGGA" in line or "$GNGGA" in line:
            fields = line.split(",")
            data = parse_GGA(fields)
            if data:
                print(f"[GGA] Lat: {data['lat']}, Lon: {data['lon']}, "
                      f"Sats: {data['sats']}, Fix: {data['fix_quality']}, "
                      f"Alt: {data['altitude_m']} m, HDOP: {data['hdop']}")

        elif "$GPRMC" in line or "$GNRMC" in line:
            fields = line.split(",")
            data = parse_RMC(fields)
            if data:
                print(f"[RMC] Lat: {data['lat']}, Lon: {data['lon']}, "
                      f"Speed: {data['speed_knots']} kn, Course: {data['course_deg']}°")

    except KeyboardInterrupt:
        print("Exiting...")
        break
