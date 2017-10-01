from MP import MP
from utils import *
import numpy as np
import math
import time

'''
this class should abstract the motor commands,
so that the rest of the framework can issue
move commands like
move(angle, distance)
'''

class MOT(MP):
    def init(self):
        self.mcs = Coordinate()
        self.mcs_t = getMs()

        try:
            import RPi.GPIO as GPIO
            from SingleMotor import SingleMotor

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)

            self.motor1 = SingleMotor(
                            self.config.getint("PINS", "MOTOR1A"),
                            self.config.getint("PINS", "MOTOR1B"),
                            self.config.getint("PINS", "MOTOR1E"),
                            self.config.getint("PINS", "MOTOR1ENCA"),
                            self.config.getint("PINS", "MOTOR1ENCB")
                            )

            self.motor2 = SingleMotor(
                            self.config.getint("PINS", "MOTOR2A"),
                            self.config.getint("PINS", "MOTOR2B"),
                            self.config.getint("PINS", "MOTOR2E"),
                            self.config.getint("PINS", "MOTOR2ENCA"),
                            self.config.getint("PINS", "MOTOR2ENCB")
                            )

        except: # no GPIO availabel means we simulate motors
            print "GPIO not available, using simulated motors"
            from SingleMotorSimulated import SingleMotorSimulated
            self.motor1 = SingleMotorSimulated(
                    self.config.getfloat("MOT", "MPERS50"))
            self.motor2 = SingleMotorSimulated(
                    self.config.getfloat("MOT", "MPERS50"))

    def fwd(self,speed):
        self.motor1.set_mode("forward")
        self.motor2.set_mode("forward")
        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)

    def bwd(self, speed):
        self.motor1.set_mode("backward")
        self.motor2.set_mode("backward")
        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)

    def left(self,speed):
        self.motor1.set_mode("forward")
        self.motor2.set_mode("backward")
        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        
    def right(self,speed):
        self.motor1.set_mode("backward")
        self.motor2.set_mode("forward")
        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)
        
    def stop(self):
        self.motor1.set_speed(0)
        self.motor2.set_speed(0)
        self.motor1.set_mode("block")
        self.motor2.set_mode("block")

    def integrate_mcs(self):
        d1=self.motor1.get_delta()
        d2=self.motor2.get_delta()

        b = 0.2
        d = (d1+d2)/2.
        t = Coordinate()
        tmp_a = (d1-d2)/b
        t.x = self.mcs.x + d*math.cos(self.mcs.a + tmp_a )
        t.y = self.mcs.y - d*math.sin(self.mcs.a + tmp_a )
        t.a = self.mcs.a + tmp_a
        return t
        

    def run_impl(self):
        if "Move" in self.md:
            if len(self.md["Move"]) == 2:
                speed = self.md["Move"][0]
                direction = self.md["Move"][1]

                self.md["Move"] = []

                if direction == "forward":
                    print "Motor: FWD"
                    self.fwd(speed)
                elif direction == "backward":
                    print "Motor: BWD"
                    self.bwd(speed)
                elif direction == "left":
                    print "Motor: LEFT"
                    self.left(speed)
                elif direction == "right":
                    print "Motor: RIGHT"
                    self.right(speed)
                elif direction == "stop":
                    print "Motor: STOP"
                    self.stop()

            # integrate motion to perform dead-reckoning
            self.mcs = self.integrate_mcs()
            self.md["MCS"] = self.mcs
            self.mcs_t = getMs() #-- get current time in milliseconds

    def cleanup(self):
        self.motor1.cleanup()
        self.motor2.cleanup()
        GPIO.cleanup()
