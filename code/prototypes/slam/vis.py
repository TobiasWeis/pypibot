#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def getDist(lsb, msb):
    if (msb == "80" or msb == "70"):
        return False
    return int(msb + lsb, 16)/1000.

def addPoint(dist, theta, x, y):
    if (dist != False and dist < 6):
        print "added point"
        print(dist)
        x.append(dist*np.cos((theta+90) * np.pi/180))
        y.append(dist*np.sin((theta+90) * np.pi/180))
    else:
        print "Not adding, problem with distance"

x=[]
y=[]
cnt = 0

def plot():
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(np.arange(-10,10,0.5))
    ax.set_yticks(np.arange(-10,10.,0.5))
    ax.set_aspect('equal')
    plt.xlim((-6.,6.))
    plt.ylim((-6.,6.))
    plt.scatter(x,y)
    plt.plot(0,0,'ro')
    plt.axvline(0,color='red')
    plt.axhline(0,color='red')
    plt.grid()
    #plt.savefig("Map_%08d.png" % cnt)
    plt.show()

#with open("outfile_forward_backward.txt") as f:
with open("outfile_complex.txt") as f:
    line = f.readline()
    while line != "":
        bytes = line.split(':')
        if (len(bytes[:-1]) == 22):
            theta = (int(bytes[1], 16) - 160) * 4
            if theta == 0:
                cnt += 1
                print cnt
                plot()
                x=[]
                y=[]
            # print(line)
            print(theta)
            addPoint(getDist(bytes[4], bytes[5]), theta, x, y)
            addPoint(getDist(bytes[8], bytes[9]), theta + 1, x, y)
            addPoint(getDist(bytes[12], bytes[13]), theta + 2, x, y)
            addPoint(getDist(bytes[16], bytes[17]), theta + 3, x, y)
        else:
            print "not 22 bytes"
        line = f.readline()

