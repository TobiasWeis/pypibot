#!/usr/bin/python
import serial
import time

f = serial.Serial(port='/dev/arduino', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

while True:
    try:
        l = f.readline()
        if l != '':
            print "Voltage: ", float(l.rstrip())
    except:
        print "Could not read voltage"
        time.sleep(1)
