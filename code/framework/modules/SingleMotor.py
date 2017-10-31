#import RPi.GPIO as GPIO
import pigpio

class SingleMotor():
    def __init__(self,a,b,e,enca,encb):
        self.a = a
        self.b = b
        self.e = e
        self.enca = enca
        self.encb = encb

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

        # set up variables for encoder comptuations
        self.old_seq = 0
        self.direction = 0
        self.cnt = 0

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
        if level == 1:
            self.cnt += 1

        '''
        reada = self.pi.read(self.enca)

        if self.lasta < reada:
            self.cnt += 1
        self.lasta = reada
        '''

    def check_encoder(self):
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

    def get_delta(self):
        #self.check_encoder()
        #self.get_state()
        delta_m = (self.cnt/float(350))*0.26 # circumference
        self.cnt = 0
        return delta_m

    def set_speed(self,speed):
        self.pi.set_PWM_dutycycle(self.e, speed)
        #self.p.ChangeDutyCycle(speed)

    def cleanup(self):
        self.set_speed(0)
        self.set_mode("release")
        self.cba.cancel()
        #self.cbb.cancel()

