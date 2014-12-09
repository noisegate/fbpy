import fbpy.fb as fb
import numpy as np
import time

if __name__ == '__main__':

    main = fb.Surface()

    sub = fb.Surface((0,0),(300,300))
    sub.dddtrafo

    sub.dddtrafo.ez=155
    sub.dddtrafo.ex=-100
    sub.dddtrafo.ey=-100
    sub.dddtrafo.cx = 0
    sub.dddtrafo.cy = 0
    sub.dddtrafo.cz = 325 

    mini =-100
    maxi = 100
    back =-100 
    front =100
    sub.addpoly(   [mini,maxi,maxi,mini,mini],
                   [mini,mini,maxi,maxi,mini],
                   [back,back,back,back,back])
    sub.addpoly(   [mini,maxi,maxi,mini,mini],
                   [mini,mini,maxi,maxi,mini],
                   [front,front,front,front,front])
    sub.addpoly(   [mini,mini,mini,mini,mini],
                   [mini,mini,maxi,maxi,mini],
                   [back,front,front,back,back])
    sub.addpoly(   [maxi,maxi,maxi,maxi,maxi],
                   [mini,mini,maxi,maxi,mini],
                   [back,front,front,back,back])

    for i in np.arange(0,2*np.pi,0.005):
        sub.clear()
        sub.dddtrafo.tetay = 2*i
        sub.dddtrafo.tetax = 3*i
        sub.dddtrafo.tetaz = i
        sub.dddtrafo.ctetax = 0.0
        sub.dddtrafo.ctetay = 0.0
        sub.dddtrafo.ctetaz = 0.0
        sub.draw3dpolys()
        time.sleep(0.005)
        sub.update()

