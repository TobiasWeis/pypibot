import cv2
from MP import MP

class CAM(MP):
    def init(self):
        self.objseen = False

    def run_impl(self):
        if not self.objseen:
            print "CAM: inserting ball"
            self.objseen = True
            self.md["Objects"] = ["Ball"]

        print "IMPL"
