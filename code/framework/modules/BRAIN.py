from MP import MP
import time
import numpy as np
from MAP import *

_debug = False

class BRAIN(MP):
    def init(self):
        self.map = MAP(self.md)

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

            for i in range(10,-10,-1):
                m = self.md["lidar"][i]
                if np.isnan(m):
                    print ".",
                elif m > 100 and m < 500:
                    print "X",
                    free = False
                else:
                    print "O",

                print " ",
            print

            if not free:
                self.md["Move"] = [25, "left"]
            else:
                self.md["Move"] = [25, "forward"]
                '''
                # try to drive to the least known map cell
                target_coords = np.unravel_index(np.argmin(self.map.tiles), self.map.tiles.shape)
                print "Minimal knowledge at tile: "
                tmp = self.map.tile2coordm(target_coords[1], target_coords[0])
                self.md["target"] = Coordinate(tmp[0], tmp[1], 0)
                self.map.wcs2rcs(self.md["target"])
                # first, rotate until we are facing it
                # transfer map tile (WCS) to RCS to calculate relative angle
                '''

        #time.sleep(0.1)

        '''
        if "US1" in self.md:
            if self.md["US1"] < 30:
                # send motor-command
                self.md["Move"] = [50,0] # speed, angle
        '''
