#!/usr/bin/python
from threading import Thread
import RPi.GPIO as GPIO
import time

'''
test the wheel encoders
http://guy.carpenter.id.au/gaugette/2013/01/14/rotary-encoder-library-for-the-raspberry-pi/

Motor dreht mit 6200, erste getriebe setzt um auf 177!

6200 U/m -> 103 U/s
177 U/m -> 2.95 U/s

Laut Datenblatt: 14 Pole, 7 Pulse pro U

14 Pole machen doch aber 28 Flanken pro U ?!

-> Bei voller Drehzahl liegen vorne 177 U/s an, hinten 6200 U/s
6200 / 177 == 35.028, d.h. eine volle Umdrehung des Rades NACH Getriebe müsste
35.028 * 7 = 245 Pulse haben

Zähle per Umdrehung ca. 1500 Umdrehungen, was ca. 35*14*3 (Übersetzung, #Pole, Faktor) entspricht (1470))
'''

GPIO.setmode(GPIO.BOARD)

ENC1A = 12
ENC1B = 16

#GPIO.setup(ENC1A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(ENC1B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(ENC1A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENC1B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

def check_encoder(a,b,old_seq,cnt,direction):
    seq = get_seq(not GPIO.input(a), not GPIO.input(b))

    delta = (seq-old_seq) % 4

    if delta == 0:
        pass # nothing happened
    elif delta == 1:
        #print "%08d - Forward" % cnt # one step
        direction = 1
        cnt += 1
    elif delta == 2:
        cnt += 2*direction
        #print "%08d - Two steps" % cnt # clockwise OR counter-clockwise
    elif delta == 3:
        direction = -1
        #print "%08d - Backward" % cnt
        cnt -= 1

    return seq,cnt,direction


seq=0
cnt=0
direction=0

ss = time.time()

while True:
    seq,cnt,direction = check_encoder(ENC1A, ENC1B,seq,cnt,direction)

    if time.time() - ss > 2:
        u = cnt/float(35*14*3)
        m = u*0.265
        print "%08d\t%d\t%.2f rot, %.3f m" % (cnt,direction, u, m)
        ss = time.time()



