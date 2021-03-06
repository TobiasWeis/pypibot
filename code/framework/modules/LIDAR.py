from MP import MP # Base-class
import serial
import numpy as np
import time
import math

class LIDAR(MP):
    def init(self):
        self.f = serial.Serial(
                port='/dev/serial0', 
                baudrate=115200, 
                parity=serial.PARITY_NONE, 
                stopbits=serial.STOPBITS_ONE, 
                bytesize=serial.EIGHTBITS, 
                timeout=0)

        self.rays = [np.nan] * 360 # create a 360-elements list with zeros
        self.points = []
        self.cnt = 0
        self.ss = time.time()

    def decodeLine(self, line):
        data = []

        #bytes = [int(byte,16) for byte in line.strip("\n").split(":")]

        #print len(bytes)

        for idx,byte in enumerate(line.strip("\n").split(":")[:21]):
            if byte == '':
                return
            data.append(int(byte,16))

        start = data[0]
        idx = data[1] - 0xa0
        speed = float(data[2] | (data[3] << 8)) / 64.0
        #print speed
        #in_checksum = data[-2] + (data[-1] << 8)

        # first data package (4 bytes after header)
        angle = idx*4 + 0

        for i in range(4):
            theta = angle + i
            dist_mm = data[(i*4)+4] | ((data[(i*4)+5] & 0x1f) << 8)
            quality = data[(i*4)+6] | (data[(i*4)+7] << 8)
            x = dist_mm * np.cos((theta+90) * np.pi/180)
            y = dist_mm * np.sin((theta+90) * np.pi/180)
            bad = data[(i*4)+5] & 0x80
            bad2 = data[(i*4)+5] & 0x40

            if not bad and not bad2:
                self.rays[theta] = dist_mm
                self.points.append([x,y])
            else:
                self.rays[theta] = np.nan

        if angle == 0 or angle == 1 or angle == 2 or angle == 3:
            #print time.time() - self.ss
            self.ss = time.time()
            self.md["lidar_points"] = self.points
            self.md["lidar"] = self.rays
            self.points = []

    def run_impl(self): # overwrite baseclass, we do not need a loop here
        started = False
        string = []
        byte = self.f.read(1)
        #while not self.md["shutdown"]:
        while True:
            if byte != '':
                enc = (byte.encode('hex') + ":")
                if enc == "fa:":
                    if started:
                        try:
                            self.decodeLine(string)
                        except Exception, e:
                            print e
                            pass
                    if self.md["shutdown"]:
                        break
                    started = True
                    string = "fa:"
                elif started:
                    string += enc
                else:
                    print "Waiting for start"                                                                                                         
            byte = self.f.read(1)
