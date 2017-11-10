#!/usr/bin/python
import matplotlib as mpl
mpl.use('Agg')
import time
import sys
sys.path.append("../framework/modules/")
from SingleMotor import *
import ConfigParser
import numpy as np
import matplotlib.pyplot as plt

Config = ConfigParser.ConfigParser()
Config.read("../framework/config.ini")

motor1 = SingleMotor(
                Config.getint("PINS", "MOTOR1A"),
                Config.getint("PINS", "MOTOR1B"),
                Config.getint("PINS", "MOTOR1E"),
                Config.getint("PINS", "MOTOR1ENCA"),
                Config.getint("PINS", "MOTOR1ENCB"),
                "MOTLEFT",
                False
                )

motor2 = SingleMotor(
                Config.getint("PINS", "MOTOR2A"),
                Config.getint("PINS", "MOTOR2B"),
                Config.getint("PINS", "MOTOR2E"),
                Config.getint("PINS", "MOTOR2ENCA"),
                Config.getint("PINS", "MOTOR2ENCB"),
                "MOTRIGHT",
                False
                )


motor1.set_mode("forward")
motor2.set_mode("forward")

p = 0.1 # how many seconds between delta-updates

speeds = []
for pwm in range(70,255,10):
    motor1.pi.set_PWM_dutycycle(motor1.e, pwm)
    motor2.pi.set_PWM_dutycycle(motor2.e, pwm)

    readings = []
    ss = time.time()
    while time.time() - ss < 5:
        d = motor1.get_delta()
        d2 = motor2.get_delta()
        #print d, " -> ",d*(1./p)," m/s"
        time.sleep(p)

        # disregard first second (that is startup)
        if time.time() - ss > 1:
            readings.append(d*(1./p))

    print "Average speed for PWM-value ",pwm,": ",np.sum(readings)/float(len(readings))
    speeds.append([pwm, np.sum(readings)/float(len(readings))])

    # pause so I can turn the bot
    motor1.pi.set_PWM_dutycycle(motor1.e,0)
    motor2.pi.set_PWM_dutycycle(motor2.e,0)
    time.sleep(5)


motor1.set_mode("release")
motor1.pi.set_PWM_dutycycle(motor1.e, 0)

motor2.set_mode("release")
motor2.pi.set_PWM_dutycycle(motor2.e, 0)


speeds = np.array(speeds)

fig = plt.figure()
plt.plot(speeds[:,0],speeds[:,1])
plt.xlabel("PWM value")
plt.ylabel("Speed (m/s)")
fig.savefig("/tmp/speeds.png")
