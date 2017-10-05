from utils import *

class SingleMotorSimulated():
    def __init__(self,m_per_s):
        self.m_per_s = float(m_per_s)
        self.motion = 0
        self.last_delta_ts = getMs()

    def set_mode(self, d):
        if d == "backward":
            self.motion = -1
        elif d == "forward":
            self.motion = 1
        elif d == "block":
            self.motion = 0
        elif d == "release":
            self.motion = 0
        else:
            print "Motor: I do not know this direction"

    def get_delta(self):
        diff = getMs() - self.last_delta_ts
        diff_s = diff/1000.
        self.last_delta_ts = getMs()
        return diff_s * self.motion * self.m_per_s

    def set_speed(self,speed):
        pass # not implemented yet

    def cleanup(self):
        pass

