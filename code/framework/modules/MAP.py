from MP import MP
import math
#import matplotlib.pyplot as plt
import numpy as np
import cv2
from utils import *

from bresenham import bresenham

class MAP():
    def __init__(self, md):
        self.md = md
        self.mappoints = []
        self.laser_offset = [0.,0.,0.]
        self.lastpos = None
        #plt.ion()
        self.mapsize = [16,16] # m in x- and y-direction
        self.tilesize = [0.1,0.1] # how big a single cell should be
        self.tiles = np.zeros(
                (
                    int(self.mapsize[1]/self.tilesize[1]), 
                    int(self.mapsize[0]/self.tilesize[0])
                    )
                )
        self.egopoints = None

    def tile2coordm(self,row,col):
        fst = (col - self.tiles.shape[1]/2.) * self.tilesize[1] + self.tilesize[1]/2.
        snd = (row - self.tiles.shape[0]/2.) * self.tilesize[0] + self.tilesize[0]/2.
        return fst,snd 

    def wcs2rcs(self, coordinate):
        p = np.array([coordinate.x,coordinate.y])
        R = np.array([
                [math.cos(self.md["WCS"].a), -math.sin(self.md["WCS"].a)],
                [math.sin(self.md["WCS"].a), math.cos(self.md["WCS"].a)]
                ])
        t = np.array([self.md["WCS"].x, self.md["WCS"].y])
        print "Point ", p, " is in WCS:"
        print np.dot(p,R)+t
        return np.dot(p,R)+t

    def integrate(self, pos, egopoints):
        # we know our current pose from the odometry,
        # so we just translate and rotate the sick-data to build a map
        self.egopoints = egopoints

        for c in egopoints:
            if not np.isnan(c[0]):
                tx = c[0]  
                ty = c[1] + self.laser_offset[0] # compensate for laserscanner relative to robot center 
                ta = pos.a

                x = tx * math.cos(ta) - ty * math.sin(ta)
                y = ty * math.cos(ta) + tx * math.sin(ta)

                x += pos.x
                y -= pos.y

                # calculate all cells between us and the point
                # (we know that there is no obstacle, so we should
                # integrate this knowledge
                tilepos = [
                            int(pos.x/self.tilesize[0])+self.tiles.shape[0]/2,
                            -int(-pos.y/self.tilesize[1])-self.tiles.shape[1]/2
                        ]
                tiletarget = [
                            int(x/self.tilesize[0])+self.tiles.shape[0]/2,
                            -int(y/self.tilesize[1])-self.tiles.shape[1]/2
                        ]

                # FIXME: too computationally heavy
                '''
                try:
                    l = list(bresenham(tilepos[0],tilepos[1],tiletarget[0],tiletarget[1]))
                    for bpos in l:
                        self.tiles[-bpos[1],bpos[0]] += 0.5
                except Exception, e:
                    print "Exception: ", e
                '''

                self.mappoints.append([x,y])
                try:
                    self.tiles[int(y/self.tilesize[1])+self.tiles.shape[1]/2,
                            int(x/self.tilesize[0])+self.tiles.shape[0]/2] += 1
                except Exception, e:
                    pass

                self.tiles = np.minimum(100,self.tiles)

                if len(self.mappoints) > 1000:
                    self.mappoints = self.mappoints[len(self.mappoints)-5000:]

    def visualize(self, tick=0, save=False):
        rows = 2
        cols = 2

        fig = plt.figure(3, figsize=(13,20))
        
        plt.cla()
        fig.clf()

        fig.suptitle("Time: %.3fs" % tick)

        ax = fig.add_subplot(rows,cols,1)
        ax.set_title('Worldview')
        ax.imshow(cv2.cvtColor(cv2.imread("/tmp/ldimg.png"), cv2.COLOR_BGR2RGB), interpolation='nearest')

        ax = fig.add_subplot(rows,cols,2)
        ax.set_title('LIDAR points in RCS')
        ps = np.array(self.egopoints)
        ax.scatter(ps[:,0], ps[:,1], alpha=0.1)
        ax.set_xlim((-self.mapsize[0]/2.,self.mapsize[0]/2.))
        ax.set_ylim((-self.mapsize[1]/2.,self.mapsize[0]/2.))
        ax.set_aspect('equal')

        ax = fig.add_subplot(rows,cols,3)
        ax.set_title("LIDAR points in WCS")
        ps = np.array(self.mappoints)
        ax.scatter(ps[:,0], ps[:,1], alpha=0.1)
        ax.set_xlim((-self.mapsize[0]/2.,self.mapsize[0]/2.))
        ax.set_ylim((-self.mapsize[1]/2.,self.mapsize[0]/2.))
        ax.set_aspect('equal')

        ax2 = fig.add_subplot(rows,cols,4)
        ax2.set_title("Integrated LIDAR w. conf.")
        ax2.set_aspect('equal')
        ax2.imshow(self.tiles, cmap=plt.cm.jet, interpolation='nearest')
        ax2.invert_yaxis()

        plt.tight_layout()

        if save:
            plt.savefig("/tmp/map_%08.3f.png" %(tick))

        plt.show()
        plt.pause(0.000001)
