import fbpy.fb as fb
import fbpy.svg as svg
import fbpy.sprite as sprite
import time
import subprocess
import numpy as np
import curses
import pdb

message1 ="""
              This is a demo of the fbpy module for python. 
              The module is for drawing in the framebuffer.
              This means it basically allows for low-level access to the 
              graphics device
              Why would one want that?
                  1) Skip the overhead of a windowing system on the computer
                  2) Easy, quick and dirty graphics access
                  3) Enjoy the magic of drawing in a tekst console
                  4) Fun
                  5) It is nerdy, geeky, and much pleasure can be gained from that
                  6) Gives some of that pre-os era 8 bit home computer feel
                  7) and before I go on repeating myself I finalize by stating
                     that either u get the point of this awesome, crazy, insane
                     pleasure of meaningless devine bitmanipulation or u dont.
                     In the latter case I will not be able to convince u anyhow
                     and in the former i dont need to.

              By now, u see the workings of the tekst console. Now lets mess it up
              with some graphx shit....
              
          """

message2= """
             We are now on the virtual teletype no.1 a.k.a.
             tty1
             This message is generated using curses.
             fbpy can grab the screen as a bitmap and
             manipulate it, that is what you saw when the
             previous message dissapeared
          """

message3= """
             But we can also gen our own characters...
             Using the built in svg lib and prefab svg charset:
          """

message4= """
             And we have ...
             SPRITES !!!!!!!!!!!!!!!!!!!
                                                           
             and because in fbpy, sprites are simply
             blitted surface objects, we can apply all
             surface features to our sprites. how cool is that?

          """


