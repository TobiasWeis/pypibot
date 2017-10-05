#!/usr/bin/python

from MP import MP
import time
import cv2
import numpy as np
import math
from utils import *

class SIMU(MP):
    def init(self):
        # load map
        self.mymap = np.array([
                [[0,10], [10,10]],
                [[0,0],  [10,0]],
                [[0,10], [0,0]],
                [[10,10],[10,0]],
                ], dtype=np.float64)

        self.mymap = np.append(self.mymap,self.create_rect(0,9), axis=0)
        self.mymap = np.append(self.mymap,self.create_rect(2,3), axis=0)
        self.mymap = np.append(self.mymap,self.create_rect(6,2), axis=0)
        self.mymap = np.append(self.mymap,self.create_rect(8,5,w=2), axis=0)
        self.mymap = np.append(self.mymap,self.create_rect(2,7,w=3), axis=0)


        self.lidar = []

        self.visited_points = []

        self.start_robot = Coordinate(5,5,math.radians(0))
        self.robot = Coordinate(5,5,math.radians(0))

    def create_rect(self,sx,sy,w=1,h=1):
        rect = np.array([
                [[sx,sy],[sx,sy+h]],
                [[sx+w,sy],[sx+w,sy+h]],
                [[sx,sy],[sx+w,sy]],
                [[sx,sy+h],[sx+w,sy+h]],
            ], dtype=np.float64)
        return rect

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
        for idx,ldar in enumerate(self.lidar):
            if idx == 0:
                color = (255,0,255)
            else:
                color = (128,128,128)

            try:
                lr = ldar[3:]
                cv2.line(img,
                        (int(lr[0]/float(size)*res),int(lr[1]/float(size)*res)),
                        (int(lr[2]/float(size)*res),int(lr[3]/float(size)*res)),
                        color,
                        1
                        )
            except:
                pass

        # draw intersects
        for v in self.lidar:
            l = [v[1],v[2]]
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
                (int(self.robot.x/float(size)*res),int(self.robot.y/float(size)*res)),
                5,
                (255,0,255))

        ofx = 0.5 * math.cos(self.robot.a)
        ofy = -0.5 * math.sin(self.robot.a)
        cv2.line(img,
                (int(self.robot.x/float(size)*res),int(self.robot.y/float(size)*res)),
                (int((self.robot.x+ofx)/float(size)*res),int((self.robot.y+ofy)/float(size)*res)),
                (255,0,255),
                2
                )
        
        #draw visited points
        for vp in self.visited_points:
            cv2.circle(img,
                    (int(vp.x/float(size)*res),int(vp.y/float(size)*res)),
                    5,
                    (255,0,255)
                    )


        cv2.imshow("map",img)
        cv2.imwrite("/tmp/ldimg.png",img) # FIXME: remove
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
	lx = 6.*math.cos(self.robot.a + angle)
	ly = -6.*math.sin(self.robot.a + angle)
	return np.array([[self.robot.x, self.robot.y],[self.robot.x+lx, self.robot.y+ly]])

    def eucl_dist(self,pa,pb):
        a=float(pa[0]-pb[0])
        b=float(pa[1]-pb[1])
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
        self.lidar = (np.zeros((angles,7), dtype=np.float64) + [100.,0,0,0,0,0,0]) * [1., np.nan, np.nan,np.nan,np.nan,np.nan,np.nan]
        self.lidar_points = []

        # FIXME: this always starts at 0?! -> pointing up?!

        for alpha_tmp in range(angles):
            try:
                alpha = float(alpha_tmp + self.md["WCS"].a)
            except:
                alpha = float(alpha_tmp)

            ll = self.get_line(math.radians(alpha))

            x = None
            for lm in self.mymap:
                # check if segments intersect at all, then calculate intersection
		if self.seg_intersect_check(ll[0],ll[1],lm[0],lm[1]):
		    intersect = self.seg_intersect(ll[0],ll[1],lm[0],lm[1])
		    #print intersect
                    d = self.eucl_dist([self.robot.x,self.robot.y],intersect)
		    if (d < 6) and (d < self.lidar[int(math.floor(alpha)) % 360][0]):
                        lli = [[self.robot.x,self.robot.y],[intersect[0],intersect[1]]]

                        x = d * np.cos((alpha) * np.pi/180.) # m
                        y = d * np.sin((alpha) * np.pi/180.) # m

                        self.lidar[int(math.floor(alpha)) % 360] = [d,intersect[0],intersect[1],lli[0][0],lli[0][1],lli[1][0],lli[1][1]]
            if x is not None:
                self.lidar_points.append([x,y])
        #self.lidar[:,0] *= 1000. #mm
        self.md["lidar"] = self.lidar
        self.md["lidar_points"] = self.lidar_points

    def run_impl(self):
        if "MCS" in self.md:
            self.robot.x = self.start_robot.x + self.md["MCS"].x
            self.robot.y = self.start_robot.y + self.md["MCS"].y
            self.robot.a = self.start_robot.a + self.md["MCS"].a
        self.visited_points.append(Coordinate(self.robot.x, self.robot.y, self.robot.a))
        self.calc_lidar()
        self.show()

        #time.sleep(0.05)

if __name__ == "__main__":
    md = {}
    md["shutdown"] = False

    sim = SIMU("SIMU",None,md)
    sim.init()

    ss = time.time()
    for x in np.arange(0,10,0.1):
        sim.robot.x = x
        sim.robot.a = 0
        sim.calc_lidar()
        print time.time() -ss
        ss = time.time()
        sim.show()
