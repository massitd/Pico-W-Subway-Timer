from LCD_1inch8 import LCD_1inch8
import framebuf
import struct
import network
import time
from secrets import WIFI_SSID, WIFI_PASSWORD
import urequests as requests


lcd = LCD_1inch8()

# connect the wifi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        attempt = 0
        while not wlan.isconnected() and attempt < 10:
            time.sleep(1)
            attempt += 1

    draw_wifi_status(wlan.isconnected())  # ← draw red circle if not connected

    if wlan.isconnected():
        print("Connected:", wlan.ifconfig())
    else:
        print("Failed to connect")

connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# fetch MBTA data from my URL

def fetch_mbta_data():
    try:
        url = "https://mbta-api-spring-sunset-5820.fly.dev/api/train-times"  # ← replace with your Mac IP
        response = requests.get(url)
        print("Raw Response:", response.text)
        data = response.json()
        response.close()
        return data
    except Exception as e:
        print("Error fetching MBTA data:", e)
        return {
            'green_d': {'next_train': None, 'following_train': None},
            'green_e': {'next_train': None, 'following_train': None}
        }


# Clear the screen to a color (default: white)
def clear_screen(color=0xFFFF):
    lcd.fill(color)

# Draw a filled or outlined rectangle
def draw_rect(x, y, width, height, color, fill=True):
    lcd.rect(x, y, width, height, color, fill)

# Draw text at any position, with a color and optional size
def draw_text(text, x, y, color=0x0000, size=1):
    # size is driver-dependent; fallback to default if unsupported
    try:
        lcd.set_text_color(color)
        lcd.set_text_size(size)
    except:
        pass  # if your driver doesn't support it, ignore

    lcd.text(text, x, y, color)

# Draw unfilled circle using midpoint algorithm
def draw_circle(x0, y0, r, color):
    x = r
    y = 0
    p = 1 - r

    while x >= y:
        lcd.pixel(x0 + x, y0 + y, color)
        lcd.pixel(x0 + y, y0 + x, color)
        lcd.pixel(x0 - y, y0 + x, color)
        lcd.pixel(x0 - x, y0 + y, color)
        lcd.pixel(x0 - x, y0 - y, color)
        lcd.pixel(x0 - y, y0 - x, color)
        lcd.pixel(x0 + y, y0 - x, color)
        lcd.pixel(x0 + x, y0 - y, color)

        y += 1
        if p <= 0:
            p += 2 * y + 1
        else:
            x -= 1
            p += 2 * (y - x) + 1

# Draw filled circle by checking each pixel in a bounding square
def fill_circle(x0, y0, r, color):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x*x + y*y <= r*r:
                lcd.pixel(x0 + x, y0 + y, color)

# Draw a filled circle with an outline and optional label
def draw_icon(x, y, r, fill_color, outline_color=0x0000, label=None, label_color=0xFFFF):
    fill_circle(x, y, r, fill_color)
    draw_circle(x, y, r, outline_color)
    if label:
        # Estimate character width (8 px per char), center label inside circle
        text_width = len(label) * 8
        text_x = x - text_width // 2
        text_y = y - 4  # vertically center for 8px tall font
        draw_text(label, text_x, text_y, label_color)

# Draw stippled background with slight movement
def draw_background(offset):
    lcd.fill(0xFFFF)
    for y in range(0, 128, 6):
        for x in range(0, 160, 6):
            if (x + y + offset) % 12 < 6:
                lcd.rect(x, y, 4, 4, 0xC618, True)
    lcd.show()

# wifi helper drawing
def draw_wifi_status(connected):
    if not connected:
        # small red circle in top-right corner (e.g., 150x10)
        fill_circle(150, 10, 5, 0xF800)  # 0xF800 = pure red in BGR565


# main refresh loop
def draw_ui(data):
    clear_screen()

    d1 = data['green_d']['next_train']
    d2 = data['green_d']['following_train']
    d1_min = f"{d1['minutes_away']} min" if d1 else "no train"
    d2_min = f"{d2['minutes_away']} min" if d2 else "no train"

    e1 = data['green_e']['next_train']
    e2 = data['green_e']['following_train']
    e1_min = f"{e1['minutes_away']} min" if e1 else "no train"
    e2_min = f"{e2['minutes_away']} min" if e2 else "no train"

    clear_screen()

    draw_rect(0, 0, 160, 25, 0x6006)
    draw_text("Government Center", 10, 8, 0x0000)
    draw_rect(0, 25, 160, 1, 0x0000)

    draw_text("Union Square", 30, 40)
    draw_text(d1_min + ",", 45, 60)
    draw_text(d2_min, 95, 60)

    draw_text("Medford/Tufts", 30, 85)
    draw_text(e1_min + ",", 45, 105)
    draw_text(e2_min, 95, 105)

    draw_icon(x=15, y=42, r=10, fill_color=0xE007, outline_color=0x0000, label="D", label_color=0x0000)
    draw_icon(x=15, y=88, r=10, fill_color=0xE007, outline_color=0x0000, label="E", label_color=0x0000)

    lcd.show()

# Main loop
while True:
    for offset in range(0, 18, 2):  # Animate background first
        draw_background(offset)
        time.sleep(0.07)

    data = fetch_mbta_data()       # Fetch data *after* animation
    draw_ui(data)                  # Then draw main UI

    time.sleep(15)  # Wait before next refresh