import fbpy.fb as fb

if __name__ == '__main__':
    main = fb.Surface()

    sub = fb.Surface((0,0),(800,100))

    sub.clear()

    sub.pixelstyle.color = fb.Color(40,40,40,255)
    sub.fillrect((0.0, 0.0),(1.0,1.0))

    sub.pixelstyle = fb.Pixelstyles.sharp
    sub.pixelstyle.color = fb.Colors.darkgrey

    sub.printxy((10,10),"Drawing in the framebuffer is fun!",2)
    #sub.line((0,35),(800,35))

    sub.pixelstyle = fb.Pixelstyles.faint
    sub.pixelstyle.blur = 2
    sub.pixelstyle.blurradius = 8
    sub.pixelstyle.sigma = 4
    sub.pixelstyle.color = fb.Color(2,2,2,200)
    sub.printxy((10,10+24+3),"Drawing in the framebuffer is fun!",2)
    sub.grabsilent("../Doc/source/images/test.png")

    main.close()

