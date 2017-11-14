#import RPi.GPIO as GPIO
import pigpio
from utils import *
import collections

class SingleMotor():
    def __init__(self,a,b,e,enca,encb,name,use_pid=True):
        self.a = a
        self.b = b
        self.e = e
        self.enca = enca
        self.encb = encb
        self.name = name
        self.use_pid = use_pid

        self.lasta = -1
        self.lastb = -1

        self.pi = pigpio.pi()

        self.pi.set_mode(self.a, pigpio.OUTPUT)
        self.pi.set_mode(self.b, pigpio.OUTPUT)
        self.pi.set_mode(self.e, pigpio.OUTPUT)

        self.pi.set_mode(self.enca, pigpio.INPUT)
        self.pi.set_mode(self.encb, pigpio.INPUT)
        self.pi.set_pull_up_down(self.enca, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.encb, pigpio.PUD_UP)

        # configure callbacks
        self.cba=self.pi.callback(self.enca, pigpio.EITHER_EDGE, self.get_state)
        #self.cbb=self.pi.callback(self.encb, pigpio.EITHER_EDGE, self.get_state)

        self.set_mode("release")
        self.speed_ms = 0

        # set up variables for encoder comptuations
        self.old_seq = 0
        self.direction = 0
        self.cnt = 0

        self.PID_UPDATE_INT_MS = 50
        self.pid_ts = 0
        self.pid_queue = collections.deque()
        self.pid_kp = 50.0
        self.pid_ki = 10.0
        self.pid_kd = 2.0
        self.pid_last_error = 0.
        self.pid_integral = 0.

        # setup PWM on enable port
        self.pi.set_PWM_dutycycle(self.e, 0)
        
        # FIXME: remove
        self.outfile = open("/tmp/pid_out_%s_%.2f_%.2f_%.2f.txt" % (self.name, self.pid_kp, self.pid_ki, self.pid_kd), "w")
        self.outfile.write("HEADER: Kp: %f, Ki: %f, Kd: %f\n" % (self.pid_kp, self.pid_ki, self.pid_kd))
        self.outfile.write("HEADER: tsnow, tmpdelta, err, self.pid_integral, deriv, out, out_pwm\n")


    def set_mode(self, d):
        if d == "backward":
            self.direction=-1
            self.pi.write(self.a, 1)
            self.pi.write(self.b, 0)
        elif d == "forward":
            self.direction=1
            self.pi.write(self.a, 0)
            self.pi.write(self.b, 1)
        elif d == "block":
            self.pi.write(self.a, 1)
            self.pi.write(self.b, 1)
        elif d == "release":
            self.pi.write(self.a, 0)
            self.pi.write(self.b, 0)
        else:
            print "Motor: I do not know this direction"

    def get_seq(self):
        a = not self.pi.read(self.enca)
        b = not self.pi.read(self.encb)
        return (a ^ b) | b << 1

    def get_state(self, gpio, level, tick):
        curr = getMs()
        if level == 1:
            self.cnt += self.direction*1
            if self.use_pid:
                self.pid_queue.append(curr) # push ts in a queue 

        if self.use_pid:
            for elem in list(self.pid_queue): # remove elements from queue that are older than 100Ms
                if curr - elem > self.PID_UPDATE_INT_MS:
                    self.pid_queue.popleft()
                else:
                    break

            # PID loop
            dt = curr - self.pid_ts
            if dt >= self.PID_UPDATE_INT_MS:
                #print "[",self.name,"] (",len(self.pid_queue),") Queue: " #, self.pid_queue
                #print "[",self.name,"] DIFF: ", (curr - self.pid_ts)
                # calculate speed in m/s over the last 100Ms
                tmpdelta = self.cnt_to_m(len(self.pid_queue)) # this is the distance of the last 100Ms
                #print self.speed_ms,"-",tmpdelta*(1000./float(self.PID_UPDATE_INT_MS)), "-", self.speed_ms - tmpdelta*(1000./float(self.PID_UPDATE_INT_MS))
                err = self.speed_ms - tmpdelta*(1000./float(dt))
                self.pid_integral += err*dt
                deriv = (err - self.pid_last_error)/dt
                out = self.pid_kp*err + self.pid_ki*self.pid_integral + self.pid_kd*deriv

                # translate "out"-value (m/s) to pwm value
                #if out < 0: out = 0.0
                if out > 0.7: out = 0.7

                if out <= 0:
                    out_pwm = 0 # if we fall below the threshold, there is anyway zero output
                else:
                    out_pwm = min(255, max(0, int(64.46*out*out*out + 310.2*out*out - 2.388*out + 51.16)))


                tsnow = getMs()
                self.outfile.write("%d, %f, %f, %f, %f, %f, %d\n" % (tsnow, tmpdelta, err, self.pid_integral, deriv, out, out_pwm))

                #print "[",self.name,"]-------------------PID: delta: ",tmpdelta*(1000./self.PID_UPDATE_INT_MS),", err: ",err,", out: ", out, ", out_pwm: ", out_pwm
                self.pid_last_error = err
                self.pi.set_PWM_dutycycle(self.e, out_pwm)
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
        self.outfile.close()

