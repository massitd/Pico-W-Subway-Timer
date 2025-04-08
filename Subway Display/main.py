import picographics
import jpegdec
import time
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_INKY_PACK

display = PicoGraphics(display=DISPLAY_INKY_PACK)

def clear():
    display.set_pen(15)
    display.clear()

clear()

# you can change the update speed here!
# it goes from 0 (slowest) to 3 (fastest)
display.set_update_speed(3)

def imgDisplay():
    # Create a new JPEG decoder for our PicoGraphics
    j = jpegdec.JPEG(display)
    j.open_file("ticon.jpg")
    j.decode()
    j.open_file("busicon.jpg")
    j.decode(0, 65)


imgDisplay()

def txtDisplay():
    display.set_pen(0)
    display.text("inbounds \n5 minutes", 65, 10, 240, 3)
    display.text("to kenmore \n10 minutes", 65, 75, 240, 3)
    display.update()
    
txtDisplay()

display.update()