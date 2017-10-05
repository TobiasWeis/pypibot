#!/usr/bin/python
import time
import RPi.GPIO as GPIO

import curses, time

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


#- M1
p1 = GPIO.PWM(M1E, 100)
p1.start(0)

#- M2
p2 = GPIO.PWM(M2E, 100)
p2.start(0)


def neutral():
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.LOW)

    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)

def forward(t, pow=50):
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.HIGH)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)

def backward(t, pow=50):
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M1A, GPIO.HIGH)
    GPIO.output(M2B, GPIO.LOW)
    GPIO.output(M2A, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)

def left(t, pow=80):
    GPIO.output(M1A, GPIO.HIGH)
    GPIO.output(M1B, GPIO.LOW)
    GPIO.output(M2A, GPIO.LOW)
    GPIO.output(M2B, GPIO.HIGH)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)

def right(t, pow=80):
    GPIO.output(M1A, GPIO.LOW)
    GPIO.output(M1B, GPIO.HIGH)
    GPIO.output(M2A, GPIO.HIGH)
    GPIO.output(M2B, GPIO.LOW)

    p1.ChangeDutyCycle(pow)
    p2.ChangeDutyCycle(pow)

def input_char(message):
    try:
        win = curses.initscr()
        win.addstr(0, 0, message)
        while True: 
            ch = win.getch()
            if ch in range(32, 127): break
            time.sleep(0.05)
    except: raise
    finally:
        curses.endwin()
    return chr(ch)


while True:
    c = input_char('wasd: drive, Space: Stop, q: exit')

    #inp = raw_input()
    if c == 'w':
        forward(0.05,45)
    elif c == 's':
        backward(0.05,45)
    elif c == 'a':
        left(0.05,25)
    elif c == 'd':
        right(0.05,25)
    elif c == ' ':
        neutral()
    elif c == 'q':
        break

GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.LOW)

GPIO.output(M2A, GPIO.LOW)
GPIO.output(M2B, GPIO.LOW)

GPIO.cleanup()
