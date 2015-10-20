import fbpy.fb as fb
import numpy as np
import time

if __name__ == '__main__':

    win = fb.Surface()
    win.clear()
    win.update()    
    subwin2 = fb.Surface((10,200),(200,200))
    subwin3 = fb.Surface((300,200),(200,200))
    subwin4 = fb.Surface((110,100),(600,24))
    graticule  = fb.Surface((200,200),(200,200))
    graticule.clear()
    graticule.pixelstyle.colors = fb.Color(40,40,40,0)
    graticule.pixelstyle.color = fb.Colors.darkgrey
    graticule.fillrect((0.0,0.0),(1.0,1.0))    
    graticule.pixelstyle.color = fb.Colors.grey
    graticule.graticule((0.0,0.0),(1.0,1.0))
    sprite = graticule.get_raw()  
    backgrnd = subwin4.get_raw()

    subwin3.pixelstyle.blur = 2
    subwin3.pixelstyle.blurradius = 2
    subwin3.pixelstyle.sigma = 2
    subwin3.pixelstyle.color = fb.Color(10,30,30,100)

    for j in range(1):
        t = np.arange(0, 1, 0.01, dtype=np.float)
        x = np.cos(2*t*2*np.pi)*0.5+0.5
        for i in range(600):
            subwin3.clear()
            subwin2.clear()
            subwin4.clear()
            subwin2.set_raw(sprite)
            subwin3.set_raw(sprite)
            subwin4.set_raw(backgrnd)
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

            subwin4.update()
            subwin3.update()
            subwin2.update()
            time.sleep(.001)
            #subwin3.grabsequence("/dev/shm/test")
    
    s = raw_input()

    fb.Surface.close()

    
    