class Welcome(object):

    main = fb.Surface()
    midd = fb.Surface((10,10),(800,300))
    centor = fb.Surface((80,80),(640,640))
    scrn = None

    @classmethod
    def setup(cls):
        cls.scrn = curses.initscr()
        cls.midd.clear()
        cls.main.clear()
        curses.cbreak()

    @classmethod 
    def curses(cls, message, r,c, align):
        cls.scrn.clear()
        cls.scrn.addstr(10,10,"computer up...")
        for i,s in enumerate(message.splitlines()):
            if align == 'center':
                s=s.center(70)
            for j, kar in enumerate(s):
                cls.scrn.addstr(r+i,c+j,kar)
                time.sleep(.02)
                cls.scrn.refresh()
            time.sleep(0.2)
        cls.centor.clear()
        cls.centor.keepbackground()
        cls.centor.update()

    @classmethod
    def helloworld(cls):
        cls.main.clearscreen()
        cls.main.update()
        cls.midd.pixelstyle = fb.Pixelstyles.faint
        cls.midd.pixelstyle.color.a = 130 
        #cls.midd.rect((0.01,0.01),(0.99,0.99))

        cls.midd.update()
        tekst1 = svg.Text((10,10),"invoking svg module", 1.5, cls.midd)
        time.sleep(.1)
        tekst2 = svg.Text((10,34),"now showing the svg submodules Text class", 1.5,cls.midd)
        time.sleep(.1)
        tekst3 = svg.Text((10,58),"These characters are svg of 200x200 px rendered",1.5,cls.midd)
        time.sleep(.1)
        tekst4 = svg.Text((10,82),"by the polys functionality of fb",1.5,cls.midd)
        cls.midd.update()
        time.sleep(2)
        sprite = cls.midd.get_raw()
        for i in range(1,300,2):
            
            cls.midd.origo = (i,i)
            cls.midd.set_raw(sprite)
            cls.midd.clearframebuffer()
            cls.midd.update()

        time.sleep(2)

        for i in range(150):
            cls.midd.pixelstyle.sigma = 1 
            cls.midd.pixelstyle.blur = 2 
            cls.midd.pixelstyle.blurradius = 1
            cls.midd.pixelstyle.color.a = 170+((255-170)*i/150.0)
            cls.midd.informdriver()
            cls.midd.styledredraw()
            cls.midd.update()

    @classmethod
    def blurrit(cls):
        cls.main.clear()
        cls.main.keepbackground()
        cls.main.pixelstyle.color = fb.Color(20,20,20,10)
        cls.main.pixelstyle.blur = 2
        cls.main.pixelstyle.blurradius = 1
        cls.main.pixelstyle.sigma = 1
        cls.main.styledredraw()
        cls.main.update()
        cls.countdown(5)

    @classmethod
    def rotit(cls):
        R = fb.Trafo()
        S = fb.Trafo()

        R.rotate(0.01)
        S.stretch(0.9, 0.9)
        cls.main.pixelstyle.blur = 0
        cls.main.trafo *=R
        cls.main.trafo *=S
        sprite = cls.main.get_raw()
        domeen = np.linspace(0.02, 0.06, num = 30)
        for i in domeen:
            R.rotate(i)
            cls.main.trafo *= R
            cls.main.trafo *= S
            cls.main.clear()
            cls.main.set_raw(sprite)
            cls.main.styledredraw()
            #cls.main.clearscreen()
            cls.main.update()
        cls.main.clearscreen()

    @classmethod
    def fckmybitchmup(cls):
        svg.Text((10,10),"loading png is also an option", 1.5, cls.midd)
        #time.sleep(2)
        cls.centor.blit("./cylonnoeye.png")
        cls.centor.update()
        #time.sleep(3)
        svg.Text((600,500),"and we can manipulate it", 0.8, cls.midd)
        svg.Text((600,520),"just like them other pix", 0.8, cls.midd)
        cls.main.update()
        #time.sleep(3)

        redeye = fb.Surface((230,400),(100,30))
        shadow = fb.Surface((230,400),(100,30))
        #redeye.blit('./eye.png')
        redeye.pixelstyle.blur = 2
        redeye.pixelstyle.blurradius = 4
        redeye.pixelstyle.sigma = 2
        
        for i in range(1600):
            redeye.clear()
            shadow.clear()
            redeye.trafo.identity()
            redeye.trafo.rotate(-0.06*np.sin(i/1600.0*8*3.14))
            redeye.pixelstyle.color.a = 245+7*np.cos(i/1600.0*16*3.14)
            redeye.origo = (230+90*np.sin(i/1600.0*8*3.14), 400 + 0*np.cos(i/1600.0*8*3.13))
            redeye.blit('./eye.png')
            #redeye.arc((50,15),20,7,0,20,20)
            redeye.styledredraw()
            shadow.update()
            redeye.update()
            shadow.icopyu(redeye)
            if i%5==0:
                #cls.centor.grabsequence("/dev/shm/cylanim")
                pass
        time.sleep(3)
        #cls.centor.pixelstyle.blur = 2
        #cls.centor.pixelstyle.blurradius = 3 
        #cls.centor.pixelstyle.sigma=1
        #cls.centor.pixelstyle.color.a=230
        #for i in range(15):
        #    #cls.centor.trafo.rotate(0.03)
        #    cls.centor.styledredraw()
        #    cls.centor.update()

    @classmethod
    def sprites(cls):
        cls.main.clear()
        cls.main.update()
        cls.main.blit("./stars.png")
        cls.main.update()

        mysprite = sprite.Sprite((0,0),(150,157))

        for i in range(160):
            mysprite.surface.clear()
            mysprite.surface.blit("./fighter_viper_mk1small.png")
            mysprite.surface.trafo.identity()
            mysprite.surface.trafo.rotate(6.28/160.0*i)
            mysprite.surface.styledredraw()
            mysprite.save()

        path1 = range(1400,400,-1)
        path2 = range(400,-150,-1)

        for x in path1:
            mysprite.moveto((x, 350),0)
            time.sleep(0.003)

        for ang in range(160):
            mysprite.moveto((400,350),ang)
            time.sleep(0.01)

        for x in path2:
            mysprite.moveto((x, 350),159)
            time.sleep(0.003)

        time.sleep(3)
        mysprite.hide()

    @classmethod
    def countdown(cls, t):
        for i in range(t):
            cls.scrn.addstr(30,40,"{0}".format(t))
            time.sleep(1)

    @classmethod
    def enough(cls):
        curses.endwin()
        fb.Surface.close()

if __name__ == "__main__":
    Welcome.setup()
    Welcome.curses(message1,10,10,'')
    time.sleep(2)
    Welcome.rotit()
    Welcome.curses(message2,10,10,'')
    time.sleep(3)
    Welcome.curses(message3,10,10,'center')
    time.sleep(3)
    Welcome.main.clearscreen()
    Welcome.helloworld()
    time.sleep(3)
    Welcome.fckmybitchmup()
    time.sleep(3)
    Welcome.curses(message4,10,10,'')
    time.sleep(3)
    Welcome.sprites()
    time.sleep(3)
    Welcome.enough()
