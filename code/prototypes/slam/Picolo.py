#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

class LaserPoint():
    def __init__(self,x,y,quality,bad,bad2):
        self.x = x
        self.y = y
        self.bad=bad
        self.bad2=bad2
        self.quality = quality

class Picolo():
    def __init__(self):
        self.round = 0
        self.points = {}
        self.points[0] = np.zeros((360,5), np.float64) * np.nan

    def decodeLine(self,line):
        try:
            bytes = [int(x,16) for x in line.split(':')[:-1]]
        except Exception, e:
            print "Err:", e
            return

        if len(bytes) != 22:
            return False

        theta_base = (bytes[1] - 160) * 4
        # on theta == 0 degrees start a new round
        if theta_base == 0:
            self.round += 1
            #self.points[self.round] = []
            self.points[self.round] = np.zeros((360,5), np.float64) * np.nan

        speed = float(bytes[2] | (bytes[3] << 8)) / 64.0

        for i in range(4):
            theta = theta_base + i
            dist_mm = bytes[(i*4)+4] | ((bytes[(i*4)+5] & 0x1f) << 8)
            quality = bytes[(i*4)+6] | (bytes[(i*4)+7] << 8)
            x = dist_mm * np.cos((theta+90) * np.pi/180)
            y = dist_mm * np.sin((theta+90) * np.pi/180)
            bad = bytes[(i*4)+5] & 0x80
            bad2 = bytes[(i*4)+5] & 0x40

            if dist_mm > 60:
                self.points[self.round][theta] = [x,y,quality,bad,bad2]
            #self.points[self.round].append(LaserPoint(x,y,quality,bad,bad2))

    def readFile(self,fname):
        with open(fname) as f:
            line = f.readline()
            while line != "":
                self.decodeLine(line)
                line = f.readline()

    def show(self):
        for i in range(self.round):
            self.plot(i)

    def plot(self,cnt):
        fig = plt.figure()
        plt.title("Round: %d" % cnt)
        '''
        arr = []
        for lp in self.points[cnt]:
            arr.append([lp.x, lp.y, lp.quality, lp.bad, lp.bad2])

        arr = np.array(arr)
        '''
        arr = self.points[cnt]
        plt.scatter(arr[:,0], arr[:,1], c=arr[:,2], alpha=0.8,  vmax=max(arr[:,2]), cmap="inferno")
        plt.colorbar()
        
        plt.plot(0,0,'go')
        plt.axvline(0,color='g')
        plt.axhline(0,color='g')

        bad_ones = arr[(arr[:,3] == True) | (arr[:,4] == True)]
        plt.scatter(bad_ones[:,0], bad_ones[:,1], c='r')

        plt.axis('equal')
        plt.show()

if __name__ == "__main__":
    p = Picolo()
    p.readFile("outfile_forward_backward.txt")
    p.show()
