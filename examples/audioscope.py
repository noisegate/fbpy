#test audio scope
#this is what actualy started the whole thing...
import sys
import threading
import struct
from threading import Thread
import alsaaudio, time, audioop
import curses

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

class Singleton(type):
    __instance = None
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance

class Audio(object):
    __metaclass__ = Singleton
    
    CHANNELS    = 1
    INFORMAT1   = alsaaudio.PCM_FORMAT_FLOAT_LE
    INFORMAT2   = alsaaudio.PCM_FORMAT_S16_LE
    RATE        = 44100
    FRAMESIZE   = 220
    
    def __init__(self):
        mycard = "plug:leftrecord"
        #mycard = "plug:mixin"
        #mycard = "Loopback PCM"
        self.inp = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE,mode=alsaaudio.PCM_NORMAL,card=mycard)
        self.inp.setchannels(self.CHANNELS)
        self.inp.setrate(self.RATE)
        self.inp.setformat(self.INFORMAT2)
        self.inp.setperiodsize(self.FRAMESIZE)
        self.l = 0
        self.data_ = None
        self.new_data =False
        self.dtime = self.FRAMESIZE/self.RATE
        
        self.cards = alsaaudio.cards()
        self.mixers = alsaaudio.mixers()
        #print self.mixers
        self.mixMaster = alsaaudio.Mixer('Master')#check ik in self.mixers
        
        self.thread = Threaded(self.read)
        
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.thread.stop()
        
    def read(self):
        self.l=0
        t0 = time.time()
        while self.l==0:
            self.l, data = self.inp.read()
        time.sleep(self.dtime)
        if self.l==220:
            self.data_ = struct.unpack("h"*self.FRAMESIZE, data)
            self.new_data = True
        else:
            pass
            #print "Some error..."    

    @property    
    def data(self):
        self.new_data = False
        return self.data_
        
    @property
    def volume(self):
        vol = int(self.mixMaster.getvolume()[0])
        return vol

    @volume.setter
    def volume(self, volume):
        self.mixMaster.setvolume(volume,0)

class myScope(object):
    
    def __init__(self, audio, origo, rect):
        self.rect = (0,0,rect[0],rect[1])
        self.scrn = curses.initscr()
        curses.cbreak()
        curses.nodelay(1)
        self.scrn.addstr(0,0,"audio scope = running")
        self.scrn.refresh()
        self.sound = audio
        self.sound.start()
        self.height = rect[1]-origo[1]
        self.vertcenter = self.height/2
        self.width = rect[0]-origo[0]
        self.horizcenter = self.width/2
        self.datalen = Audio.FRAMESIZE
        self.skip = self.datalen/100
        self.N = self.width/100
        self.exitflag = False
        self.thread = Threaded(self.loop)
        self.thread.start()
        
    def exit(self):
        print "stopping sound thread"
        self.sound.stop()
        print "stopping video thread"
        self.thread.stop()
        curses.endwin()
        sys.exit()

    def test(self):
        time.sleep(0.5)
        print "a"

    def loop(self):
        time.sleep(.05)
        key = self.scrn.getch()
        if key!=-1:
            self.scrn.addch(1,0,key)
            self.scrn.refresh()
            if key == curses.KEY_UP:
                self.exitflag = TRUE
        print "no keypress",
        #for event in pygame.event.get():
        #    if event.type==QUIT:
        #        self.exitflag = True
        #    elif event.type==KEYDOWN:
        #        if event.key == K_ESCAPE:
        #            self.exitflag = True
                
        t0 = time.time()
        while not self.sound.new_data:
            if time.time()-t0>1:
                sys.exit()
        data = self.sound.data[::self.skip]
        #self.frbuffer.rect((0,0,0), self.rect)
        #pygame.draw.line(self.frbuffer.screen,(255,0,0),(0,self.vertcenter),(self.width,self.vertcenter),1)
        points = [(i*self.N, self.vertcenter+y/100) for i, y in enumerate(data)]
        #pygame.draw.polygon(self.frbuffer.screen, (1,1,255), points, 1)

if __name__ == "__main__":
    audio = Audio()
    scope = myScope(audio, (0,0),(300,300))
    audio.volume = 30
    print Threaded.threads()
    while not scope.exitflag:
        print "Yeah yeah yeah\n"
        time.sleep(1)
    #time.sleep(10)
    scope.exit()
