import fbpy.fb as fb
import numpy as np
import time

if __name__ == '__main__':

    main = fb.Surface()

    sub = fb.Surface((700,300),(500,500))

    grid = fb.Surface((700,300),(500,500))

    sub.dddtrafo.ez=155
    sub.dddtrafo.ex=-250
    sub.dddtrafo.ey=-250
    sub.dddtrafo.cx = 0
    sub.dddtrafo.cy = 40
    sub.dddtrafo.cz = 325 
    grid.dddtrafo.ez=155
    grid.dddtrafo.ex=-250
    grid.dddtrafo.ey=-250
    grid.dddtrafo.cx = 0
    grid.dddtrafo.cy = 40
    grid.dddtrafo.cz = 325
    grid.pixelstyle.color = fb.Color(0,100,0,0)

    mini =-50
    maxi = 50
    back =-50 
    front =50
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


    for x in range(-200,200,20):
        grid.addpoly([x,x],[-200,200],[0,0])
        grid.addpoly([-200,200],[x,x],[0,0])

    for i in np.arange(0,2*np.pi,0.005):
        cx = 325*np.sin(i)
        cz = 325*np.cos(i)
        cy = 40
        sub.clear()
        grid.dddtrafo.tetay = 0.0
        grid.dddtrafo.tetax = 1.5
        grid.dddtrafo.tetaz = 0.0 
        grid.dddtrafo.ctetax = 0.0
        grid.dddtrafo.ctetay = i
        grid.dddtrafo.ctetaz = 0.0
        grid.dddtrafo.cx = cx
        grid.dddtrafo.cz = cz
        grid.dddtrafo.cy = cy
        grid.clear()
        grid.draw3dpolys()
        sub.dddtrafo.tetay = 2*i
        sub.dddtrafo.tetax = 3*i         
        sub.dddtrafo.tetaz = i                  
        sub.dddtrafo.ctetax = 0.0      
        sub.dddtrafo.ctetay = i
        sub.dddtrafo.ctetaz = 0.0
        sub.dddtrafo.cx = cx
        sub.dddtrafo.cz = cz
        sub.dddtrafo.cy = cy
        sub.draw3dpolys()
        grid.update()
        sub.update()
        time.sleep(0.005) 
