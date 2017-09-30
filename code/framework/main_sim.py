#!/usr/bin/python
'''
pypibot
author: Tobias Weis

- sensing: camera -> picture, objects, etc.
- memory: objects are transferred to memory
- brain: decides how to act
- motion: controls motors
'''

import time
import sys
import select
import ConfigParser

from multiprocessing import Process, Manager

from modules import BRAIN,CAM,US,MEM,MOT,LIDAR
from modules import SIMU
from modules.utils import *

_simulate = True

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

Manager = Manager()
md = Manager.dict()
md["shutdown"] = False
md["WCS"] = Coordinate(0.,0.,0.)
md["starttime"] = getMs()

procs = []

if _simulate:
    lidar = SIMU.SIMU("LIDAR_SIM", Config, md)
else:
    lidar = LIDAR.LIDAR("LIDAR", Config, md)
procs.append(lidar)
lidar.init()
#lidar.start()

'''
cam = CAM.CAM("CAM", Config, md)
procs.append(cam)
cam.start()

us = US.US("US", Config, md)
procs.append(us)
us.start()

mem = MEM.MEM("MEM", Config, md)
procs.append(mem)
mem.start()
'''

brain = BRAIN.BRAIN("BRAIN", Config, md)
brain.init()
procs.append(brain)
#brain.start()

mot = MOT.MOT("MOT", Config, md)
mot.init()
procs.append(mot)
#mot.start()


while not md["shutdown"]:
    brain.run_impl()
    mot.run_impl()
    lidar.run_impl()
    #time.sleep(.2)

    #if "MCS" in md:
    #    md["MCS"]._print()

    #if _simulate:
    #    lidar.show()

    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line:
            print "Keyboard Interrupt, shutting down."
            shutdown = True
            md["shutdown"] = True
        else:
            # stdin is gone/closed, exit
            print "EOF!"
            shutdown = True

for p in procs:
    p.shutdown = True
    p.join()
