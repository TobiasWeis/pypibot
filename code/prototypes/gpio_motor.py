#!/usr/bin/python
import time
import RPi.GPIO as GPIO

M1A = 3
M1B = 5
M1E = 7

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(M1A, GPIO.OUT)
GPIO.setup(M1B, GPIO.OUT)
GPIO.setup(M1E, GPIO.OUT)

GPIO.output(3, GPIO.LOW)
GPIO.output(5, GPIO.HIGH)
p = GPIO.PWM(M1E, 100)
p.start(0)

for i in range(10,101,10):
    print i
    p.ChangeDutyCycle(i)
    time.sleep(5)

GPIO.output(3, GPIO.LOW)
GPIO.output(5, GPIO.LOW)

GPIO.cleanup()
