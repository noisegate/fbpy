# * fb.py main module for pythons fbpy package. Draws stuff in the
# * Linux framebuffer. 
# * Copyright (C) 2014  Marcell Marosvolgyi aka noisegate
# * 
# * This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License
# * as published by the Free Software Foundation; either version 2
# * of the License, or (at your option) any later version.
# * 
# * This program is distributed in the hope that it will be useful,
# *      but WITHOUT ANY WARRANTY; without even the implied warranty of
# *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# *      GNU General Public License for more details.
# * 
# *      You should have received a copy of the GNU General Public License
# *      along with this program; if not, write to the Free Software
# *      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# *      
# version: 0.1
# profanities included 4 xtra power

import fblib
import svg
import numpy as np
from itertools import count
import os.path
import copy

"""
    Some module documentation....

    .. doctest:: 

       >>> print "hw!"
       hw!
    
"""

class Uniton(type):

    """
       The Uniton is a special case of the Vulgion
       and ensures inheritance of certain properties of 
       the primeordial instance for all consecutive instances. 

    """
    #__instance = None
   
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Uniton, self).__init__(*args, **kwargs)
       
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Uniton, cls).__call__(*args, **kwargs)
            cls.__instance._setupfb()
            cls.__instance.origo = (0,0)
            cls.__instance.size = (cls.scr_width, cls.scr_height)
            cls.__instance.pixelstyle = Pixelstyle()
        else:
            cls.__instance = super(Uniton, cls).__call__(*args, **kwargs)
        cls.instances.append(cls.__instance)
        return cls.__instance


class Bounds(object):

    def __init__(self, function):
        self.function = function

    def adjust(self, x, maxi):
        #if float then assume scaled
        #and scale it:
        if (type(x) == float):
            #if x<0 :x=0
            #if x>1 :x=1
            x = x * (maxi-1)
        return x % maxi

    def __call__(self, *args, **kwargs):
        origo = args[0].origo
        size = args[0].size
        pixelstyle = args[0].pixelstyle
        maxx=size[0]
        maxy=size[1]
        #should let the driver know about the winsize
        #args[0].winsize = (origo[0],origo[1],size[0],size[1], args[0].pixelstyle)
        args[0].informdriver()
        new_args = []
        firstarray = True

        for i, X in enumerate(args):
            if isinstance(X, tuple):
                x = self.adjust(X[0],maxx)
                y = self.adjust(X[1],maxy)
                #x = x + origo[0]
                #y = y + origo[1]
                new_args.append((int(x),int(y)))
            elif isinstance(X, np.ndarray):
                X = np.where(X>=0,X,0)
                X = np.where(X<=1,X,1)
                if firstarray:
                    X *= (maxx-1)
                    #X += origo[0]
                    firstarray = False
                else:
                    X *= (maxy-1)
                    #X += origo[1]
                X = X.astype(np.int32)    
                new_args.append(X)
            else:
                new_args.append(X)
            args = tuple(new_args)

        return self.function(*args, **kwargs) 

    def __get__(self, instance, owner):
        def wrapper(*args, **kwargs):
            return self(instance, *args, **kwargs)
        wrapper.__doc__ = self.function.__doc__
        wrapper.__name__ = self.function.__name__
        return wrapper
        
class Color(object):
    def __init__(self, *args):
        if args:
            self.r = args[0]
            self.g = args[1]
            self.b = args[2]
            self.a = args[3]
        else:
            self.r=0
            self.g=0
            self.b=0
            self.a=0

    def __repr__(self):
        return "Red={0}, Green={1}, Blue={2}, Alpha={3}".format(self.r,self.g,self.b,self.a)

    @property
    def red(self):
        return self.r

    @red.setter
    def red(self, red):
        self.r = red

    @property
    def green(self):
        return self.g

    @green.setter
    def green(self, green):
        self.g = green

    @property
    def blue(self):
        return self.b

    @blue.setter
    def blue(self, blue):
        self.b = blue

    @property
    def alpha(self):
        return self.a

    @alpha.setter
    def alpha(self, alpha):
        self.a = alpha

