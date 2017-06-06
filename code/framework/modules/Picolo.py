#!/usr/bin/python
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns

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
        self.points = np.zeros((360,6), np.float64) * np.nan


    def decodeLine(self,line):
        try:
            bytes = [int(x,16) for x in line.split(':')[:-1]]
        except Exception, e:
            print "Err:", e
            return

        if len(bytes) != 22:
            return
            #raise Exception("Byte-Length does not match")

        theta_base = (bytes[1] - 160) * 4
        # on theta == 0 degrees start a new round

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
                self.points[theta] = [x,y,quality,bad,bad2,dist_mm]
            else:
                self.points[theta] = np.nan

        '''
        if theta_base == 0:
            self.frame = self.points.copy()
            self.points = np.zeros((360,6), np.float64) * np.nan
            self.round += 1

        '''


    def readFile(self,fname):
        with open(fname) as f:
            line = f.readline()
            while line != "":
                self.decodeLine(line)
                line = f.readline()

    def show(self):
        for i in range(self.round):
            self.plot(i)

    '''
    def plot(self,cnt):
        fig = plt.figure()
        plt.title("Round: %d" % cnt)
        arr = self.points[cnt]
        plt.scatter(arr[:,0], arr[:,1], c=arr[:,2], alpha=0.8,  vmin=0, vmax=2048, cmap="inferno")
        plt.colorbar()

        ax = fig.gca()
        ax.set_xticks(np.arange(-6000, 6000, 500))
        ax.set_yticks(np.arange(-6000, 6000, 500))

        
        plt.plot(0,0,'go')
        plt.axvline(0,color='g')
        plt.axhline(0,color='g')


        plt.axis('equal')


        bad_ones = arr[(arr[:,3] == True) | (arr[:,4] == True)]
        plt.scatter(bad_ones[:,0], bad_ones[:,1], c='r')

        ax.set_xlim((-6000, 6000))
        ax.set_ylim((-6000, 6000))

        plt.savefig("/tmp/laser_%08d.png" % cnt)
        #plt.show()
    '''

if __name__ == "__main__":
    p = Picolo()
    p.readFile("outfile_complex.txt")
    p.show()
