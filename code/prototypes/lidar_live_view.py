#!/usr/bin/python
import serial
import time
import math

import numpy as np
import cv2
#import matplotlib.pyplot as plt

print("Hello")

outfile = open("outfile.txt", "w+")

f = serial.Serial(
        port='/dev/serial0', 
        baudrate=115200, 
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_ONE, 
        bytesize=serial.EIGHTBITS, 
        timeout=0)

measurements = np.zeros((360,3), np.float64)

global ss
ss = time.time()

def decode_string(string,measurements):
    global ss
    #print string
    data = []

    for byte in string.strip("\n").split(":")[:21]:
        data.append(int(byte,16))

    start = data[0]
    idx = data[1] - 0xa0
    speed = float(data[2] | (data[3] << 8)) / 64.0
    in_checksum = data[-2] + (data[-1] << 8)

    # first data package (4 bytes after header)
    angle = idx*4 + 0
    angle_rad = angle * math.pi / 180.
    dist_mm = data[4] | ((data[5] & 0x1f) << 8)
    quality = data[6] | (data[7] << 8)

    if data[5] & 0x80:
        #print "X - ",
        pass
    else:
        #print "O - ",
        pass
    if data[5] & 0x40:
        #print "NOT GOOD"
        pass

    measurements[angle,0] = min(5999, int(dist_mm))
    measurements[angle,1] = quality

    #print "Speed: ", speed, ", angle: ", angle, ", dist: ",dist_mm, ", quality: ", quality
    #print "Checksum: ", checksum(data), ", from packet: ", in_checksum
    #outfile.write(string+"\n")
    #print "-----------"
    if angle == 0:
        print time.time() - ss
        ss = time.time()
        update_plot(measurements)

def update_plot(measurements):
    img = np.zeros((200,200,3), np.uint8)

    for angle,m in enumerate(measurements):
        x = img.shape[1]/2 + (int(-m[0]*math.sin(math.radians(angle))) / (6000 / img.shape[0]))
        y = img.shape[0]/2 - (int(m[0]*math.cos(math.radians(angle))) / (6000 / img.shape[1]))
        img[y,x] = [m[1],255,255]
    cv2.imshow("meas",img)
    cv2.waitKey(1)

byte = f.read(1)
count = 1
started = False
string = "Start"
#while byte != "":# and count <= 22*1000:
while True:
    if byte != '':
        enc = (byte.encode('hex') + ":")
        if enc == "fa:":
            #outfile.write(string + "\n")
            if started:
                try:
                    decode_string(string,measurements)
                except Exception, e:
                    #print e
                    pass
            started = True
            string = "fa:"
        elif started:
            string += enc
        else:
            print "Waiting for start"
        #time.sleep(0.0000000001)
    byte = f.read(1)
    count += 1

    
outfile.close()
print("Goodbye")
