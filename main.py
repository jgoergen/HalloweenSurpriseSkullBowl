# portions of this code is taken from the Adafruit Crickit examples!

import time
import random
from adafruit_crickit import crickit
import neopixel
import board
import audioio

# ================== settings ===================

COLOR_SCROLL_SPEED = 4
RESET_SPEED = 5
SERVO_BASE_POSITION = 80
SERVO_TRIGGERED_POSITION = 0
TRIGGER_DEPTH = 100
NEOPIXEL_COUNT = 23
BUTTON_PIN = crickit.SIGNAL8

# ================ end settings ==================

nextChange = time.monotonic()
triggered = False
colorIndex = 0

# init

pixels = neopixel.NeoPixel(
    board.A1, 
    NEOPIXEL_COUNT, 
    brightness=1, 
    auto_write=False)
crickit.servo_1.angle = SERVO_BASE_POSITION
ss = crickit.seesaw
depthTrigger = crickit.SIGNAL8
depthEcho = crickit.SIGNAL7
ss.pin_mode(depthTrigger, ss.OUTPUT)
ss.pin_mode(depthEcho, ss.INPUT)
ss.pin_mode(BUTTON_PIN, ss.INPUT_PULLDOWN)
wavfile = "sound.wav"
f = open(wavfile, "rb")
wav = audioio.WaveFile(f)
a = audioio.AudioOut(board.A0)

# ================ utility functions =============

def usleep(microSeconds):
    time.sleep((1/1000000.0) * microSeconds)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
    
def readDepth():
    ss.digital_write(depthTrigger, False)
    usleep(2)
    ss.digital_write(depthTrigger, True)
    usleep(10)
    ss.digital_write(depthTrigger, False)
    start = time.monotonic()
    
    while not ss.digital_read(depthEcho):
        pass
        
    return time.monotonic() - start
        
# =============== end utility functions ==========

while True:
    
    # print(readDepth())

    if time.monotonic() > nextChange:
        nextChange = time.monotonic() + RESET_SPEED
        if triggered is True:
            triggered = False
            print("reset")
            crickit.servo_1.angle = SERVO_BASE_POSITION

    if triggered is False:
        # read distance from depth sensor
        if ss.digital_read(BUTTON_PIN) is True:
            print("triggered")
            triggered = True
            crickit.servo_1.angle = SERVO_TRIGGERED_POSITION
            a.play(wav)
        
        # display idle animation
        
        colorIndex += COLOR_SCROLL_SPEED
        
        if colorIndex > 255:
            colorIndex = 0
        
        for i in range(NEOPIXEL_COUNT):
            rc_index = (i * 256 // NEOPIXEL_COUNT) + colorIndex
            pixels[i] = wheel(rc_index & 255)
                
    else:
        # display triggered animation
        
        for i in range(NEOPIXEL_COUNT):
            pixels[i] = (random.randrange(255), 0, 0)
            
    time.sleep(0.05)
    pixels.show()