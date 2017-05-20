#!/usr/bin/python
import serial

print("Hello")

outfile = open("outfile.txt", "w+")

f = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

byte = f.read(1)
count = 1

started = False

string = "Start"

while byte != "":# and count <= 22*1000:
    enc = (byte.encode('hex') + ":")
    if enc == "fa:":
        started = True
        #outfile.write(string + "\n")
        print string
        string = "fa:"
    elif started:
        string += enc
    else:
        print "Waiting for start"

    byte = f.read(1)
    count += 1
outfile.close()
print("Goodbye")
