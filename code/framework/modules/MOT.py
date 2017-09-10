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


try:
    import RPi.GPIO as GPIO

    class Motor():
        def __init__(self,a,b,e,enca,encb):
            self.a = a
            self.b = b
            self.e = e
            self.enca = enca
            self.encb = encb

            GPIO.setup(self.a, GPIO.OUT)
            GPIO.setup(self.b, GPIO.OUT)
            GPIO.setup(self.e, GPIO.OUT)

            GPIO.setup(self.enca, GPIO.IN)
            GPIO.setup(self.encb, GPIO.IN)

            self.set_mode("release")

            # set up variables for encoder comptuations
            self.old_seq = 0
            self.direction = 0
            self.cnt = 0

            # setup PWM on enable port
            self.p = GPIO.PWM(self.e, 100)
            self.p.start(0)

        def set_mode(self, d):
            if d == "backward":
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

        def get_seq(self):
            a = not GPIO.input(self.enca)
            b = not GPIO.input(self.encb)
            return (a ^ b) | b << 1

        def check_encoder(self):
            seq = self.get_seq()
            delta = (seq - self.old_seq) % 4
            self.old_seq = seq

            if delta == 0:
                pass # nothing happened
            elif delta == 1:
                self.direction = 1
                self.cnt += 1
            elif delta == 2:
                self.cnt += 2*self.direction
            elif delta == 3:
                self.direction = -1
                self.cnt -= 1

        def get_delta(self):
            self.check_encoder()
            delta_m = self.cnt/float(35*14*3)*0.265 # circumference
            self.cnt = 0
            return delta_m

        def set_speed(self,speed):
            self.p.ChangeDutyCycle(speed)

        def cleanup(self):
            self.set_speed(0)
            self.set_mode("release")

    class MOT(MP):
        def init(self):
            self.motion = None
            self.mcs = Coordinate()
            self.mcs_t = getMs()

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)

            self.motor1 = Motor(
                            self.config.getint("PINS", "MOTOR1A"),
                            self.config.getint("PINS", "MOTOR1B"),
                            self.config.getint("PINS", "MOTOR1E"),
                            self.config.getint("PINS", "MOTOR1ENCA"),
                            self.config.getint("PINS", "MOTOR1ENCB")
                            )

            self.motor2 = Motor(
                            self.config.getint("PINS", "MOTOR2A"),
                            self.config.getint("PINS", "MOTOR2B"),
                            self.config.getint("PINS", "MOTOR2E"),
                            self.config.getint("PINS", "MOTOR2ENCA"),
                            self.config.getint("PINS", "MOTOR2ENCB")
                            )

            self.motor3 = Motor(
                            self.config.getint("PINS", "MOTOR3A"),
                            self.config.getint("PINS", "MOTOR3B"),
                            self.config.getint("PINS", "MOTOR3E"),
                            self.config.getint("PINS", "MOTOR3ENCA"),
                            self.config.getint("PINS", "MOTOR3ENCB")
                            )

            self.motor4 = Motor(
                            self.config.getint("PINS", "MOTOR4A"),
                            self.config.getint("PINS", "MOTOR4B"),
                            self.config.getint("PINS", "MOTOR4E"),
                            self.config.getint("PINS", "MOTOR4ENCA"),
                            self.config.getint("PINS", "MOTOR4ENCB")
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

            self.motion = "forward"

        def bwd(self, speed):
            self.motor1.set_mode("backward")
            self.motor2.set_mode("backward")
            self.motor3.set_mode("backward")
            self.motor4.set_mode("backward")

            self.motor1.set_speed(speed)
            self.motor2.set_speed(speed)
            self.motor3.set_speed(speed)
            self.motor4.set_speed(speed)

            self.motion = "bacward"

        def left(self,speed):
            self.motor1.set_mode("forward")
            self.motor2.set_mode("forward")
            self.motor3.set_mode("backward")
            self.motor4.set_mode("backward")

            self.motor1.set_speed(speed)
            self.motor2.set_speed(speed)
            self.motor3.set_speed(speed)
            self.motor4.set_speed(speed)
            
            self.motion = "left"

        def right(self,speed):
            self.motor1.set_mode("backward")
            self.motor2.set_mode("backward")
            self.motor3.set_mode("forward")
            self.motor4.set_mode("forward")

            self.motor1.set_speed(speed)
            self.motor2.set_speed(speed)
            self.motor3.set_speed(speed)
            self.motor4.set_speed(speed)
            
            self.motion = "right"

        def stop(self):
            self.motor1.set_speed(0)
            self.motor2.set_speed(0)
            self.motor3.set_speed(0)
            self.motor4.set_speed(0)

            self.motor1.set_mode("block")
            self.motor2.set_mode("block")
            self.motor3.set_mode("block")
            self.motor4.set_mode("block")

            self.motion = None

        def integrate_mcs(self,t):
            x = self.mcs.x + t.x*math.cos(self.mcs.a) - t.y*math.sin(self.mcs.a)
            y = self.mcs.y + t.x*math.sin(self.mcs.a) + t.y*math.cos(self.mcs.a)
            a = self.mcs.a + t.a
            return Coordinate(x,y,a)

        def calc_t(self):
            # get all encoder values
            d1=self.motor1.get_delta()
            d2=self.motor2.get_delta()
            d3=self.motor3.get_delta()
            d4=self.motor4.get_delta()

            #-- calculate movement of bot
            t = Coordinate()
            #t.x = np.mean([d1,d2,d3,d4]) # FIXME: only works if all go fwd/bwd
            t.x = np.max([d1,d2,d3,d4])
            # FIXME: integration missing, only for testing!

            return t
            

        def run_impl(self):
            # integrate motion to perform dead-reckoning
            #self.mcs = self.integrate_mcs(self.calc_t())
            #self.md["MCS"] = self.mcs
            #self.mcs_t = getMs() #-- get current time in milliseconds

            # FIXME: this needs to be transformed in order to still
            # be able to read encoders fast enough
            if "Move" in self.md:
                if len(self.md["Move"]) == 2:
                    #-- get the command
                    print self.name, " - MOVING!"
                    speed = self.md["Move"][0]
                    direction = self.md["Move"][1]
                    #-- take it out of the queue
                    self.md["Move"] = []
                    #-- execute
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

                    time.sleep(1)
                    self.stop()
                    print self.name, " - MOVING DONE!"

        def cleanup(self):
            self.motor1.cleanup()
            self.motor2.cleanup()
            self.motor3.cleanup()
            self.motor4.cleanup()
            GPIO.cleanup()

except:
    class MOT(MP):
        def init(self):
            self.motion = None
            self.mcs = Coordinate()
            self.mcs_t = getMs()

        def fwd(self,speed):
            self.motion = "forward"

        def bwd(self, speed):
            self.motion = "bacward"

        def left(self,speed):
           self.motion = "left"

        def right(self,speed):
           self.motion = "right"

        def stop(self):
           self.motion = None

        def integrate_mcs(self,t):
            '''
            x = self.mcs.x + t.x*math.cos(self.mcs.a) - t.y*math.sin(self.mcs.a)
            y = self.mcs.y + t.x*math.sin(self.mcs.a) + t.y*math.cos(self.mcs.a)
            '''
            x = self.mcs.x + t.x*math.cos(self.mcs.a) 
            y = self.mcs.y - t.x*math.sin(self.mcs.a)

            a = self.mcs.a + t.a
            return Coordinate(x,y,a)

        def calc_t(self):
            diff = getMs() - self.mcs_t #-- calculate difference to last timestamp
            diff_s = diff/1000.

            #-- calculate movement of bot
            t = Coordinate()
            if self.motion == "forward":
                t.x = diff_s * self.config.getfloat("MOT", "MPERS50") 
            elif self.motion == "backward":
                t.x = -diff_s * self.config.getfloat("MOT", "MPERS50") 
            elif self.motion == "left":
                t.a = diff_s * math.radians(self.config.getfloat("MOT", "APERS50"))
            elif self.motion == "right":
                t.a = -diff_s * math.radians(self.config.getfloat("MOT", "APERS50"))

            return t
            

        def run_impl(self):
            # integrate motion to perform dead-reckoning
            self.mcs = self.integrate_mcs(self.calc_t())
            self.mcs_t = getMs() #-- get current time in milliseconds

            self.md["MCS"] = self.mcs 

            if "Move" in self.md:
                if len(self.md["Move"]) == 2:
                    #-- get the command
                    print self.name, " - MOVING!"
                    speed = self.md["Move"][0]
                    direction = self.md["Move"][1]
                    #-- take it out of the queue
                    self.md["Move"] = []
                    #-- execute
                    if direction == "forward":
                        #print "Motor: FWD"
                        self.fwd(speed)
                    elif direction == "backward":
                        #print "Motor: BWD"
                        self.bwd(speed)
                    elif direction == "left":
                        #print "Motor: LEFT"
                        self.left(speed)
                    elif direction == "right":
                        #print "Motor: RIGHT"
                        self.right(speed)

        def cleanup(self):
            pass

