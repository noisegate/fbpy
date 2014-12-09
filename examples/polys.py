import fbpy.fb as fb
import fbpy.svg as svg
import numpy as np

if __name__ == '__main__':
    main = fb.Surface()
    win = fb.Surface((00,00),(1300,400))
    win.pixelstyle = fb.Pixelstyles.faint
    win.pixelstyle.blurradius = 4
    win.pixelstyle.color = fb.Color(0,40,0,100)
    textl1 = svg.Text((10,10),"TESTING FBPY V 0_1;",1.5,win)
    textl2 = svg.Text((10,32),"THIS IS WHAT IT LOOKS LIKE :)",1.5,win)
    textl3 = svg.Text((10,54),"(DO NEED SOME WORK ON THE CHAR GEN ##)",1.5,win)
    textl4 = svg.Text((10,76),"$OTHERWISE QUIET FUNCTIONAL$",1.5,win)
    textl5 = svg.Text((10,98),"2014_JUN",1.5,win)
    textl6 = svg.Text((10,132),"NOISEGATE IS HAVING A BLAST",1.5,win)

    win.clear() 
    s = raw_input()
    fb.Surface.close()

