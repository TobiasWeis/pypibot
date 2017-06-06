from MP import MP
import time
import numpy as np

class BRAIN(MP):
    def init(self):
        self.issued_fwd = False
        self.issued_left = False
        self.issued_right = False
        self.issued_bwd = False

    def run_impl(self):
        '''
        if "Lidar" in self.md:
            #print self.md["Lidar"]
            for i in range(10):
                m = self.md["Lidar"][i]

                if np.isnan(m):
                    print ".",
                elif m > 100 and m < 300:
                    print "X",
                elif m >= 300:
                    print "O",
                elif m < 100:
                    print ":",
            print
            time.sleep(0.5)

        '''

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
