import fbpy.fb as fb
import time
import subprocess 

#just a demo of some cool stuff 
#you can do with the framebuffer library

class Systeminfo(object):

    def __init__(self):
        self.temp1 =-1
        self.temp2 =-1
        self.uptime = -1

    def update(self):
        temp = subprocess.check_output(['sensors'])
        uptime = subprocess.check_output(['uptime'])
        dummy = temp.splitlines()

        self.temp1 = dummy[2]
        self.temp2 = dummy[3]

        dummy = uptime.split(",")
        self.uptime = ".".join([dummy[-3], dummy[-2], dummy[-1]])

        return 0

if __name__ == "__main__":

    systeminfo = Systeminfo()
    main = fb.Surface()
    win = fb.Surface((main.width-300,0),(300,42))
 
    while(True):
        grey = fb.Colors.grey
        darkgrey = fb.Colors.darkgrey
        grey.alpha = 100
        darkgrey.alpha = 4

        try:
            win.clear()
            win.printxy((2,2),time.ctime(), 1)

            systeminfo.update()

            win.printxy((2,12), systeminfo.temp1, 1)
            win.printxy((2,22), systeminfo.temp2, 1)

            win.printxy((2,32), systeminfo.uptime, 1)

            win.rect((0.0,0.0),(1.0,1.0))

            win.update()

            time.sleep(1)


        except (KeyboardInterrupt, SystemExit):
            fb.Surface.close()
            print "exitted correctly..."

