import fbpy.fb as fb
import time

class Flashtext(object):

    def __init__(self, tekst, surface):
        self.tekst = tekst
        self.surface = surface


    def grababunch(self):
        for i in range(30):
            self.surface.grabsequence("/dev/shm/tmp/test")

    def draw(self):
        N=25

        self.snow()

        for i in range(N):
            self.surface.clear()
            self.surface.printxy((300,300),self.tekst, fb.Color(60,60,i,0), fb.Colors.black, 2)
            self.surface.update()
            self.surface.focus = N-i-1

            self.surface.grabsequence("/dev/shm/tmp/test")

        self.grababunch()

        for i in range(N):
            self.surface.clear()
            self.surface.printxy((300,300),self.tekst, fb.Color(0,50-2*i,50-2*i,0), fb.Colors.black, 2)
            self.surface.update()
            self.surface.focus = i

            self.surface.grabsequence("/dev/shm/tmp/test")

    def snow(self):
        self.surface.focus = 1
        for i in range(10):
            self.surface.clear()
            self.surface.snow()
            self.surface.update()
    
            self.surface.grabsequence("/dev/shm/tmp/test")

        self.surface.focus = 25

if __name__ == '__main__':
    win = fb.Surface()

    N = 25

    win.clear()
    win.blur = 2
    win.focus = N
    
    flash = Flashtext("Hello world!!!", win)
    flash.draw()
    flash.tekst = "from fbpy..."
    flash.draw()
    flash.tekst = "the new Python framebuffer module for linux"
    flash.draw()
    flash.tekst = "by Noisegate (c) 2014..."
    flash.draw()

    s=raw_input()

    win.close()
     
