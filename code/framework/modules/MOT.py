from MP import MP
import RPi.GPIO as GPIO
from utils import *
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
	self.mcs = utils.Coordinate()
        self.mcs_t = utils.getMs()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        self.motor1 = Motor(
                        self.config.getint("PINS", "MOTOR1A"),
                        self.config.getint("PINS", "MOTOR1B"),
                        self.config.getint("PINS", "MOTOR1E")
                        )

        self.motor2 = Motor(
                        self.config.getint("PINS", "MOTOR2A"),
                        self.config.getint("PINS", "MOTOR2B"),
                        self.config.getint("PINS", "MOTOR2E")
                        )

        self.motor3 = Motor(
                        self.config.getint("PINS", "MOTOR3A"),
                        self.config.getint("PINS", "MOTOR3B"),
                        self.config.getint("PINS", "MOTOR3E")
                        )

        self.motor4 = Motor(
                        self.config.getint("PINS", "MOTOR4A"),
                        self.config.getint("PINS", "MOTOR4B"),
                        self.config.getint("PINS", "MOTOR4E")
                        )

    def fwd(self,speed):
        self.motor1.set_mode("forward")
        self.motor2.set_mode("forward")
        self.motor3.set_mode("forward")
        self.motor4.set_mode("forward")

        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        self.motor3.set_speed(speed)
        self.motor4.set_speed(speed)

    def bwd(self, speed):
        self.motor1.set_mode("backward")
        self.motor2.set_mode("backward")
        self.motor3.set_mode("backward")
        self.motor4.set_mode("backward")

        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        self.motor3.set_speed(speed)
        self.motor4.set_speed(speed)

    def left(self,speed):
        self.motor1.set_mode("backward")
        self.motor2.set_mode("backward")
        self.motor3.set_mode("forward")
        self.motor4.set_mode("forward")

        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        self.motor3.set_speed(speed)
        self.motor4.set_speed(speed)

    def right(self,speed):
        self.motor1.set_mode("forward")
        self.motor2.set_mode("forward")
        self.motor3.set_mode("backward")
        self.motor4.set_mode("backward")

        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        self.motor3.set_speed(speed)
        self.motor4.set_speed(speed)

    def stop(self):
        self.motor1.set_speed(0)
        self.motor2.set_speed(0)
        self.motor3.set_speed(0)
        self.motor4.set_speed(0)

        self.motor1.set_mode("block")
        self.motor2.set_mode("block")
        self.motor3.set_mode("block")
        self.motor4.set_mode("block")

    def integrate(self,t):
	x = self.mcs.x + t.x*math.cos(self.mcs.a) - t.y*math.sin(self.mcs.a)
	y = self.mcs.y + t.x*math.sin(self.mcs.a) + t.y*math.cos(self.mcs.a)
	a = self.mcs.a + t.a
	return Coordinate(x,y,a)

    def calc_t(self):
        diff = getMs() - self.mcs_t #-- calculate difference to last timestamp
	diff_s = diff/1000.

        #-- calculate movement of bot
	t = Coordinate()
        if self.motion == forward:
            t.x = diff_s * self.config.getfloat("MOT", "MPERS50")
        elif self.motion == backward:
            t.x = -diff_s * self.config.getfloat("MOT", "MPERS50")
        elif self.motion == left:
            t.a = diff_s * self.config.getfloat("MOT", "APERS50")
	elif self.motion == right:
            t.a = -diff_s * self.config.getfloat("MOT", "APERS50")

	return t
        

    def run_impl(self):
        # integrate motion to perform dead-reckoning
        self.mcs = self.integrate_mcs(self.calc_t())
        self.mcs_t = getMs() #-- get current time in milliseconds

        if "Move" in self.md:
            if len(self.md["Move"]) == 2:
                #-- get the command
                print self.name, " - MOVING!"
                speed = self.md["Move"][0]
                angle = self.md["Move"][1]
                #-- take it out of the queue
                self.md["Move"] = []
                #-- execute
                self.fwd(speed)
                time.sleep(2)
                self.stop()
                print self.name, " - MOVING DONE!"

    def cleanup(self):
        self.motor1.cleanup()
        GPIO.cleanup()