class Pixelstyle(object):

    def __init__(self, *args, **kwargs):
        self.color = Colors.white
        self.style = Styles.solid
        self.blur = 0
        self.blurradius = 1
        self.sigma = 1

class Geom(object):

    def __init__(self, selfy, *args):
        self.args = args
        self.parent = selfy

    def keep(self):
        self.parent.objects.append(self)

    def redraw(self):
        pass

class Rect(Geom):

    def redraw(self):
        self.parent.rect(*args)

class Line(Geom):

    def redraw(self):
        self.parent.line(*args)

class Point(object):

    def redraw(self):
        self.parent.point(*args)

class Coordinate(object):

    def __init__(self,x, y):
        self.x = x
        self.y = y

    def postprocess(self):
        pass    

def docme():
    return "Surface object of the fbpy module."

class Colors(object):
    """
        Some prefab colors, to make life easier.

        Food for Pixelstyle. e.g.: 
        

    """
    #TODO: make immutable !!! else ALL 
    #colrs change throughout FOOL I WAS

    black = Color(0,0,0,0)
    white = Color(255,255,255,0)
    grey = Color(100,100,100,0)
    darkgrey = Color(30,30,30,0)
    green = Color(0,255,0,0)
    darkgreen =  Color(0,100,0,0)
    magenta = Color(0,170,170,0)

class Styles(object):
    solid = 0
    dotted = 2
    dashed = 1

class Pixelstyles(object):
    #shoudl make this immutable
    faint = Pixelstyle()
    faint.blur = 2
    faint.blurradius = 2
    faint.style = Styles.solid
    faint.sigma = 1
    faint.color = Color(60,60,130,100)

    sharp = Pixelstyle()
    sharp.blur =0
    sharp.style = Styles.solid
    sharp.blurradius = 1
    sharp.sigma =1
    sharp.color = Colors.white


class Polys(object):
    """
        Multi poly class. Each surface has an instance
        of these. 
        draw3dpolys method of surface will use it.

    """
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []

    def getthem(self):
        l = len(self.x)
        for i in range(l):
            yield self.x[i], self.y[i], self.z[i]

