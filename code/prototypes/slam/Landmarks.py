#!/usr/bin/python
import math
import matplotlib.pyplot as plt
import numpy as np
import cv2
import random

from Picolo import *

class Line():
    def __init__(self, p1,p2):
        self.p1 = p1
        self.p2 = p2

class Landmarks():
    def __init__(self):
        self.p = Picolo()
        self.p.readFile("outfile_complex.txt")

    def perp(self,a):
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def get_intersection(self, l1, l2):
        da = l1.p2-l1.p1
        db = l2.p2-l2.p1
        dp = l1.p1-l2.p1
        dap = self.perp(da)
        denom = np.dot(dap,db)
        num = np.dot(dap,dp)
        return (num / denom.astype(float))*db + l2.p1

    def get_angle(self, l1,l2):
        vA = [l1.p1[0]-l1.p2[0], l1.p1[1]-l1.p2[1]]
        vB = [l2.p1[0]-l2.p2[0], l2.p1[1]-l2.p2[1]]
        dot_prod = np.dot(vA,vB)
        magA = np.dot(vA,vA)**0.5
        magB = np.dot(vB,vB)**0.5
        #cos_ = dot_prod/magA/magB
        angle = math.acos(dot_prod/magB/magA)
        
        return angle 


    def extract_lines(self,frame_idx, n_trials=50, n_support=45, tolerance=35):
        lines = []

        print frame_idx,",",
        all_points = self.p.points[frame_idx]
        points = all_points[(~np.isnan(all_points[:,0]))]

        fig = plt.figure(1)
        fig.clf()
        plt.scatter(points[:,0], points[:,1], alpha=0.1)

        colors = ['r', 'g', 'k', 'y', 'gray']

        matched = []
        free = range(len(points))

        for n in range(n_trials):
            col = colors[n % len(colors)]
    
            idx1 = random.choice(free)

            idx2 = idx1
            while idx2 == idx1:
                idx2 = random.choice(free) 

            p1 = points[idx1,0:2]
            p2 = points[idx2,0:2]

            # calculate line equation
            myp = [p1,p2]
            x_c,y_c = zip(*myp)
            A = np.vstack([x_c, np.ones(len(x_c))]).T
            slope,intercept = np.linalg.lstsq(A,y_c)[0]

            # compute how many points match
            inliers = []
            
            # plot trial-line
            xspace = np.linspace(min(p1[0],p2[0]), max(p1[0],p2[0]))
            plt.plot(xspace, (slope*xspace+intercept), color='k', alpha=0.05)


            for idx,p in enumerate(points):
                if idx == idx1 or idx == idx2:
                    continue
                # calculate error to line model
                #if abs(p[1] - (slope*p[0] + intercept)) < tolerance:
                #    inliers.append(idx)

                if np.linalg.norm(np.cross(p2-p1,p1-p[0:2]))/np.linalg.norm(p2-p1) < tolerance:
                    inliers.append(idx)

            if len(inliers) > n_support:
                lines.append(Line(p1,p2))
                # move those inliers to matched
                matched.extend(inliers)
                free = list(set(free) - set(inliers))
                plt.plot(p1[0],p1[1],'o', color=col)
                plt.plot(p2[0],p2[1],'o', color=col)

                # plot the line
                xspace = np.linspace(min(points[inliers,0]), max(points[inliers,0]))
                plt.plot(xspace, (slope*xspace+intercept), color=col)
                # plot points that agree
                for inl in inliers:
                    plt.plot(points[inl,0], points[inl,1],'o', color=col, alpha=0.5)

            # find intersections
            import itertools
            for linepair in list(itertools.combinations(lines, 2)):
                isect = self.get_intersection(linepair[0],linepair[1])
                if abs(isect[0]) < 10000 and abs(isect[1]) < 10000: 
                    angle = self.get_angle(linepair[0], linepair[1])
                    if abs(angle - math.pi/2.) < 0.2:
                        ax = fig.gca()
                        ax.text(isect[0], isect[1], "%.2f"% angle, color='green')
                        plt.plot(isect[0],isect[1], '*r', ms=20)
            
        plt.axis("equal")
        #plt.show()
        plt.savefig("/tmp/lines_%08d.png" % frame_idx)


if __name__ == "__main__":
    lm = Landmarks()
    for frame_idx in range(0,100,1):
        lm.extract_lines(frame_idx)

