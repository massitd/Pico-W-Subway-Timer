from PIL import Image
import os
import struct

input_folder = "./images"
output_folder = "./converted"
DISPLAY_WIDTH = 160
DISPLAY_HEIGHT = 128

def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        print(f"🔄 Converting {filename}...")

        img = Image.open(os.path.join(input_folder, filename)).convert("RGB")
        img.thumbnail((DISPLAY_WIDTH, DISPLAY_HEIGHT))  # fit inside screen
        width, height = img.size

        buf = bytearray()
        buf += struct.pack("<HH", width, height)  # 4-byte header: width, height (little-endian)

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                rgb565 = rgb888_to_rgb565(r, g, b)
                buf.append((rgb565 >> 8) & 0xFF)
                buf.append(rgb565 & 0xFF)

        out_name = os.path.splitext(filename)[0] + ".raw"
        with open(os.path.join(output_folder, out_name), "wb") as f:
            f.write(buf)

        print(f"✅ Saved: {out_name} ({width}x{height})")
