import fbpy.fb as fb

#In this example I show the abilty of surface
#gemoetries to accept scaled coordinates and
#absolute coordinates, or a combination.



if __name__ == "__main__":
    main = fb.Surface()

    #make a subwindow
    window = fb.Surface((400,400),(200,200))

    #show it
    window.clear()
    window.rect((0.0, 0.0),(1.0,1.0), fb.Colors.white, fb.Styles.solid)
    window.update()

    #now we want to draw an inner rect precicely 
    #two pixels away from the outer. 
    #scaled coordinates are not so convenient for 
    #this purpose...
    window.rect((2,2),(197,197), fb.Colors.white, fb.Styles.solid)
    window.update()
    
    #using integers will tell the Surface object 
    #we want to use pixel coordinates
    #floats will invoke the automatic scaler...

    s = raw_input("hit enter to close")

    fb.Surface.close()
