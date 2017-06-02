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
        self.p.readFile("outfile_forward_backward.txt")

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


    def plotTransition(self,of,nf):
        fig = plt.figure()
        plt.scatter(of[:,0], of[:,1], c='k', label='old frame')
        plt.scatter(nf[:,0], nf[:,1], c='b', label='new frame')
        plt.legend()


if __name__ == "__main__":
    S = Slam()
    of = S.p.points[20]
    nf = S.p.points[21]

    nof = of[~np.isnan(of[:,0])].astype(np.float64)
    nnf = nf[~np.isnan(nf[:,0])].astype(np.float64)

    #onof = np.zeros((nof.shape[0],3), np.float64)
    onnf = np.ones((nnf.shape[0],3), np.float64)

    #onof[:,0:2] = nof[:,0:2]
    onnf[:,0:2] = nnf[:,0:2]

    S.plotTransition(of,nf)

    #T,dist = icp(nof[:,0:2], nnf[:,0:2])
    T,dist = icp(nnf[:,0:2], nof[:,0:2])
    print "T: ", T
    print "dist: ", dist

    fig = plt.figure()
    tpoints = np.dot(onnf, T.T)

    plt.scatter(nof[:,0], nof[:,1], c='k')
    plt.scatter(tpoints[:,0], tpoints[:,1], c='b')

    plt.show()


