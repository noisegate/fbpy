import fbpy.fb as fb
import time

if __name__ == '__main__':

    main = fb.Surface()

    sub = fb.Surface((300,300),(400,400))

    R = fb.Trafo()
    S = fb.Trafo()

    sub.trafo.stretch(0.05,0.05)
    R.rotate(0.08)
    S.stretch(1.02,1.02)

    for i in range(1,1200):

        sub.clear()

        sub.trafo*=R
        if i<200:
            sub.trafo*=S

        if i==1199:
            sub.trafo.identity()

        sub.rect((0.4,0.4),(0.6,0.6))
        sub.printxy((.4,0.5),"hahahahihi",1)
        sub.arc((0.5,0.5),60,40,0,100,100)
        sub.update()
        time.sleep(0.01)
        #sub.grabsequence("/dev/shm/rot")

