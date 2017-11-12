#!/usr/bin/python
#import RPi.GPIO as GPIO
import pigpio
import ConfigParser
import time

# bumpers are wired to ground, and connection is broken on press

Config = ConfigParser.ConfigParser()
Config.read("../framework/config.ini")

blpin = Config.getint("PINS","BUMPERL")
brpin = Config.getint("PINS","BUMPERR")

pi = pigpio.pi()

pi.set_mode(blpin, pigpio.INPUT)
pi.set_mode(brpin, pigpio.INPUT)
pi.set_pull_up_down(blpin, pigpio.PUD_UP)
pi.set_pull_up_down(brpin, pigpio.PUD_UP)

while True:
    leftread = pi.read(blpin)
    rightread = pi.read(brpin)

    print "L: %d - R: %d" % (leftread, rightread)

    time.sleep(1)

