from MP import MP
import pigpio
import time

'''
read the bumper state and put in global dict
'''

class BUMPER(MP):
    def init(self):
        self.pi = pigpio.pi()

        self.blpin = self.config.getint("PINS","BUMPERL")
        self.brpin = self.config.getint("PINS","BUMPERR")

        self.pi.set_mode(self.blpin, pigpio.INPUT)
        self.pi.set_mode(self.brpin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.blpin, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.brpin, pigpio.PUD_UP)

        self.cbl=self.pi.callback(self.blpin, pigpio.RISING_EDGE, self.bumper_pressed)
        self.cbr=self.pi.callback(self.brpin, pigpio.RISING_EDGE, self.bumper_pressed)

    def bumper_pressed(self,gpio,level,tick):
        self.md["Bumper"] = [1,1]

    def run_impl(self):
        pass

    def cleanup(self):
        self.cbl.cancel()
        self.cbr.cancel()

