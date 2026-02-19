import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

im = plt.imshow(np.random.randn(10,100))
a = np.zeros((10, 100), dtype = np.int16)
def update(i):
    global a
    a[:, i % 100] = np.random.randn(10)
    im.set_array(a)
    return im, 

ani = FuncAnimation(plt.gcf(), update, frames=range(1000), interval=0.1, blit=True)

plt.show()
