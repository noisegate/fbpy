import fbpy.fb as fb
import numpy as np
import time

if __name__ == '__main__':

    win = fb.Surface()
    win.clear()
    #win.fillrect((1,1),(1365,767))
    win.update()    
    subwin = fb.Surface((10,10),(300,300))
    subwin2 = fb.Surface((400,400),(200,200))
    subwin3 = fb.Surface((800,400),(200,200))
    subwin4 = fb.Surface((410,100),(800,24))
    #subwin.fillrect((0,0,0,0),(1.0,1.0))
    backgrnd0 = subwin.get_raw()
    subwin.update()
    graticule  = fb.Surface((400,400),(200,200))
    graticule.clear()
    graticule.pixelstyle.colors = fb.Color(40,40,40,0)
    graticule.pixelstyle.color = fb.Colors.darkgrey
    graticule.fillrect((0.0,0.0),(1.0,1.0))    
    graticule.pixelstyle.color = fb.Colors.grey
    graticule.graticule((0.0,0.0),(1.0,1.0))
    sprite = graticule.get_raw()  
    #subwin4.fillrect((0.0,0.0),(1.0,1.0))
    backgrnd = subwin4.get_raw()

    subwin3.pixelstyle.blur = 2
    subwin3.pixelstyle.blurradius = 2
    subwin3.pixelstyle.sigma = 2
    subwin3.pixelstyle.color = fb.Color(10,30,30,100)
    subwin.pixelstyle.blur = 0
    subwin.pixelstyle.blurradius = 7
    subwin.pixelstyle.sigma = 3
    subwin.pixelstyle.color = fb.Colors.magenta


    for j in range(1):
        t = np.arange(0, 1, 0.01, dtype=np.float)
        x = np.cos(2*t*2*np.pi)*0.5+0.5
        for i in range(600):
            subwin3.clear()
            subwin2.clear()
            subwin.clear()
            subwin4.clear()
            subwin2.set_raw(sprite)
            subwin3.set_raw(sprite)
            subwin4.set_raw(backgrnd)
            subwin.set_raw(backgrnd0)
            subwin3.pixelstyle.sigma=1
            subwin3.printxy((0,0),"Phase:{0}".format(i*0.03), 1)
            subwin4.printxy((2+i,2),time.ctime(), 2)
            y = np.sin(3*t*2*np.pi-(i*0.03))*0.5+0.5 
            subwin2.set_dotstyle(2,1) 
            subwin2.poly(x, y)
            subwin2.set_dotstyle(0,1)
            subwin3.set_dotstyle(2, 1)
            subwin3.pixelstyle.sigma=2
            subwin3.poly(t, y)
            subwin3.set_dotstyle(0, 1)
            subwin.rect((0.0,0.0),(1.0,1.0))
            subwin.arc((0.5,0.5),np.sin(np.pi*i/300.0),np.sin(np.pi*i/300.0),0, 100, 100)

            subwin4.update()
            subwin3.update()
            subwin2.update()
            subwin.update()
            time.sleep(.01)
            #subwin3.grabsequence("/dev/shm/test")
    
    s = raw_input()

    fb.Surface.close()

    
    
