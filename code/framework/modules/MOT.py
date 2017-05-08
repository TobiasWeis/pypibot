from MP import MP
import RPi.GPIO as GPIO
import time

'''
this class should abstract the motor commands,
so that the rest of the framework can issue
move commands like
move(angle, distance)
'''

class Motor():
    def __init__(self,a,b,e):
        self.a = a
        self.b = b
        self.e = e

        GPIO.setup(self.a, GPIO.OUT)
        GPIO.setup(self.b, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)

        self.set_mode("release")

        # setup PWM on enable port
        self.p = GPIO.PWM(self.e, 100)
        self.p.start(0)

    def set_mode(self, d):
        if d == "back":
            GPIO.output(self.a, GPIO.HIGH)
            GPIO.output(self.b, GPIO.LOW)
        elif d == "forward":
            GPIO.output(self.a, GPIO.LOW)
            GPIO.output(self.b, GPIO.HIGH)
        elif d == "block":
            GPIO.output(self.a, GPIO.HIGH)
            GPIO.output(self.b, GPIO.HIGH)
        elif d == "release":
            GPIO.output(self.a, GPIO.LOW)
            GPIO.output(self.b, GPIO.LOW)
        else:
            print "Motor: I do not know this direction"

    def set_speed(self,speed):
        self.p.ChangeDutyCycle(speed)

    def cleanup(self):
        self.set_speed(0)
        self.set_mode("release")

class MOT(MP):
    def init(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        self.motor1 = Motor(
                        self.config.getint("PINS", "MOTOR1A"),
                        self.config.getint("PINS", "MOTOR1B"),
                        self.config.getint("PINS", "MOTOR1E")
                        )

    def run_impl(self):
        if len(self.md["Move"]) == 2:
            print self.name, " - MOVING!"
            speed = self.md["Move"][0]
            angle = self.md["Move"][1]
            self.md["Move"] = []
            self.motor1.set_mode("forward")
            self.motor1.set_speed(speed)
            time.sleep(2)
            self.motor1.set_speed(0)
            self.motor1.set_mode("release")
            print self.name, " - MOVING DONE!"

    def cleanup(self):
        self.motor1.cleanup()
        GPIO.cleanup()
