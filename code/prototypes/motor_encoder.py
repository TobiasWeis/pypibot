#!/usr/bin/python
from threading import Thread
import RPi.GPIO as GPIO
import time

'''
test the wheel encoders
http://guy.carpenter.id.au/gaugette/2013/01/14/rotary-encoder-library-for-the-raspberry-pi/
'''

GPIO.setmode(GPIO.BOARD)

ENC1A = 12
ENC1B = 16

#GPIO.setup(ENC1A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(ENC1B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(ENC1A, GPIO.IN)
GPIO.setup(ENC1B, GPIO.IN)

def get_seq(a,b):
    a = not a
    b = not b
    '''
    Decoder logic
    Seq B   A   A ^ B
    0   0   0   0
    1   0   1   1
    2   1   1   0
    3   1   0   1
    '''
    return (a ^ b) | b << 1

def check_encoder(a,b, name):
    old_seq = 0
    cnt = 0
    direction = 0
    while True:
        seq = get_seq(not GPIO.input(a), not GPIO.input(b))

        delta = (seq-old_seq) % 4

        if delta == 0:
            pass # nothing happened
        elif delta == 1:
            print "%08d - Forward" % cnt # one step
            direction = 1
            cnt += 1
        elif delta == 2:
            cnt += 2*direction
            print "%08d - Two steps" % cnt # clockwise OR counter-clockwise
        elif delta == 3:
            direction = -1
            print "%08d - Backward" % cnt
            cnt -= 1

        old_seq = seq


while True:
    check_encoder(ENC1A, ENC1B, "A")


