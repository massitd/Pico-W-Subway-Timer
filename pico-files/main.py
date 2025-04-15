from LCD_1inch8 import LCD_1inch8
import framebuf
import struct

lcd = LCD_1inch8()

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

# LAYOUT BELOW #
clear_screen()

# Header bar
draw_rect(0, 0, 160, 25, 0x6006)  # Green header
draw_text("Government Center", 10, 8, 0x0000)  

# Spacer
draw_rect(0, 25, 160, 1, 0x0000)

# Train data
draw_text("Union Square", 30, 40)
draw_text("4 min,", 45, 60)
draw_text("10 min", 95, 60)
draw_text("Medford/Tufts", 30, 85)
draw_text("6 min,", 45, 105)
draw_text("12 min", 95, 105)

# circle logos
draw_icon(
    x=15, y=42, r=10,
    fill_color=0xE007,     # BGR565 green
    outline_color=0x0000,  # black outline
    label="D",            # Government Center
    label_color=0x0000
)
draw_icon(
    x=15, y=88, r=10,
    fill_color=0xE007,     # BGR565 green
    outline_color=0x0000,  # black outline
    label="E",            # Government Center
    label_color=0x0000
)

lcd.show()