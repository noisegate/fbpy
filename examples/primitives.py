import fbpy.fb as fb
from fbpy.obj import Ddd
import numpy as np
import time

if __name__ == '__main__':

    main = fb.Surface()
    sub = fb.Surface((400,200),(500,500))
    sub.pixelstyle.color = fb.Color(10,40,10,0)
    sub.pixelstyle.style = fb.Styles.solid
    sub.pixelstyle.blur=1

    objdata = Ddd('./grid0.obj',100)
    objdata.open()
    grid = fb.DDDObject(objdata.x, objdata.y,objdata.z, sub)
    grid.tetax = 0
    grid.tetay = 0
    grid.tetaz = 0
    grid.dx = 00
    grid.dy = 0
    grid.dz = 0
    objdata = Ddd('./cube0.obj',100)
    objdata.open()
    cube = fb.DDDObject(objdata.x,objdata.y,objdata.z,sub)
    cube.dx=200
    cube.tetay=1.2
    cube.dy = 150
    objdata = Ddd('./sphere0.obj',100)
    objdata.open()
    sphere = fb.DDDObject(objdata.x,objdata.y,objdata.z,sub)
    sphere.dx=200
    sphere.tetay=0.2
    sphere.dy = 350
    objdata = Ddd('./cone0.obj',100)
    objdata.open()
    cone = fb.DDDObject(objdata.x,objdata.y,objdata.z,sub)
    cone.dx=100
    cone.tetay=1.6
    cone.dy = 150

    sub.dddtrafo.ex=-250
    sub.dddtrafo.ey=-250
    sub.dddtrafo.tetax=0.0
    sub.dddtrafo.tetay=0.0
    sub.dddtrafo.ez=155
    sub.dddtrafo.cy=180
    sub.dddtrafo.cz=400
    
    #camera

    for i in np.arange(0,6*np.pi,0.01):
        #sub.dddtrafo.tetax = i*3
        sub.dddtrafo.ctetay = -(i)
        sub.dddtrafo.cx = -450*np.sin(i)
        sub.dddtrafo.cz = 450*np.cos(i)
        sub.dddtrafo.cy = 180
        sub.clear()
        sub.pixelstyle.color = fb.Color(10,40,10,0)
        grid.draw()
        cube.draw()
        sphere.draw()
        cone.draw()
        sub.update()
        #sub.grabsequence('/dev/shm/voyager')
        time.sleep(0.01)


