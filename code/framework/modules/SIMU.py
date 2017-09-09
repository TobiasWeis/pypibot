#!/usr/bin/python

from MP import MP
import time
import cv2
import numpy as np
import math

class SIMU(MP):
    def init(self):
        # load map
        self.mymap = [
                [(0,10), (10,10)],
                [(0,0),(10,0)],
                [(0,10),(0,0)],
                [(10,10), (10,0)]
                ]

        self.robot = [5,5,math.radians(180)]

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

        #draw bot
        cv2.circle(img, 
                (int(self.robot[0]/float(size)*res),int(self.robot[1]/float(size)*res)),
                5,
                (255,0,255))

        ofx = 0.5 * math.cos(-self.robot[2])
        ofy = 0.5 * math.sin(-self.robot[2])
        cv2.line(img,
                (int(self.robot[0]/float(size)*res),int(self.robot[1]/float(size)*res)),
                (int((self.robot[0]+ofx)/float(size)*res),int((self.robot[1]+ofy)/float(size)*res)),
                (255,0,255),
                2
                )


        cv2.imshow("map",img)
        cv2.waitKey()

    def run_impl(self):
        pass


if __name__ == "__main__":
    md = {}
    md["shutdown"] = False

    sim = SIMU("SIMU",None,md)
    sim.init()

    sim.show()
