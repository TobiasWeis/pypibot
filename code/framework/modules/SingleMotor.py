#import RPi.GPIO as GPIO
import pigpio
from utils import *
import collections

class SingleMotor():
    def __init__(self,a,b,e,enca,encb,name):
        self.a = a
        self.b = b
        self.e = e
        self.enca = enca
        self.encb = encb
        self.name = name

        self.lasta = -1
        self.lastb = -1

        self.pi = pigpio.pi()

        self.pi.set_mode(self.a, pigpio.OUTPUT)
        self.pi.set_mode(self.b, pigpio.OUTPUT)
        self.pi.set_mode(self.e, pigpio.OUTPUT)
        '''
        GPIO.setup(self.a, GPIO.OUT)
        GPIO.setup(self.b, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)
        '''

        self.pi.set_mode(self.enca, pigpio.INPUT)
        self.pi.set_mode(self.encb, pigpio.INPUT)
        self.pi.set_pull_up_down(self.enca, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.encb, pigpio.PUD_UP)
        '''
        GPIO.setup(self.enca, GPIO.IN)
        GPIO.setup(self.encb, GPIO.IN)
        '''

        # configure callbacks
        self.cba=self.pi.callback(self.enca, pigpio.EITHER_EDGE, self.get_state)
        #self.cbb=self.pi.callback(self.encb, pigpio.EITHER_EDGE, self.get_state)

        self.set_mode("release")
        self.speed_ms = 0

        # set up variables for encoder comptuations
        self.old_seq = 0
        self.direction = 0
        self.cnt = 0

        self.PID_UPDATE_INT_MS = 100
        self.pid_ts = 0
        self.pid_queue = collections.deque()
        self.pid_kp = 5000.
        self.pid_ki = 500.
        self.pid_kd = 10.
        self.pid_last_error = 0.
        self.pid_integral = 0.

        # setup PWM on enable port
        self.pi.set_PWM_dutycycle(self.e, 0)
        #self.p = GPIO.PWM(self.e, 100)
        #self.p.start(0)

    def set_mode(self, d):
        if d == "backward":
            self.direction=-1
            self.pi.write(self.a, 1)
            self.pi.write(self.b, 0)
            #GPIO.output(self.a, GPIO.HIGH)
            #GPIO.output(self.b, GPIO.LOW)
        elif d == "forward":
            self.direction=1
            self.pi.write(self.a, 0)
            self.pi.write(self.b, 1)
            #GPIO.output(self.a, GPIO.LOW)
            #GPIO.output(self.b, GPIO.HIGH)
        elif d == "block":
            self.pi.write(self.a, 1)
            self.pi.write(self.b, 1)
            #GPIO.output(self.a, GPIO.HIGH)
            #GPIO.output(self.b, GPIO.HIGH)
        elif d == "release":
            self.pi.write(self.a, 0)
            self.pi.write(self.b, 0)
            #GPIO.output(self.a, GPIO.LOW)
            #GPIO.output(self.b, GPIO.LOW)
        else:
            print "Motor: I do not know this direction"

    def get_seq(self):
        a = not self.pi.read(self.enca)
        b = not self.pi.read(self.encb)
        #a = not GPIO.input(self.enca)
        #b = not GPIO.input(self.encb)
        return (a ^ b) | b << 1

    def get_state(self, gpio, level, tick):
        curr = getMs()
        if level == 1:
            self.cnt += self.direction*1
            self.pid_queue.append(curr) # push ts in a queue 
            # remove elements from queue that are older than 100Ms

        for elem in list(self.pid_queue):
            if curr - elem > 100:
                self.pid_queue.popleft()

        # PID loop
        '''
        self.pid_kp = 1.
        self.pid_ki = 1.
        self.pid_kd = 1.
        self.pid_last_error = 0.
        self.pid_integral = 0.
        '''

        if (curr - self.pid_ts) >= self.PID_UPDATE_INT_MS:
            print "[",self.name,"] (",len(self.pid_queue),") Queue: " #, self.pid_queue
            print "[",self.name,"] DIFF: ", (curr - self.pid_ts)
            # calculate speed in m/s over the last 100Ms
            tmpdelta = self.cnt_to_m(len(self.pid_queue)) # this is the distance of the last 100Ms
            err = self.speed_ms - abs(tmpdelta*(1000./self.PID_UPDATE_INT_MS))
            self.pid_integral += err
            deriv = (err - self.pid_last_error)/(1000./self.PID_UPDATE_INT_MS)
            out = max(0,min(255, int(self.pid_kp*err + self.pid_ki*self.pid_integral + self.pid_kd*deriv)))

            print "[",self.name,"]-------------------PID: delta: ",tmpdelta,", err: ",err,", out: ", out
            self.pid_last_error = err
            self.pi.set_PWM_dutycycle(self.e, out)
            self.pid_ts = curr

    def check_encoder(self):
        '''
        here for legacy reasons
        '''
        seq = self.get_seq()
        delta = (seq - self.old_seq) % 4
        self.old_seq = seq

        if delta == 0:
            pass # nothing happened
        elif delta == 1:
            self.cnt += 1
        elif delta == 2:
            self.cnt += 2*self.direction
        elif delta == 3:
            self.cnt -= 1

    def cnt_to_m(self,cnt):
        return (cnt/float(350))*0.26 # circumference

    def get_delta(self):
        '''
        called from outside.
        cnt updated through interrupts and callback to get_state
        '''
        #self.check_encoder()
        delta_m = self.cnt_to_m(self.cnt) 
        self.cnt = 0
        return delta_m

    def set_speed(self,speed):
        '''
        with the PID, this speed should be in m/s
        '''
        self.speed_ms = speed
        self.get_state(0,0,0)
        #self.pi.set_PWM_dutycycle(self.e, speed)
        #self.p.ChangeDutyCycle(speed)

    def cleanup(self):
        self.pi.set_PWM_dutycycle(self.e, 0)
        self.set_mode("release")
        self.cba.cancel()
        #self.cbb.cancel()

