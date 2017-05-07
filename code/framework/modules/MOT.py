from MP import MP
import RPi.GPIO as GPIO
import time

M1A = 3
M1B = 5
M1E = 7

class MOT(MP):
    def init(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(M1A, GPIO.OUT)
        GPIO.setup(M1B, GPIO.OUT)
        GPIO.setup(M1E, GPIO.OUT)

        GPIO.output(3, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)

        self.p = GPIO.PWM(M1E, 100)
        self.p.start(0)


    def run_impl(self):
        if len(self.md["Move"]) == 2:
            print self.name, " - MOVING!"
            speed = self.md["Move"][0]
            angle = self.md["Move"][1]
            self.md["Move"] = []
            self.move(speed, angle)
            print self.name, " - MOVING DONE!"

    def move(self, speed, angle):
        # currently only one motor is working,
        # so we just set the speed
        #
        # also, we need to read encoders to check whether we travelled the distance or not
        # currently: just move for 1 second
        self.p.ChangeDutyCycle(speed)
        time.sleep(2)
        self.p.ChangeDutyCycle(0)

    def cleanup(self):
        GPIO.output(3, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)

        GPIO.cleanup()
