import cv2
import time
import multiprocessing

class MP(multiprocessing.Process):
    def __init__(self, name, config, md):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.md = md

    def run(self):
        # let the class define some of its class-specific variables
        self.defvars()

        while not self.md["shutdown"]:
            print self.name
            self.run_impl()
            time.sleep(1)

        self.cleanup()

    def run_impl(self):
        raise NotImplementedError

    def defvars(self):
        print self.name," - Defvars"
        pass

    def cleanup(self):
        print self.name," - Cleanup"
        pass