class Trafo(object):
    """
        Handle two dim lintrafos for
        your surface.

        that is: Stretch and or Rotate

        yih.

        Work-flow.
        
        You start with making an instance:

        .. code-block:: python
           
           T = Trafo()

        Uppon instanciation you get an unity 
        transform by default.
        Then decide what should happen to it.. E.g.
        you want to rotate and then stretch it. 
        Well, you'll define two Operators:

        .. code-block:: python

           R = Trafo()
           S = Trafo()
           R.rotate(0.1)           #where 0.1 is the angle in RAD
           S.stretch(1.05, 1.05)   #ehhhr, 5% in horiz and vert

        Now you can iterate:

        .. code-block:: python

           T *=R
           T *=S

        Each surface has a built in trafo fb.Surface.trafo, which is
        unity or identity by default. The state of this operator is
        passed to the fb driver. 

        Here is a full example:

        .. doctest::

           >>> import fbpy.fb as fb

           >>> main = fb.Surface()

           >>> sub = fb.Surface((100,100),(200,200))

           >>> R = fb.Trafo()

           >>> R.rotate(0.1)

           >>> sub.clear()
           0
           >>> for i in range(10): 
           ...     sub.trafo*=R
           ...     sub.rect((10,10),(190,190))
           0
           0
           0
           0
           0
           0
           0
           0
           0
           0
           >>> sub.grabsilent("./source/images/rotate.png")
           0

        .. image:: ./images/rotate.png

        .. code-block:: python

           sub.trafo.identity() #reset the transform
        

    """

    def __init__(self):
        self.m_11 = 1.0
        self.m_12 = 0.0
        self.m_21 = 0.0
        self.m_22 = 1.0
        self.o_11 = None
        self.o_12 = None
        self.o_21 = None
        self.o_22 = None

        self.store11 = None
        self.store12 = None
        self.store21 = None
        self.store22 = None
        self.unity = 1

    def identity(self):
        self.m_11 = 1.0
        self.m_12 = 0.0
        self.m_21 = 0.0
        self.m_22 = 1.0
        self.unity = 1

    def set(self, a,b,c,d):
        self.m_11 = a
        self.m_12 = b
        self.m_21 = c
        self.m_22 = d
        self.unity = 0

    def rotate(self, angle):
        self.o_11 = np.cos(angle)
        self.o_12 = np.sin(angle)
        self.o_21 = -np.sin(angle)
        self.o_22 = np.cos(angle)
        self.unity = 0
        self.multiply()

    def stretch(self, x, y):
        self.o_11 = x
        self.o_12 = 0.0
        self.o_21 = 0.0
        self.o_22 = y
        self.unity = 0
        self.multiply()

    def multiply(self):
        #multiply self with other
        #self() * self
        self.store11 = self.m_11 * self.o_11 + self.m_12 * self.o_21
        self.store12 = self.m_11 * self.o_12 + self.m_12 * self.o_22
        self.store21 = self.m_21 * self.o_11 + self.m_22 * self.o_21
        self.store22 = self.m_21 * self.o_12 + self.m_22 * self.o_22
        
        self.m_11 = self.store11 
        self.m_12 = self.store12
        self.m_21 = self.store21
        self.m_22 = self.store22

    def __mul__(self, T):
        """
            Be aware, this instantiates a new trafo
            uppon each multiplication. not very memory
            efficient...

        """
        self.o_11 = T.m_11
        self.o_12 = T.m_12
        self.o_21 = T.m_21
        self.o_22 = T.m_22
        res = Trafo()
        res.m_11 = self.m_11 * self.o_11 + self.m_12 * self.o_21
        res.m_12 = self.m_11 * self.o_12 + self.m_12 * self.o_22
        res.m_21 = self.m_21 * self.o_11 + self.m_22 * self.o_21
        res.m_22 = self.m_21 * self.o_12 + self.m_22 * self.o_22
        res.unity = 0
        return res

    def __imul__(self, T):
        self.o_11 = T.m_11
        self.o_12 = T.m_12
        self.o_21 = T.m_21
        self.o_22 = T.m_22
        self.unity = 0
        self.multiply()
        return self

    def __pow__(self, T):
        pass

class Trafo3(object):
    """
        transforms, or cameraviews for 2d projected
        3d objects.

        args:
        teta{x,y,z}  rotaion angles of object around own Origin
        cteta{x,y,z] cam rotation

    """
    def __init__(self,  tetax,tetay,tetaz,
                        ctetax,ctetay,ctetaz,
                        ex,ey,ez,cx,cy,cz):
        self.tetax = tetax
        self.tetay = tetay
        self.tetaz = tetaz
        self.ctetax = ctetax
        self.ctetay = ctetay
        self.ctetaz = ctetaz
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.cx = cx
        self.cy = cy
        self.cz = cz

class DDDObject(object):
    polynr=0
    
    def __init__(self,x,y,z,surf):
        self.polys = Polys()
        self.polys.x = x
        self.polys.y = y
        self.polys.z = z
        self.surface = surf
        self.mynumber = None
        self.order = []
        self.anglex = 0
        self.angley = 0
        self.anglez = 0
        self.tx = 0
        self.ty = 0
        self.tz = 0
        self.init()

    @classmethod
    def increment(cls):
        cls.polynr +=1

    def init(self):
        self.surface.informdriver()
        fblib.fbinit()
        for i in self.polys.getthem():
            fblib.fbaddpoly(i[0],i[1],i[2],self.polynr)

        self.mynumber = self.polynr
        self.increment()
        print self.mynumber

    #def settrafransform(self):
    #    self.surface.informdriver()
    #    fblib.fbtransform3d(self.anglex, self.angley,self.anglez,
    #                        self.tx,self.ty,self.tz,
    #                        np.array(self.order, dtype=np.int32),self.mynumber)

    def draw(self):
        self.surface.informdriver()
        fblib.fbsettrafoL(  self.anglex, self.angley, self.anglez,
                            self.tx, self.ty, self.tz,
                            np.array(self.order, dtype=np.int32),len(self.order))
        fblib.fbdraw3dpolys(self.mynumber)

    @property
    def tetax(self):
        return self.anglex

    @tetax.setter
    def tetax(self, x):
        self.order.append(1)
        self.anglex = x

    @property
    def tetay(self):
        return self.angley

    @tetax.setter
    def tetay(self, y):
        self.order.append(2)
        self.angley = y

    @property
    def tetaz(self):
        return self.anglez

    @tetax.setter
    def tetaz(self, z):
        self.order.append(3)
        self.anglez = z

    @property
    def dx(self):
        return self.tx

    @dx.setter
    def dx(self,tx):
        self.order.append(4)
        self.tx = tx

    @property
    def dy(self):
        return self.ty

    @dy.setter
    def dy(self,ty):
        self.order.append(5)
        self.ty = ty

    @property
    def dz(self):
        return self.tz

    @dz.setter
    def dz(self,tz):
        self.order.append(6)
        self.tz = tz

