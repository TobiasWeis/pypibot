#!/usr/bin/python
'''
author: Tobias Weis
'''

import sys,os
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import glob

sns.set()


#HEADER: tsnow, tmpdelta, err, self.pid_integral, deriv, out, out_pwm
strings = ["tsnow", "tmpdelta", "err", "pid_integral", "deriv", "out", "out_pwm"]


# read files
files = glob.glob("*LEFT*.txt")

for f in files:
    lfile = open(f, "r")
    rfile = open(f.replace("LEFT","RIGHT"), "r")
    #lfile = open("pid_out_MOTLEFT_20.00_0.00_0.00.txt", "r")
    #rfile = open("pid_out_MOTRIGHT_20.00_0.00_0.00.txt", "r")

    valuelist = []
    valuelist_r = []

    for lidx, line in enumerate(lfile):
        if lidx == 0:
            rest,kd = line.strip("\n").split(", Kd:")
            rest,ki = rest.split(", Ki:")
            rest,kp = rest.split("Kp:")
            kd = float(kd.strip(","))
            ki = float(ki.strip(","))
            kp = float(kp.strip(","))
        if lidx >= 2:
            valuelist.append(line.split(","))

    for lidx, line in enumerate(rfile):
        if lidx >= 2:
            valuelist_r.append(line.split(","))


    valuelist = np.array(valuelist, dtype=np.float64)
    valuelist_r = np.array(valuelist_r, dtype=np.float64)


    def myplot(valuelist_r, name, kp,ki,kd):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        plt.title("%s Motor, constants: Kp: %f, Ki: %f, Kd: %f" % (name, kp,ki,kd))
        mints = valuelist_r[0,0]
        print("mints:",mints)
        for i in range(6):
            #fig.add_subplot(2,3,i+1)
            #plt.title(strings[i+1])
            if strings[i+1] == "tmpdelta":
                ax1.plot(valuelist_r[:,0]-mints, valuelist_r[:,i+1]*50, label=strings[i+1]) # tmpdelta is for 100Ms only
            elif strings[i+1] == "err":
                ax1.plot(valuelist_r[:,0]-mints, valuelist_r[:,i+1], 'r-^', label=strings[i+1]) # tmpdelta is for 100Ms only
            elif strings[i+1] == "out_pwm":
                ax2 = ax1.twinx()
                ax2.plot(valuelist_r[:,0]-mints, valuelist_r[:,i+1],'ok--', label=strings[i+1])
            elif strings[i+1] == "pid_integral":
                ax1.plot(valuelist_r[:,0]-mints, valuelist_r[:,i+1], label=strings[i+1])
                pass
            else:
                ax1.plot(valuelist_r[:,0]-mints, valuelist_r[:,i+1], label=strings[i+1])
        ax1.axhline(0.3, color='yellow', label="setpoint")

        #plt.ylim((-0.3,0.3))
        ax1.legend()

    myplot(valuelist, "Left", kp,ki,kd)
    myplot(valuelist_r, "Right", kp,ki,kd)

plt.show()


