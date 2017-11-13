from MP import MP
import time
import numpy as np
from MAP import *
from utils import *

_debug = False

class BRAIN(MP):
    def init(self):
        self.map = MAP(self.md)

    def explore(self):
        # find most unexplored area, and drive there
        pass

    def run_impl(self):
        # first, check bumper
        if "Bumper" in self.md:
            print "==========================================================="
            print "============  BUMPER           ============================"
            print "==========================================================="
            print "==========================================================="
            # hardcoded evade behavior
            self.md["Move"] = [0.2, "backward"]
            time.sleep(2)
            self.md["Move"] = [0.2, "left"]
            time.sleep(1)

            del self.md["Bumper"]

            #clean up from this round
            del self.md["lidar_points"]
            return

        # next, if we have odometry, save and react to laser input
        if "MCS" in self.md:
            self.md["WCS"] = self.md["MCS"]

            if "lidar_points" in self.md:
                # build map using laser points
                self.map.integrate(self.md["WCS"], self.md["lidar_points"])
                #self.map.visualize(((getMs()-self.md["starttime"]) / 1000.),save=True)
                # save a snapshot of relevant data to files
                '''
                tsnow = getMs()
                np.save("/tmp/%d_LIDAR"%tsnow, self.md["lidar_points"])
                coord = np.array([self.md["WCS"].x, self.md["WCS"].y, self.md["WCS"].a])
                np.save("/tmp/%d_WCS"%tsnow,coord)
                np.save("/tmp/%d_MAPPOINTS"%tsnow, self.map.mappoints)
                np.save("/tmp/%d_TILES"%tsnow, self.map.tiles)
                '''

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
                    self.md["Move"] = [0.2, "left"] # was 0-100, now 0-255
                else:
                    self.md["Move"] = [0.3, "forward"]

                del self.md["lidar_points"]

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
