import fbpy.fb as fb
import fbpy.svg as svg
import time
import subprocess
import numpy as np
import curses

class Welcome(object):

    main = fb.Surface()
    midd = fb.Surface((0,0),(800,300))
    scrn = None

    @classmethod 
    def curses(cls):
        cls.scrn = curses.initscr()
        curses.cbreak()
        cls.scrn.addstr(10,10,"computer up...")

    @classmethod
    def helloworld(cls):
        print subprocess.check_output(["clear"])
        cls.midd.pixelstyle = fb.Pixelstyles.faint
        tekst1 = svg.Text((10,10),"initializing fbpy 01", 1.5, cls.midd)
        cls.midd.update()

    @classmethod
    def enough(cls):
        curses.endwin()
        fb.Surface.close()

if __name__ == "__main__":
    Welcome.curses()
    Welcome.helloworld()
    Welcome.enough()
