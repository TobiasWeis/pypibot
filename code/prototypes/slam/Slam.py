#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import math
import cv2
from sklearn.neighbors import NearestNeighbors
from utils import *

from Picolo import *

class Slam():
    def __init__(self):
        self.p = Picolo()
        self.p.readFile("outfile_complex.txt")

    def estimateTransition_raw(self,of,nf):
        # find the translation that matches old frame of and new frame nf
        # with as few errors as possible
        
        diffs = []
        for i in range(len(of)):
            diffx = nf[i,0] - of[i,0]
            diffy = nf[i,1] - of[i,1]
            diffs.append([diffx,diffy])
        diffs = np.array(diffs)

        fig = plt.figure()
        plt.title("Differences of/nf")
        plt.scatter(diffs[:,0], diffs[:,1], alpha=0.3)
        plt.xlabel('x-diff')
        plt.ylabel('y-diff')


    def estimateTransition_Ransac(self, of,nf):
        from sklearn import linear_model
        model_ransac = linear_model.RANSACRegressor(linear_model.LinearRegression())

        nof = of[~np.isnan(of[:,0])]

        model_ransac.fit(nof[:,0][:,np.newaxis], nof[:,1])
        line_x = np.arange(-500,500)
        line_y = model_ransac.predict(line_x[:,np.newaxis])

        plt.plot(line_x, line_y, color='navy', linestyle='-')


if __name__ == "__main__":
    S = Slam()
    x = 0
    y = 0
    a = 0
    coords = []
    coordsm = []

    for frame_idx in range(0,200):
        if frame_idx == 0:
            continue

        of = S.p.points[frame_idx]
        nf = S.p.points[frame_idx+1]

        nof = of[(~np.isnan(of[:,0]))].astype(np.float64)
        nnf = nf[(~np.isnan(nf[:,0]))].astype(np.float64)

        #onof = np.zeros((nof.shape[0],3), np.float64)
        onnf = np.ones((nnf.shape[0],3), np.float64)
        #onof[:,0:2] = nof[:,0:2]
        onnf[:,0:2] = nnf[:,0:2]

        print "========================="
        print "nnf: ", nnf.shape
        print "nof: ", nof.shape
        print "========================="

        T,dists = icp(nnf[:,0:2], nof[:,0:2])
        dist = np.mean(dists)
        print "T: ", T
        print "dist: ", dist

        if dist > 50: #-- points during a fast rotation are misaligned INSIDE one frame, then they do not match
            print "Meh"

        tpoints = np.dot(onnf, T.T)
        print "Translation: ", T[0,2],",",T[1,2]
        print "Rotation: ", math.degrees(math.atan2(T[1,0],T[0,0]))

        tx = T[0,2]
        ty = T[1,2]
        ta = math.atan2(T[1,0],T[0,0])

        x = x + tx*math.cos(a) - ty*math.sin(a)
        y = y + tx*math.sin(a) + ty*math.cos(a)
        a = a + ta

        coords.append([x,y,a])
        for nfp in onnf:
            nfpx = x + + nfp[0]*math.cos(a) - nfp[1]*math.sin(a)
            nfpy = y + + nfp[0]*math.sin(a) + nfp[1]*math.cos(a)
            coordsm.append([nfpx,nfpy])


        fig = plt.figure(1)
        fig.clf()
        plt.title("Distance: %.2f" % dist)
        tmpcoords = np.array(coords)
        plt.axis("equal")
        plt.xlim((-6000,6000))
        plt.ylim((-6000,6000))
        #plt.scatter(nf[:,0], nf[:,1], c='b', label='new frame', alpha=0.5)

        cm = np.array(coordsm)
        plt.scatter(cm[:,0], cm[:,1], c='b', alpha=0.01)
        plt.plot(tmpcoords[:,0], tmpcoords[:,1], 'r-o')
        plt.savefig("/tmp/slam_%08d.png" % frame_idx)

        fig = plt.figure(2)
        fig.clf()
        plt.suptitle("Distance: %.2f" % dist)
        fig.add_subplot(121)
        plt.title("Original points")
        plt.scatter(of[:,0], of[:,1], c='k', label='old frame', alpha=0.5)
        plt.scatter(nf[:,0], nf[:,1], c='b', label='new frame', alpha=0.5)
        plt.plot(0,0,'ro')
        plt.axvline(0, color='red')
        plt.axhline(0, color='red')
        plt.axis('equal')
        plt.xlim((-6000,6000))
        plt.ylim((-6000,6000))

        plt.legend()

        fig.add_subplot(122)
        plt.title("Matched points")
        plt.scatter(nof[:,0], nof[:,1], c='k', alpha=0.5, label='old frame')
        plt.scatter(tpoints[:,0], tpoints[:,1], c='b', alpha=0.5, label='matched points')
        plt.plot(0,0,'ro')
        plt.axvline(0, color='red')
        plt.axhline(0, color='red')

        plt.axis('equal')
        plt.xlim((-6000,6000))
        plt.ylim((-6000,6000))

        plt.legend()

        plt.savefig("/tmp/slam_match_%08d.png" % frame_idx)

        #plt.show()


