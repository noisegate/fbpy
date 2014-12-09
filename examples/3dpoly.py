import fbpy.fb as fb
import fbpy.sprite as sprite
import numpy as np
import time

if __name__ == '__main__':

    main = fb.Surface()

    mysprite = sprite.Sprite((0,0),(200,200))

    mysprite.surface.dddtrafo

    mysprite.surface.dddtrafo.ez=155
    mysprite.surface.dddtrafo.ex=-100
    mysprite.surface.dddtrafo.ey=-100
    mysprite.surface.dddtrafo.cx = 0
    mysprite.surface.dddtrafo.cy = 0
    mysprite.surface.dddtrafo.cz = 325 

    mini =-100
    maxi = 100
    back =-100 
    front =100
    mysprite.surface.addpoly(   [mini,maxi,maxi,mini,mini],
                                [mini,mini,maxi,maxi,mini],
                                [back,back,back,back,back])
    mysprite.surface.addpoly(   [mini,maxi,maxi,mini,mini],
                                [mini,mini,maxi,maxi,mini],
                                [front,front,front,front,front])
    mysprite.surface.addpoly(   [mini,mini,mini,mini,mini],
                                [mini,mini,maxi,maxi,mini],
                                [back,front,front,back,back])
    mysprite.surface.addpoly(   [maxi,maxi,maxi,maxi,maxi],
                                [mini,mini,maxi,maxi,mini],
                                [back,front,front,back,back])

    mysprite.surface.clear()
    for i in np.arange(0,2*np.pi,0.005):
        mysprite.surface.clear()
        mysprite.surface.dddtrafo.tetay = 2*i
        mysprite.surface.dddtrafo.tetax = 3*i
        mysprite.surface.dddtrafo.tetaz = i
        # mysprite.surface.pixelstyle.blur=2
        # mysprite.surface.pixelstyle.blurradius=1
        # mysprite.surface.pixelstyle.sigma=1
        # mysprite.surface.pixelstyle.color.a = 100
        # mysprite.surface.pixelstyle.color.r = 0
        # mysprite.surface.pixelstyle.color.g = 40
        # mysprite.surface.pixelstyle.color.b = 10
        mysprite.surface.draw3dpolys()
        mysprite.surface.styledredraw()
        mysprite.save()

    N =len(mysprite.spritedata)


    for j in range(30):
        for i in range(N):
            alpha = 2.0*i/N*np.pi
            x = np.cos(alpha)*0+600
            y = np.sin(alpha)*0+300
            mysprite.moveto((x,y),i)
            time.sleep(0.005)
