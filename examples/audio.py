import fbpy.fb as fb
import fbpy.jack as jack
import time

if __name__ == '__main__':
    main = fb.Surface()
    surf = fb.Surface((1000,15),(204,204))
    surf.graticule((0.0,0.0),(1.0,1.0))
    sprite = surf.get_raw()
    ja = jack.Jackaudio()
    
    ja.jackon()
    while 1<2:
        ja.jackread()
        ja.dataL
        x=[]
        yL=[]
        yR=[]
        j=0
        for i,a in enumerate(ja.dataL):
            if (i % 5 == 0):
                j = j+1
                x.append(j)
                yL.append(int(a*20)+80)
                yR.append(int(ja.dataR[i]*20)+120)
        surf.clear()
        surf.set_raw(sprite)
        surf.poly(x, yL)
        surf.poly(x, yR)
        surf.rect((0.0,0.0),(1.0,1.0))
        surf.update()
        time.sleep(0.05)
    ja.jackoff()
    surf.close()
    

