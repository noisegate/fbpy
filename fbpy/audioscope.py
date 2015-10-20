import fbpy.fb as fb
import fbpy.jack as jack
import time
import numpy as np
import threading
from threading import Thread

class Needmain(type):
    """
        Dont instantiate the sprite if 
        there is no main surface.
        Using this stuff in sprite as well
        clean UP 
        TODO: TODO: 

    """
    def __call__(self, *args, **kwargs):
        if fb.Surface.isalive():
            return super(Needmain, self).__call__(*args, **kwargs)
        else:
            raise TypeError("Need main surface")

class Threaded(threading.Thread):
    
    activeThreads = []
    
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func
        self.runme = True
        self.activeThreads.append(func)

    def run(self):
        while self.runme:
            self.func()

    def stop(self):
        self.runme = False
        time.sleep(1)
        self.join()
    
    @classmethod
    def threads(cls):
        for i, t in enumerate(cls.activeThreads):
            print i, t

class Scopemodes(object):
    
    def __init__(self, parentmode):
        self.pm = parentmode
    
    @property
    def scope(self):
        self.pm[0] = 1
        
    @property
    def phase(self):
        self.pm[0] = 2
        

class Scope(object):
    """
        Scope class
        
        Virtual scope, using jack and fb, for visualization of
        audiostream. 
        
        .. code-block:: python
        
           scope = Scope((0,0),(100,100))
           scope.start()
           
           scope.amplitude = 0.1
           scope.offset = 0.3
           
           scope.mode.scope
           
           scope.mode.phase
           
           scope.stop()
        
        .. image:: ./images/scope.png
        
    """    
    __metaclass__ = Needmain  
    
    def __init__(self,(x,y),(w,h)):
        self.surface = fb.Surface((x,y),(w,h))
        self.x_ = x
        self.y_ = y
        self.w_ = w
        self.h_ = h
        self.graticule = None
        self.jacky = jack.Jackaudio()
        self.leftchannel = None
        self.rightchannel = None
        self.updateinterval = 0.05
        self.background()
        self.timeax=None
        self.leftoffset = 0.25
        self.rightoffset = 0.75
        self.leftamplitudo = 0.15
        self.rightamplitudo = 0.15
        self.amplitude_ = 0.15
        self.offset_ = 0.25
        self.mode_ = [1]
        self.mode = Scopemodes(self.mode_)
        self.mode.scope
        self.thread = Threaded(self.loop)
        self.looping = True
        self.stepsize_ = 10
        self.color = self.surface.pixelstyle.color

    @property
    def blur(self):
        return self.surface.pixelstyle.blur
        
    @blur.setter
    def blur(self,x):
        self.surface.pixelstyle.blur = x

    @property
    def stepsize(self):
        """
            skip some points from audio data and connect with
            straight lines. 
            U dont want as many points in your poly as the 
            pixelwidth of the scope. To much CPU load 4
            nothin. Phaseplot wants more data, looks better...
        
        """
        
        return self.stepsize_
        
    @stepsize.setter
    def stepsize(self,s):
        self.stepsize_ = s
        step = 1.0/len(self.jacky.dataL[::self.stepsize_])
        self.timeax=np.arange(0,1-step,step).astype(float)
        
    @property
    def x(self):
        """
            x set or get the upper-left x coordinate of the scope
        """
        return self.x_
        
    @x.setter
    def x(self,x):
        self.x_ = x
        self.surface.winsize = (self.x_, self.y_, self.w_, self.h_)

    @property
    def y(self):
        """
            y set or get the upper-left y coordinate of the scope
        """
        return self.y_
        
    @y.setter
    def y(self,y):
        self.y_ = y
        self.surface.winsize = (self.x_, self.y_, self.w_, self.h_)
    
    @property
    def w(self):
        """
            well, width of the scope in pixels
        """
        return self.w_
        
    @w.setter
    def w(self,w):
        self.w_ = w
        self.surface.winsize = (self.x_, self.y_, self.w_, self.h_)
        self.background()

    @property
    def h(self):
        """
            well, height of the scope in pixels
        """
        return self.h_
        
    @h.setter
    def h(self,h):
        self.h_ = h
        self.surface.winsize = (self.x_, self.y_, self.w_, self.h_)
        self.background()
                
    @property
    def amplitude(self):
        """
            sets the relative amplitude of *both* channels L, R
            0-1
        """
        return self.amplitude_
        
    @amplitude.setter
    def amplitude(self,a):
        self.rightamplitudo = a
        self.leftamplitudo = a
        self.amplitude_ = a
        self.leftamplitudo = a
        self.rightamplitudo = a
        
    @property
    def offset(self):
        """
            sets the relative offset of *both* channels L, R
            w.r.t. middle. One goes up, two goes down
            
            0-1
        """
        return self.offset_
    
    @offset.setter
    def offset(self,o):
        self.offset_ = o
        self.leftoffset = 0.5 - o
        self.rightoffset = 0.5 + o
        
    def background(self): 
        self.surface.pixelstyle.color = fb.Colors.darkgrey
        self.surface.fillrect((0.0,0.0),(1.0,1.0))  
        self.surface.pixelstyle.color = fb.Color(80,80,80,100)   
        self.surface.graticule((0.0,0.0),(1.0,1.0))
        self.graticule = self.surface.get_raw()
        self.surface.pixelstyle.color = fb.Color(100,180,180,100)   
        
    def start(self):        
        
        self.jacky.jackon()
        self.jacky.jackread()
        step = 1.0/len(self.jacky.dataL[::self.stepsize_])
        self.timeax=np.arange(0,1-step,step).astype(float)
        self.thread.start()
    
    def stop(self):
        self.jacky.jackoff()
        self.thread.stop()        
        
    def loop(self):
        self.jacky.jackread()

        self.surface.set_raw(self.graticule)
        if self.mode_[0] == 1:
            left = (self.leftamplitudo*self.jacky.dataL[::self.stepsize_]).astype(float) + self.leftoffset
            right =(self.rightamplitudo*self.jacky.dataR[::self.stepsize_]).astype(float) + self.rightoffset
            self.surface.poly(self.timeax,left)
            self.surface.poly(self.timeax,right)
        if self.mode_[0] == 2:
            left = (self.leftamplitudo*self.jacky.dataL[::self.stepsize_]).astype(float)+ 0.5
            right =(self.rightamplitudo*self.jacky.dataR[::self.stepsize_]).astype(float) + 0.5
            self.surface.poly(right,left)
            
        self.surface.update()
        time.sleep(self.updateinterval)

if __name__ == '__main__':
    scope = Scope((800,10),(200,200))
    scope.start()
    
