import fbpy.sprite
import fbpy.fb as fb
import numpy as np
import time

if __name__ == "__main__":

    #need it, else sprite will give typerror
    main = fb.Surface()

    timew = fb.Surface((0,0),(300,10))

    sprite = fbpy.sprite.Sprite((0,0),(150,157))
    sprite.surface.clear()
    sprite.surface.blit("./fighter_viper_mk1small.png")
    sprite.save()
    for i in range(160):

        sprite.surface.clear()
        sprite.surface.blit("./fighter_viper_mk1small.png")
        sprite.surface.trafo.identity()
        sprite.surface.trafo.rotate(6.28/160.0*i)
        sprite.surface.styledredraw()
        sprite.save()

    main.keepbackground()    
    main.blit("./stars.png")
    main.update()

    tnull = time.time()
    #make it move and debug
    counter = 0
    nom=0
    for j in range(3):
        for i in range(0,301,1):
            t0 = time.time()

            t = i/300.0*2*np.pi
            x = -200*np.cos(t)+600
            y = 20*np.sin(t)+300
            
            nom = int(i/300.0*160)
            sprite.moveto((x,y), nom)

            counter +=1

            if not (counter % 50):
                timew.clear()
                timew.printxy((3,3),"runtime = {0} s".format(time.time()-tnull),1)
                timew.update()

            while((time.time()-t0)<0.005):
                pass
    ra = [700]
    ra.extend(range(350,-200,-1))
    ra.extend(range(800,1366,1))
    for i in ra:
        sprite.moveto((i,300),1)
        time.sleep(0.001)
    ra = [300]
    ra.extend(range(300,-100,-1))
    ra.extend(range(300,766,1))
    for i in ra:
        sprite.moveto((400,i),1)
        time.sleep(0.001)
    ra = [400]
    ra.extend(range(400,-2,-1))
    for i in ra:
        sprite.moveto((1366-i,768-i),1)
        time.sleep(0.001)
    ra = [400]
    ra.extend(range(400,-200,-1))
    for i in ra:
        sprite.moveto((i,i),1)
        time.sleep(0.001)
    ra = [400]
    ra.extend(range(400,-200,-1))
    for i in ra:
        sprite.moveto((1366-i,i-157),1)
        time.sleep(0.001)
    ra = [400]
    ra.extend(range(400,-200,-1))
    for i in ra:
        sprite.moveto((i-150,-i+768),1)
        time.sleep(0.001)


    sprite.hide()
