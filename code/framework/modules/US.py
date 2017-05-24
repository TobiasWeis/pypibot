from MP import MP
import RPi.GPIO as GPIO
import time

class US(MP):
    def init(self):
        self.d = -1

        GPIO.setmode(GPIO.BOARD)
        self.t = self.config.getint("PINS", "US1T")
        self.e = self.config.getint("PINS", "US1E")

        GPIO.setup(self.t, GPIO.OUT)
        GPIO.setup(self.e, GPIO.IN)

        GPIO.output(self.t, False)

    def measure(self):
        st = 0
        et = 0

        GPIO.output(self.t, 1)
        time.sleep(0.00001)
        GPIO.output(self.t, 0)

        while GPIO.input(self.e) == 0:
            st = time.time()

        while GPIO.input(self.e) == 1:
            et = time.time()

        return ((et-st) * 34300) / 2

    def run_impl(self):
        pass
        #d = self.measure()
        #print self.name ," - Distance: ", d
        #self.md["US1"] = d
