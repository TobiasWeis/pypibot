#!/usr/bin/python
import time
import RPi.GPIO as GPIO

M1A = 5
M1B = 3
M1E = 7

M2A = 13
M2B = 11
M2E = 15

M3A = 19
M3B = 21
M3E = 23

M4A = 29
M4B = 31
M4E = 33

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

#- M1 - right - front
GPIO.setup(M1A, GPIO.OUT)
GPIO.setup(M1B, GPIO.OUT)
GPIO.setup(M1E, GPIO.OUT)

GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.HIGH)

#- M2 - right - back
GPIO.setup(M2A, GPIO.OUT)
GPIO.setup(M2B, GPIO.OUT)
GPIO.setup(M2E, GPIO.OUT)

GPIO.output(M2A, GPIO.LOW)
GPIO.output(M2B, GPIO.HIGH)

#- M3 - left - back
GPIO.setup(M3A, GPIO.OUT)
GPIO.setup(M3B, GPIO.OUT)
GPIO.setup(M3E, GPIO.OUT)

GPIO.output(M3A, GPIO.LOW)
GPIO.output(M3B, GPIO.HIGH)

#- M4 - left - front
GPIO.setup(M4A, GPIO.OUT)
GPIO.setup(M4B, GPIO.OUT)
GPIO.setup(M4E, GPIO.OUT)

GPIO.output(M4A, GPIO.LOW)
GPIO.output(M4B, GPIO.HIGH)

#- M1
p1 = GPIO.PWM(M1E, 100)
p1.start(0)

#- M2
p2 = GPIO.PWM(M2E, 100)
p2.start(0)

#- M3
p3 = GPIO.PWM(M3E, 100)
p3.start(0)

#- M4
p4 = GPIO.PWM(M4E, 100)
p4.start(0)

def neutral():
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.LOW)

    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)

def forward(t, pow=50):
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.HIGH)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.HIGH)

    GPIO.output(M3A, GPIO.LOW)
    GPIO.output(M3B, GPIO.HIGH)
    GPIO.output(M4A, GPIO.LOW)
    GPIO.output(M4B, GPIO.HIGH)


    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)
    p3.ChangeDutyCycle(pow)
    p4.ChangeDutyCycle(pow)
    time.sleep(t)
    neutral()

def backward(t, pow=50):
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M1A, GPIO.HIGH)
    GPIO.output(M2B, GPIO.LOW)
    GPIO.output(M2A, GPIO.HIGH)

    GPIO.output(M3B, GPIO.LOW)
    GPIO.output(M3A, GPIO.HIGH)
    GPIO.output(M4B, GPIO.LOW)
    GPIO.output(M4A, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)
    p3.ChangeDutyCycle(pow)
    p4.ChangeDutyCycle(pow)
    time.sleep(t)
    neutral()

def left(t, pow=50):
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.HIGH)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.HIGH)

    GPIO.output(M3B, GPIO.LOW)
    GPIO.output(M3A, GPIO.HIGH)
    GPIO.output(M4B, GPIO.LOW)
    GPIO.output(M4A, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)
    p3.ChangeDutyCycle(pow)
    p4.ChangeDutyCycle(pow)
    time.sleep(t)
    neutral()

def right(t, pow=50):
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M1A, GPIO.HIGH)
    GPIO.output(M2B, GPIO.LOW)
    GPIO.output(M2A, GPIO.HIGH)

    GPIO.output(M3A, GPIO.LOW)
    GPIO.output(M3B, GPIO.HIGH)
    GPIO.output(M4A, GPIO.LOW)
    GPIO.output(M4B, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)
    p3.ChangeDutyCycle(pow)
    p4.ChangeDutyCycle(pow)
    time.sleep(t)
    neutral()


while True:
    inp = raw_input()
    if inp == 'w':
        forward(.35,45)
    elif inp == 's':
        backward(.35,45)
    elif inp == 'a':
        left(2)
    elif inp == 'd':
        right(2)
    print "INput: ", inp

sys.exit()

for i in range(20,101,10):
    print i
    p1.ChangeDutyCycle(i)
    p2.ChangeDutyCycle(i)
    p3.ChangeDutyCycle(i)
    p4.ChangeDutyCycle(i)

    time.sleep(3)

GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.LOW)

GPIO.output(M2A, GPIO.LOW)
GPIO.output(M2B, GPIO.LOW)

GPIO.output(M3A, GPIO.LOW)
GPIO.output(M3B, GPIO.LOW)

GPIO.output(M4A, GPIO.LOW)
GPIO.output(M4B, GPIO.LOW)




GPIO.cleanup()
