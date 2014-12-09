import fbpy.audioscope as audioscope
import fbpy.fb as fb

if __name__ == '__main__':
    main  = fb.Surface()
    scope = audioscope.Scope((800,10),(350,350))
    scope.start()
    
