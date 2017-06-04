#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np

with open("ticks.txt", "r") as f:
    content = f.readlines()

ticks = []
for line in content:
    ticks.append(line.split(",")[:])
ticks = np.array(ticks).astype(np.float64)

plt.plot(ticks[:,2], ticks[:,0]+1.2, 'k-', label='A')
plt.plot(ticks[:,2], ticks[:,1], 'b-', label='B')
plt.legend()

plt.show()



