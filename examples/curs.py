import fbpy.fb as fb
import curses
import time

if __name__ == "__main__":
    s = curses.initscr()
    curses.cbreak()
    s.addstr(10,10,"Hello world")

    s.keypad(1)

    key =''

    while (key!=ord('q')):
        key = s.getkey()
        s.addstr(30,30,time.ctime())
        s.refresh()
    
    curses.endwin()
