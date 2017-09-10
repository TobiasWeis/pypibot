#!/usr/bin/python

from MP import MP
import time
import cv2
import numpy as np
import math

class SIMU(MP):
    def init(self):
        # load map
        self.mymap = np.array([
                [[0,10], [10,10]],
                [[0,0],  [10,0]],
                [[0,10], [0,0]],
                [[10,10],[10,0]],
                [[5,2],[5,3]]
                ])

        self.lidar = {}
        self.lidar_rays = []

        self.robot = [5,5,math.radians(90)]

    def show(self, size=10, res=1000):

        img = np.zeros((res,res,3), np.uint8)

        # draw map
        for l in self.mymap:
            cv2.line(img,
                    (int((l[0][0]/float(size))*res), int(l[0][1]/float(size)*res)),
                    (int((l[1][0]/float(size))*res), int(l[1][1]/float(size)*res)),
                    (255,255,255),
                    3
                    )

        # draw lidar rays
        for lr in self.lidar_rays:
            cv2.line(img,
                    (int(lr[0][0]/float(size)*res),int(lr[0][1]/float(size)*res)),
                    (int(lr[1][0]/float(size)*res),int(lr[1][1]/float(size)*res)),
                    (128,128,128),
                    1
                    )

        # draw intersects
        for k,v in self.lidar.iteritems():
            l = v[1]
            try:
                cv2.circle(img,
                        (int(l[0]/float(size)*res), int(l[1]/float(size)*res)),
                        5,
                        (0,0,255)
                        )
            except:
                pass


        #draw bot
        cv2.circle(img, 
                (int(self.robot[0]/float(size)*res),int(self.robot[1]/float(size)*res)),
                5,
                (255,0,255))

        ofx = 0.5 * math.cos(self.robot[2])
        ofy = -0.5 * math.sin(self.robot[2])
        cv2.line(img,
                (int(self.robot[0]/float(size)*res),int(self.robot[1]/float(size)*res)),
                (int((self.robot[0]+ofx)/float(size)*res),int((self.robot[1]+ofy)/float(size)*res)),
                (255,0,255),
                2
                )


        cv2.imshow("map",img)
        cv2.waitKey(10)

    def perp(self, a ) :
	b = np.empty_like(a)
	b[0] = -a[1]
	b[1] = a[0]
	return b

    def seg_intersect(self, a1,a2, b1,b2) :
	da = a2-a1
	db = b2-b1
	dp = a1-b1
	dap = self.perp(da)
	denom = np.dot( dap, db)
	num = np.dot( dap, dp )
	return (num / denom.astype(float))*db + b1

    def get_line(self, angle):
	lx = 6.*math.cos(angle)
	ly = -6.*math.sin(angle)
	return np.array([[self.robot[0], self.robot[1]],[self.robot[0]+lx, self.robot[1]+ly]])

    def eucl_dist(self,pa,pb):
        a=pa[0]-pb[0]
        b=pa[1]-pb[1]
        return math.sqrt(a*a + b*b)

    def ccw(self,A,B,C):
	return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    # Return true if line segments AB and CD intersect
    def seg_intersect_check(self,A,B,C,D):
	return self.ccw(A,C,D) != self.ccw(B,C,D) and self.ccw(A,B,C) != self.ccw(A,B,D)

    def calc_lidar(self, angles=360):
        '''
            simulate the lidar-beams w.r.t the robot position and the map
        '''
        self.lidar = {}
        self.lidar_rays = []

        for alpha in range(angles):
            self.lidar[alpha] = [100, [-1,-1]]
            ll = self.get_line(math.radians(alpha))
            self.lidar_rays.append(ll)
            for lm in self.mymap:
                # check if segments intersect at all
		if self.seg_intersect_check(ll[0],ll[1],lm[0],lm[1]):
		    intersect = self.seg_intersect(ll[0],ll[1],lm[0],lm[1])
		    #print intersect
                    d = self.eucl_dist([self.robot[0],self.robot[1]],intersect)
		    if (d < 6) and (d < self.lidar[alpha][0]):
                        self.lidar[alpha] = [d,intersect]

    def run_impl(self):
        pass


if __name__ == "__main__":
    md = {}
    md["shutdown"] = False

    sim = SIMU("SIMU",None,md)
    sim.init()

    for x in np.arange(0,10,0.1):
        sim.robot[0] = x
        sim.robot[2] = 0
        sim.calc_lidar()
        sim.show()
