import RPi.GPIO as GPIO

class SingleMotor():
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

