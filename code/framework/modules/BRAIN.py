from MP import MP
import time
import numpy as np
from MAP import *

_debug = False

class BRAIN(MP):
    def init(self):
        self.issued_fwd = False
        self.issued_left = False
        self.issued_right = False
        self.issued_bwd = False
        self.map = MAP()

    def run_impl(self):

        if "lidar" in self.md:

            if "lidar_points" in self.md:
                self.map.integrate(self.md["WCS"], self.md["lidar_points"])
                self.map.visualize()

            # build map using laser points

            free = True

            for i in range(15,-15,-1):
                m = self.md["lidar"][i][0]
                
                if np.isnan(m):
                    if _debug:
                        print ". ",
                elif m < 300:
                    if _debug:
                        print "X ",
                    free = False
                else:
                    if _debug:
                        print "O ",

                if not free:
                    break
            if _debug:
                print

            if not free:
                self.md["Move"] = [35, "left"]
            else:
                self.md["Move"] = [35, "forward"]
        time.sleep(0.1)

        # FIXME: just to test the motor module
        '''
        if not self.issued_fwd:
            self.issued_fwd = True
            self.md["Move"] = [50, "forward"]
        elif not self.issued_left:
            self.issued_left = True
            self.md["Move"] = [50, "left"]
        elif not self.issued_right:
            self.issued_right = True
            self.md["Move"] = [50, "right"]
        elif not self.issued_bwd:
            self.issued_bwd = True
            self.md["Move"] = [50, "backward"]
        time.sleep(2)
        '''

        if "US1" in self.md:
            if self.md["US1"] < 30:
                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
