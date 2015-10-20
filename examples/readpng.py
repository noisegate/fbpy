import fbpy.fb as fb

if __name__ == '__main__':

    main = fb.Surface()

    main.clear()
    main.blit("./cylon.png")

    main.pixelstyle.color = fb.Color(40,40,60,100)
    main.pixelstyle.blur=2
    main.pixelstyle.blurradius=4
    main.pixelstyle.sigma=1

    main.printxy((0.3,0.5),"fbpy: by your command...",2)
    main.update()

    main.grab("byyrcmnd.png")

    fb.Surface.close()
    
    s = raw_input()
