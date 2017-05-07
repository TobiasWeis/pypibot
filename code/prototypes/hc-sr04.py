#!/usr/bin/python

#Bibliotheken einbinden
import RPi.GPIO as GPIO
import time

GPIO.cleanup()
 
#GPIO Modus (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
#GPIO Pins zuweisen
GPIO_TRIGGER = 8
GPIO_ECHO = 10
 
#Richtung der GPIO-Pins festlegen (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.output(GPIO_TRIGGER, False)
time.sleep(2)
 
def distanz():
    StartZeit = 0
    StopZeit = 0

    print "Start"
    # setze Trigger auf HIGH
    # setze Trigger nach 0.01ms aus LOW
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
 
    # speichere Startzeit
    while GPIO.input(GPIO_ECHO) == 0:
        StartZeit = time.time()
 
    # speichere Ankunftszeit
    while GPIO.input(GPIO_ECHO) == 1:
        StopZeit = time.time()


    print "StartZeit: ", StartZeit
    print "StopZeit: ", StopZeit
 
    # Zeit Differenz zwischen Start und Ankunft
    TimeElapsed = StopZeit - StartZeit
    # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
    # und durch 2 teilen, da hin und zurueck
    distanz = (TimeElapsed * 34300) / 2
 
    return distanz
 
if __name__ == '__main__':
    try:
        while True:
            abstand = distanz()
            print ("Gemessene Entfernung = %.1f cm" % abstand)
            time.sleep(1)
 
        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        GPIO.cleanup()
