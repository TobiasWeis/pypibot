#!/usr/bin/python
import serial

f = serial.Serial(port='/dev/arduino', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

while True:
    l = f.readline()
    if l != '':
        print "Voltage: ", float(l.rstrip())
