#!/usr/bin/python
from threading import Thread
import RPi.GPIO as GPIO
import time
import math

'''
test the wheel encoders
http://guy.carpenter.id.au/gaugette/2013/01/14/rotary-encoder-library-for-the-raspberry-pi/

Motor dreht mit 6200, erste getriebe setzt um auf 177!

6200 U/m -> 103 U/s
177 U/m -> 2.95 U/s

Laut Datenblatt: 14 Pole, 7 Pulse pro U

14 Pole machen doch aber 28 Flanken pro U ?!

-> Bei voller Drehzahl liegen vorne 177 U/s an, hinten 6200 U/s
6200 / 177 == 35.028, d.h. eine volle Umdrehung des Rades NACH Getriebe musste
35.028 * 7 = 245 Pulse haben

Zahle per Umdrehung ca. 1500 Umdrehungen, was ca. 35*14*3 (Ubersetzung, #Pole, Faktor) entspricht (1470))
'''

ENC1A = 32
ENC1B = 36

ENC2A = 38
ENC2B = 40

ENC3A = 18
ENC3B = 22

ENC4A = 12
ENC4B = 16

outfile = open("odo_out.txt", "w+")

class Enc():
    def __init__(self, pina,pinb,name):
        self.a = pina
        self.b = pinb
        self.name = name

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.a, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.b, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.seq=0
        self.cnt=0
        self.dir=0

        self.ticks_per_round = float(35*14*3)
        #self.circumference = 0.265 # gum tires
        self.circumference = 0.2043 # drift tires

    def get_seq(self):
        a = not GPIO.input(self.a)
        b = not GPIO.input(self.b)

        '''
        Decoder logic
        Seq B   A   A ^ B
        0   0   0   0
        1   0   1   1
        2   1   1   0
        3   1   0   1
        '''
        return (a ^ b) | b << 1

    def reset(self):
        self.cnt = 0

    def check_encoder(self):
        seq = self.get_seq()

        delta = (seq-self.seq) % 4

        if delta == 0:
            pass # nothing happened
        elif delta == 1:
            #print "+",
            #print "%08d - Forward" % cnt # one step
            self.dir = 1
            self.cnt += 1
        elif delta == 2:
            #cnt += 2*direction
            print "X",
            #print "%08d - Two steps" % cnt # clockwise OR counter-clockwise
        elif delta == 3:
            #print "-",
            self.dir = -1
            #print "%08d - Backward" % cnt
            self.cnt -= 1

        self.seq = seq

        return self.seq,self.cnt,self.dir

    def get_travel(self):
        u = self.cnt/self.ticks_per_round 
        m = u*self.circumference
        return m

    def print_track(self):
        u = self.cnt/self.ticks_per_round 
        m = u*self.circumference
        print "%s: %08d\t%d\t%.2f rot, %.3f m" % (self.name, self.cnt,self.dir, u, m)


encoders = [
        Enc(ENC1A, ENC1B, "M1"),
        Enc(ENC2A, ENC2B, "M2"),
        Enc(ENC3A, ENC3B, "M3"),
        Enc(ENC4A, ENC4B, "M4"),
        ]


''' 
Odometry for skid-steered robots: 
https://www.coursera.org/learn/robotics-learning/lecture/YdleV/odometry-modeling

They suggest to SOLELY using a gyro to measure angular change, instead of calculating it from the encoders.
'''

class OdoPosition():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.a = 0

    def integrate(self,tx,ty,ta):
        self.x = self.x + tx*math.cos(self.a) - ty*math.sin(self.a)
        self.y = self.y + tx*math.sin(self.a) + ty*math.cos(self.a)
        self.a = self.a + ta


ss = time.time()
ss2 = time.time()
width_between_wheels = 0.25 #20.5cm
op = OdoPosition()

while True:
    for e in encoders:
        e.check_encoder()

    if time.time() - ss > 0.1: # integrate 10 times a second
        # lets average left ticks for e_inner/e_outer
        e_1_0 = encoders[0].get_travel()
        encoders[0].reset()
        e_1_1 = encoders[1].get_travel()
        encoders[1].reset()
        e_2_0 = encoders[2].get_travel()
        encoders[2].reset()
        e_2_1 = encoders[3].get_travel()
        encoders[3].reset()

        e_1 = (e_1_0 + e_1_1)/2.
        e_2 = (e_2_0 + e_2_1)/2.

        # the larger one is the outer
        e_inner = min(e_1,e_2)
        e_outer = max(e_1,e_2)

        theta = (e_outer - e_inner) / width_between_wheels
        x = ((e_inner + e_outer) / 2) * math.cos(theta)
        y = ((e_inner + e_outer) / 2) * math.sin(theta)
        #print "X: %.2f, Y: %.2f, Theta: %.2f" % (x,y,math.degrees(theta))
        #print e_1_0,",",e_1_1," - ", e_2_0,",",e_2_1
        op.integrate(x,y,theta)
        outfile.write("%.2f, %.2f, %.2f\n" % (op.x, op.y, op.a))
        ss = time.time()

    if time.time() - ss2 > 2:
        print "Position: ", op.x,",",op.y,",",op.a
        ss2 = time.time()

outfile.close()
