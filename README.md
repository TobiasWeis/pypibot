# PyPiBot

A robot that is controlled by python on a raspberry pi.
The build is rover-like, with four driven wheels.

![PyPiBot](0001.png)

## Parts-List
* Raspberry-Pi B+ V2
* Edimax EW-7811UN Wireless USB Adapter

* Motors: 4x DC 6.0V, 35:1 gear ratio, diameter of shaft: 4mm
* Motor-mounts: 4x DROK 25mm universal dc motor mount
* Motor-driver: 2x L298 dual H-bridge modules

* Tires: 4x GoolRC 1:10 Drift Car Tires
* Tire-mount: 12mm Hex Wheel Adapter for 4mm shaft

## Software
Not yet finished, proposed:
* Python mainloop with subprocesses for motor/sensor/worldmodel/reasoning control
* Motor control: GPIO interfaced with motor-module, speed via PWM-implemention of pyGPIO
* Sensing: camera + ultrasonic modules
* Worldmodel: 2D-map of environment
* Reasoning: Obstacle avoidance, object-tracking, self-loading and finding base
