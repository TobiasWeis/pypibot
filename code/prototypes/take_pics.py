#!/usr/bin/python

import cv2
import numpy as np

cap = cv2.VideoCapture(0)

cnt = 0
while True:
    ret, img = cap.read()
    cv2.imwrite("img_%08d.png" % cnt, img)
    cnt += 1