class Surface(object):
    """
        This is the main class, it generates a drawing surface.

        On first invokation, it will generate a surface which
        encompasses the entire screen automaticaly *and* it
        will open the framebuffer device.
        The *classmethod* close will close it. 
        Subsequent instances will need arguments defining size and
        position.

    """

    __metaclass__ = Uniton

    #__doc__ = docme()
    instances = []
    scr_width = 0
    scr_height = 0

    def __init__(self, *args):
        self.origo = (0,0)
        self.size = None
        self.sprite = None

        self.pixelstyle = Pixelstyle()

        self.trafo = Trafo()
        self.dddtrafo = Trafo3( 0.0,0.0,0.0,
                                0.0,0.0,0.0,
                                0.0,0.0,1.0,
                                1.0,1.0,1.0)

        if len(args)==2:
            if isinstance(args[0], tuple) and isinstance(args[1],tuple):
                self.origo = args[0]
                self.size = args[1]
                self.informdriver()

        self.polys = Polys()
        self.objects = []

    def informdriver(self):
        """
            pass relevant class info to
            fbutils driver,
            this is how one 'instance' of the
            driver can serve multiple Surface
            instances

            .. doctest::

               >>> import fbpy.fb as fb

               >>> main = fb.Surface()

               >>> main.informdriver()
               

        """

        a=fblib.fbsetwinparams( self.origo[0], self.origo[1], self.size[0], self.size[1], 
                                self.pixelstyle.color.r,
                                self.pixelstyle.color.g,
                                self.pixelstyle.color.b,
                                self.pixelstyle.color.a,
                                self.pixelstyle.style,
                                self.pixelstyle.blur, self.pixelstyle.blurradius, 
                                self.pixelstyle.sigma)

        b=fblib.fbsettrafo( self.trafo.m_11, self.trafo.m_12, 
                            self.trafo.m_21, self.trafo.m_22, 
                            self.trafo.unity)

        fblib.fbsettrafo3(  self.dddtrafo.tetax, self.dddtrafo.tetay,self.dddtrafo.tetaz,
                            self.dddtrafo.ctetax, self.dddtrafo.ctetay,self.dddtrafo.ctetaz,
                            self.dddtrafo.ex,self.dddtrafo.ey,self.dddtrafo.ez,
                            self.dddtrafo.cx,self.dddtrafo.cy,self.dddtrafo.cz)

        window = fblib.fbgetwinparams()

        origos = (window[0] == self.origo[0]) and (window[1] == self.origo[1])
        sizes = (window[2] == self.size[0]) and (window[3] == self.size[1])

        if origos and sizes: return 0
        else: return -1

    @classmethod
    def _setupfb(cls):
        fblib.fbsetup()
        cls.scr_width = fblib.fbgetWidth()
        cls.scr_height = fblib.fbgetHeight()

    @property
    def focus(self):
        return -1

    @focus.setter
    def focus(self, r):
        self.blurradius = r
        fblib.fbfocus(r)

    @property
    def winsize(self):
       return (self.origo,self.size)

    @winsize.setter
    def winsize(self, X):
        x0 = X[0]
        y0 = X[1]
        w = X[2]
        h = X[3]
        self.origo = (x0,y0)
        self.size = (w,h)
        self.informdriver()

    def _set_color_(self, color):
        fblib.fbsetcolor(color.r,color.g,color.b,color.a)

    def _set_color2_(self, color):
         fblib.fbsetcolor2(color.r,color.g,color.b,color.a)

    def _set_style_(self, style_):
        fblib.fbsetstyle(style_)

    def set_dotstyle(self, dotstyle, blurrad_):
        """
            set_dotstyle(<dotstlyle>, <blur radius>)

            dotstyle 0 : fast plot
            dotstyle 1 : plot with soft alpha
            dotstyle 2 : plot with blur + soft alpha

            blur radius: well, 2 sigma ^2 it is

        """
        self.blur = dotstyle
        self.blurradius = blurrad_
        self.informdriver()

    def __repr__(self):

        message = """
                      framebuffer surface object:\n
                      origin X:{0}\n
                      origin Y:{1}\n
                      width   :{2}\n
                      height  :{3}\n
                  """

        return message.format(self.origo[0], self.origo[1], self.size[0], self.size[1])

    def clear(self):
        """
            will clear the temp buffer
        """
        self.informdriver() 
        return fblib.fbclearbuffer()

    def clearframebuffer(self):
        """
            will clear the framebuffer
            but not the temp buffer.
            Use clearscreen for a clear screen,
            or clear to clear the temp buffer
        """
        self.informdriver()
        fblib.fbclearscreen()
        return 0

    def clearscreen(self):
        """
            will clear the screen,
            that is, swap buffer + actual frameb
        """
        self.informdriver()
        fblib.fbclearbuffer()
        fblib.fbclearscreen()
        return 0

    def styledredraw(self):
        self.informdriver()
        return fblib.fbstyledredraw()

    def update(self):
        """
            update()
            draws the buffered geometries. So, you need this before you actualy see 
            anything

        """
        self.informdriver()
        return fblib.fbupdate()

    def keepbackground(self):
        self.informdriver()
        return fblib.fbkeepcurrent()

    def store(self):
        self.sprite = self.get_raw()
        return 0

    def restore(self):
        self.set_raw(self.sprite)
        return 0

    def overlay(self, res_buf, sprite, oldx, oldy, mode):
        self.informdriver()
        #length = self.size[0]*self.size[1]*4
        #res_buf = np.zeros(length, dtype=np.int8)
        return fblib.fboverlay(res_buf, sprite, oldx, oldy, mode)
        
    def get_raw(self):
        """
            get_raw()

            returns an raw bitmap array of the current window, use
            set_raw to put the bitmap back.

            .. code-block:: python

               sprite = main.get_raw()
               main.set_raw(sprite)

        """

        self.informdriver()
        length = self.size[0]*self.size[1]*4
        sprite = np.zeros(length, dtype=np.int8)

        fblib.fbgetraw(sprite)
        return sprite

    def set_raw(self, sprite):
        """
            set_raw(sprite)

            puts the bitmap array into the buffer, see get_raw.
        """
        self.informdriver()
        fblib.fbsetraw(sprite)

    def swap(self, page):
        fblib.fbswap(page)

    def fill(self,color):
        self._set_color_(color) 
        fblib.fbclearscreen()

    @Bounds
    def poly(self, xdata, ydata):
        """
            poly(<xdata numpy array>, <ydata numpy array>)

            x, y will be the points, have to be the same length and type

            style = 0, 1, 2
            0: solid line
            1: dashed line
            2: dotted line

            .. doctest::

               >>> import fbpy.fb as fb

               >>> import numpy as np

               >>> x = np.arange(0, 1,0.01)

               >>> y = 0.5*np.sin(x*2*2*np.pi) + 0.5

               >>> main  = fb.Surface()

               >>> subwin = fb.Surface((0,0),(200,200))
               
               >>> subwin.clear()
               0
               >>> subwin.pixelstyle = fb.Pixelstyles.faint

               >>> subwin.poly(x, y)
               0
               >>> subwin.grabsilent("./source/images/poly.png")
               0

            .. image:: ./images/poly.png

    
        """

        if  isinstance(xdata, np.ndarray) and isinstance(ydata, np.ndarray):
            if xdata.dtype == np.int32 and ydata.dtype == np.int32:
                pass
            else:
                raise NameError("something wrong with the array")
        else:
            xdata = np.array(xdata, dtype=np.int32)
            ydata = np.array(ydata, dtype=np.int32)

        if len(xdata) == len(ydata):
            fblib.fbpoly(xdata, ydata)
        else:
            raise NameError("SIZE MISSSMATCH")
        
        return 0



    @Bounds    
    def addpoly(self, x, y, z):
        """
            just a test for the moment
            I have to store this in this
            instance...
            and then on draw3dpolys should I
            call the drivers addpoly!!!

            addpoly(<x array>,<y array>, )
               
        """        

        if isinstance(x,np.ndarray) and isinstance(y, np.ndarray) and isinstance(z,np.ndarray):
            x1 = x
            y1 = y
            z1 = z
        else:
            x1 = np.array(x, dtype=np.int32)
            y1 = np.array(y, dtype=np.int32)
            z1 = np.array(z, dtype=np.int32)
        return fblib.fbaddpoly(x1,y1,z1)
        #self.polys.x.append(x1)
        #self.polys.y.append(y1)
        #self.polys.z.append(z1)
        return 0

    def drawpolys(self):
        """
            Draw a bunch of polygons

            .. doctest::
               
               >>> import fbpy.fb as fb

               >>> import numpy as np

               >>> main  = fb.Surface()

               >>> main.clear()

               >>> sub = fb.Surface((100,100),(200,200))

               >>> sub.clear()
               0
               >>> x1 = np.arange(0,1,0.02)

               >>> y1 = 0.5*np.sin(x1*2*np.pi)+0.5

               >>> z1 = np.zeros(np.size(x1))

               >>> x2 = np.arange(0,1,0.02)

               >>> y2 = 0.5*np.cos(x2*2*np.pi)+0.5

               >>> z2 = np.zeros(np.size(x2))

               >>> sub.addpoly(x1,y1,z1)
               0
               >>> sub.addpoly(x2,y2,z2)
               0
               >>> sub.drawpolys()
               0
               >>> sub.trafo.rotate(np.pi/2)
               0
               >>> sub.drawpolys()
               0
               >>> sub.grabsilent("./source/images/polys.png")
               0

            .. image:: ./images/polys.png



        """
        self.informdriver()
        return fblib.fbdrawpolys()

    def draw3dpolys(self, resend, polynr):
        self.informdriver()
        #now I can upload the polys to the driver:
        if resend==1:
            #fblib.fbfreepolys()
            fblib.fbinit()#set visit=0 
            for i in self.polys.getthem():
                fblib.fbaddpoly(i[0],i[1],i[2],polynr)
        fblib.fbdraw3dpolys(polynr)

    def lintrafo(self,tx,ty,tz,dx,dy,dz,order,polynr):
        self.informdriver()
        return fblib.fbtransform3d(tx,ty,tz,dx,dy,dz,
                                    np.array(order,dtype=np.int32),polynr)

    def dumppolys(self):
        """
            print informationa about the currently loaded 
            multipoly struct.

        """
        fblib.fbprintapoly()

    def freepolys(self):
        fblib.fbfreepolys()

    @Bounds
    def line(self,X1, X2):
        """
            line(<tuple crd from>,<tuple crd to>)

            or

        """
        
        fblib.fbline(X1[0], X1[1], X2[0], X2[1])
        return 0

    @Bounds
    def arc(self, X1, R1, R2, startseg, endseg, segs):
        """
            arc(<tuple>, <radius 1>, <radius 2>, <start seg>, <end seg>, <no seg>)

            couple of examples here:

            .. doctest::

               >>> import fbpy.fb as fb
               
               >>> main = fb.Surface()

               >>> sub = fb.Surface((0,0), (200,200))

               >>> sub.clear()
               0
               >>> sub.pixelstyle = fb.Pixelstyles.faint

               >>> sub.arc((100,100), 60, 90, 0, 50, 100)
               0
               >>> sub.pixelstyle = fb.Pixelstyles.sharp

               >>> sub.arc((100,100), 40, 40, 30, 90, 100)
               0
               >>> sub.grabsilent("./source/images/arc.png")
               0
              
            .. image:: ./images/arc.png

        """

        if type(R1) == float:
            rx=self.size[0] * R1/2
        else:
            rx = R1
        if type(R2) == float:
            ry=self.size[1] * R2/2
        else:
            ry = R2
            
        fblib.fbarc(X1[0], X1[1], rx, ry, startseg, endseg, segs)  
        return 0

    @Bounds
    def circle(self, X1, R1, segs):
        """
            circle(<tuple>,<radius>, <segments>)

            Will draw a ...

            .. doctest::

               >>> import fbpy.fb as fb
               
               >>> main = fb.Surface()

               >>> sub = fb.Surface((0,0), (200,200))

               >>> sub.clear()
               0
               >>> sub.circle((100,100),0.5, 100)
               0
               >>> sub.grabsilent("./source/images/circle.png")
               0
              
            .. image:: ./images/circle.png


        """
        fblib.fbarc(X1[0],X1[1],R1*self.size[0],R1*self.size[1],0,segs,segs) 
        return 0

    @Bounds
    def rect(self, X1, X2):
        """
            rect(<tuple>, <tuple>, <fb color>, <style>)
            
            Will draw a rectangle @ first tuple, width and height
            as in second tuple


        """

        fblib.fbline(X1[0],X1[1],X2[0],X1[1])
        fblib.fbline(X1[0],X1[1],X1[0],X2[1])
        fblib.fbline(X1[0],X2[1],X2[0],X2[1])
        fblib.fbline(X2[0],X1[1],X2[0],X2[1])
        #return Rect(self, X1, X2, color)
        return 0

    @Bounds
    def printxy(self, X1, string, size_):
        """
            printxy (<tuple>, <string>, <size>)
            
            Will print text in string at position defined by tuple (x, y).

            Size can be 1 or 2, where 2 prints triple sized LCD-like format
            
            returns 0

            .. doctest::

               >>> import fbpy.fb as fb
               
               >>> main = fb.Surface()

               >>> sub = fb.Surface((0,0),(800,100))

               >>> sub.clear()
               0
               >>> sub.printxy((10,10),"Hello world!", 2)
               0 
               >>> sub.printxy((10,38),"or a bit smaller...", 1)
               0
               >>> sub.pixelstyle.color = fb.Color(20,20,20,100)

               >>> sub.pixelstyle.blur = 2

               >>> sub.pixelstyle.blurradius = 4

               >>> sub.pixelstyle.sigma = 1

               >>> sub.printxy((10,76),"where R them goggles...", 1)
               0
               >>> sub.grabsilent("./source/images/printxy.png")
               0               

            .. image:: ./images/printxy.png


        """

        fblib.fbprint(X1[0],X1[1], string, size_)
        return 0

    @Bounds
    def graticule(self, X1, WH):
        """
            graticule(<tuple>,<tuple>, <fb.color>, <fb.color>)

            draws scope-like graticule @ first tuple of size second tuple
            (width/height). color = subs, color2 main

            returns 0

            .. doctest::

               >>> import fbpy.fb as fb

               >>> main  = fb.Surface()

               >>> sub2 = fb.Surface((0,0),(200,200))

               >>> sub2.clear() == 0
               True
               >>> sub2.pixelstyle.color = fb.Color(200,200,200,00) 
                 
               >>> sub2.fillrect((0,0),(200,200)) == 0
               True
               >>> sub2.pixelstyle.color = fb.Colors.white

               >>> sub2.graticule((0.0,0.0),(1.0,1.0)) == 0
               True
               >>> sub2.grabsilent("./source/images/graticule.png") == 0
               True

            .. image:: ./images/graticule.png

        """
        
        fblib.fbgraticule(X1[0],X1[1],WH[0]-X1[0],WH[1]-X1[1])
        return 0

    @Bounds
    def fillrect(self, X1, WH):
        fblib.fbfillrect(X1[0],X1[1],WH[0],WH[1])
        return 0

    def snow(self):
        """
            snow()

            show some noise...

            .. doctest::

               >>> import fbpy.fb as fb

               >>> main = fb.Surface()

               >>> sub = fb.Surface((0,0),(200,200))

               >>> sub.clear()
               0
               >>> sub.pixelstyle = fb.Pixelstyles.faint

               >>> sub.snow()
               0
               >>> sub.grabsilent("./source/images/snow.png")
               0
               
            .. image:: ./images/snow.png


        """

        self.informdriver()
        fblib.fbsnow()
        return 0

    @Bounds
    def point(self, X1):
        fblib.fbplot(X1[0],X1[1])
        #return Point(self, X1, color)

    def add(self, x):
        if isinstance(x, Line): print "Adding line"
        self.objects.append(x)      

    def blit(self, filename):
        """
            blit(<filename>)

            will put the PNG <filename> in the current surface

            .. doctest::

               >>> import fbpy.fb as fb

               >>> main = fb.Surface()

               >>> sub = fb.Surface((100,100),(600,600))

               >>> sub.blit("../examples/cylon.png")
               0
               >>> sub.grabsilent("./source/images/gottherobot.png")
               0
            
            .. image:: ./images/gottherobot.png

        """
        self.informdriver()
        return fblib.fbblit(filename)

    def grab(self,filename):
        """
            grab(<filename>)

            grabs current frame into file <filename>.png
        """
        self.informdriver()
        return fblib.fbgrab(filename)

    def grabsilent(self, filename):
        """
            grabsilent(<filename>)

            grabs current buffer into file <filename>.png

            so, if you dont use update, you'll never actually 
            *see* the drawing. Handy for doctest stuff 
            of other apps where you *only* wanna make 
            pics..
        """
        self.informdriver()
        return fblib.fbgrabsilent(filename)

    def grabsequence(self, filename):
        """
            grabsequence(<filename>)

            grabs current frame into file with filename <filename#>

            where # is an automatich counter. the output will be e.g.:
            screenshot0001.png, screenshot0002.png, ...

            you can use e.g. 
            
            .. code-block:: console

               nerd@wonka: ~/tmp$ avconv -i <filename>%04d.png -c:v huffyuv <yourmoviename>.avi  

            to convert the sequence to a movie.
            You can also use ofcourse somehtin like
            
            .. code-block:: console

               nerd@wonka: ~/tmp$ avconv -f fbdev -r 10 -i /dev/fb0 -c:v huffyuv /dev/shm/movi.avi 2> /dev/null 
            
        """

        numbered_filename = ("{}{:04d}.png".format(filename, i) for i in count(1))

        try_this = next(numbered_filename)

        while os.path.isfile(try_this):
            try_this = next(numbered_filename)

        self.grab(try_this)

        return 0

    def redraw(self):
        for i, elem in enumerate(self.objects):
            elem.redraw()

    def something(self):
        """
            .. doctest::

               >>> print "Hello from a doctest.."
               Hello from a doctest..

        """

    def icopyu(self, othersurf):
        self.origo = copy.deepcopy(othersurf.origo)
        self.size = copy.deepcopy(othersurf.size)
        self.pixelstyle = copy.deepcopy(othersurf.pixelstyle)
        self.trafo = copy.deepcopy(othersurf.trafo)
        self.informdriver()
        self.sprite = othersurf.get_raw()


    @classmethod
    def isalive(self):
        if self._Uniton__instance == None: return False
        else: return True

    @classmethod
    def close(self):
        
        self._Uniton__instance = None

        fblib.fbclose()
        return 0

if __name__ == '__main__':
    pass

