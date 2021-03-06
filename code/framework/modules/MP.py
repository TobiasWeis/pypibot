import cv2
import time
import multiprocessing

class MP(multiprocessing.Process):
    def __init__(self, name, config, md):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.config = config
        self.md = md

    def run(self):
        # let the class define some of its class-specific variables
        self.init()

        while not self.md["shutdown"]:
            self.run_impl()

        self.cleanup()

    def run_impl(self):
        raise NotImplementedError

    def init(self):
        print self.name," - Init"
        pass

    def cleanup(self):
        print self.name," - Cleanup"
        pass
