import fbpy.fb as fb
import time

main = fb.Surface()
win = fb.Surface((100,100),(300,200))
win.pixelstyle = fb.Pixelstyles.faint
win.pixelstyle.sigma = 2
win.pixelstyle.color.r = 3
win.pixelstyle.color.g = 3
win.pixelstyle.color.b = 3

for i in range(30):
    win.clear()
    print win.winsize
    win.snow()
    win.update()
    win.grabsequence("/dev/shm/snow")

s=raw_input()

main.close()
win.close()
