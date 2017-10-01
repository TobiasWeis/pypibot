from MP import MP
import time
import numpy as np
from MAP import *

_debug = False

class BRAIN(MP):
    def init(self):
        self.map = MAP()


    def explore(self):
        # find most unexplored area, and drive there
        pass


    def run_impl(self):
        if "lidar" in self.md:
            if "MCS" in self.md:
                self.md["WCS"] = self.md["MCS"]
            if "lidar_points" in self.md:
                # build map using laser points
                self.map.integrate(self.md["WCS"], self.md["lidar_points"])
                self.map.visualize(((getMs()-self.md["starttime"]) / 1000.),save=True)


            free = True

            for i in range(15,-15,-1):
                m = self.md["lidar"][i][0]
                
                if np.isnan(m):
                    if _debug:
                        print ". ",
                elif m < 1.:
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
        #time.sleep(0.1)

        '''
        if "US1" in self.md:
            if self.md["US1"] < 30:
                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
        '''
