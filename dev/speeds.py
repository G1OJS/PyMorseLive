import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

im = plt.imshow(np.random.randn(10,100))
a = np.zeros((10, 100), dtype = np.int16)
t = time.time()
def update(i):
    global a, t
    a[:, i % 100] = np.random.randn(10)
    im.set_array(a)
    if((i % 100) == 0):
        print((time.time()-t)/100)
        t = time.time()
    return im, 

ani = FuncAnimation(plt.gcf(), update, frames=range(100), interval=1, blit=True)

plt.show()
