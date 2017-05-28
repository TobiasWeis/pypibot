import time
import math

def getMs():
    return int(round(time.time() * 1000))

class Coordinate():
    def __init__(self, x=0., y=0., a=0.):
        self.x=x
        self.y=y
        self.a=a
        
    def _print(self):
        print self.x,",",self.y," @ ", math.degrees(self.a)

