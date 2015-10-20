# * fblib.pyx cython wrapper for fbutils.c in pythons fbpy package. 
# * fbutils has some framebuffer drawing functions that need speed.
# *
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

cimport cython
#from libc.stdlib cimport malloc, free
from libc.stdlib cimport *
from libc.stdio cimport fopen, FILE, stdout
import numpy as np
cimport numpy as np
ctypedef np.int32_t DTYPE_t
ctypedef np.int8_t DTYPE_char
import time

"""
    Some docu here please...


"""

#https://github.com/cython/cython/wiki/tutorials-numpy

np.import_array()

cdef extern from "test.h":
    struct _Polys:
        int **x
        int **y
        int **z
        int *polyl
        int polyc
    ctypedef _Polys Polys

    cdef FILE *debug
    char dbgrdr #debug redirection
    int visits
    int addpoly(Polys *, int x[], int y[], int z[], int lenxy)
    int setpms(int dbgrdr_, int visits_)
    int delpolys(Polys *)

cdef extern from "audio.h":
    
    int mainz()
    void kwit()
    int getnframes()
    int readout(double *, double *)

cdef extern from "fbutils.h":
    struct Color:
        unsigned char r
        unsigned char g
        unsigned char b
        unsigned char a

    struct Trafo:
        float m11
        float m12
        float m21
        float m22
        char unity

    struct TrafoL:
        double tetax
        double tetay
        double tetaz
        int dx
        int dy
        int dz
        int *order
        int numtrafos

    struct Trafo3:
        double tetax
        double tetay
        double tetaz
        double ctetax
        double ctetay
        double ctetaz
        double ex
        double ey
        double ez
        double cx
        double cy
        double cz

    int (*pPlot) (int x, int y)

    int setup()
    int swappage(int i)
    int setblurrad(int r)
    int setwinparams(   int x, int y, int width, int height, 
                        unsigned char r, unsigned char g, unsigned b, unsigned a,
                        unsigned char linestyle,
                        int blur_, int blurrad, int sigma)
    int getwinparams(   int *x, int *y, int *wi, int *he)
    int settrafo(Trafo *mytrafo)
    int settrafo3(Trafo3 *)
    int settrafoL(double, double, double, int, int, int, int*, int)
    int keepcurrent()
    int clearbuffer(char *buffy)
    int cleartmpbuffer()
    int clearscreen()
    int styledredraw()
    int update()
    int closefb()
    int get_pixel(int x, int y, Color *, char *bufferd)
    int kernel()
    int plot(int x, int y)
    int plot_(int x, int y)
    int plotalpha_(int x, int y)
    int plotblurred(int x, int y)
    int fillrect(int x0, int y0, int w, int h)
    int snow()
    int line(int x0, int y0, int x1, int y1)
    int arc(int x0, int y0, int r1, int r2, int startseg, int stopseg, int segs)
    int poly(int *x, int *y, int length)
    int drawpolys(Polys *)
    int draw3dpolys(Polys *)
    #int transform3d(Polys *, TrafoL *, int *order, int numt) 
    int overlay(char *res_buf, char *sprite, int oldx, int oldy, char mode)
    int get_raw(char *sprite, int l)
    int set_raw(char *sprite, int l)
    int printxy(int x0, int y0, char *string, int size_)
    int graticule(int x0, int y0, int w, int h)
    int getHeight()
    int getWidth()
    int helloworld(int x, int y )
    int read_PNG(char *filename)
    int write_PNG(char *filename, int interlace, char borfb)

cdef Color mycolor

cdef Color mycolor2

cdef Trafo mytrafo

cdef TrafoL mytrafoL

cdef Trafo3 mytrafo3

#cdef Polys apoly

cdef Polys *morepolys = <Polys *>malloc (10*sizeof(Polys))

class Style(object):
    style=0

def fbswap(int i):
    return swappage(i)

def fbpoly(np.ndarray[DTYPE_t, ndim=1] x, np.ndarray[DTYPE_t, ndim=1] y):
    length = x.shape[0]
    if y.shape[0] == length:
        return poly(<int *>x.data, <int *>y.data, length)
    else:
        return -1

def fboverlay(  np.ndarray[DTYPE_char, ndim=1] res_buf,
                np.ndarray[DTYPE_char, ndim=1] sprite,
                oldx, oldy, mode):
    return overlay(<char *> res_buf.data, <char *>sprite.data, oldx, oldy, <char>mode)

def fbgetraw(np.ndarray[DTYPE_char, ndim=1] sprite):
    length = sprite.shape[0]
    return get_raw(<char *>sprite.data, length)

def fbsetraw(np.ndarray[DTYPE_char, ndim=1] sprite):
    length = sprite.shape[0]
    return set_raw(<char *>sprite.data, length)

def fbfillrect(int x0, int y0, int w, int h):
    return fillrect(x0, y0, w, h)

def fbsnow():
    return snow()

def fbarc(int x, int y, int r1, int r2, int startseg, int stopseg, int segs):
    return arc(x, y, r1, r2, startseg, stopseg, segs)

def fbsetwinparams( int x, int y, int width, int height, 
                    unsigned char r, unsigned char g, unsigned char b, unsigned char a, 
                    unsigned char linestyle,
                    int blur, int blurrad, int sigma):
    """
        what about comments...
        fbsetwinparams( <x origin>, <y origin>, <width>, <height>,
                        r, g, b, a,
                        <blur>, <blur radius>, <sigma>)

    """
    return setwinparams(x, y, width, height, 
                        r, g, b, a, 
                        linestyle, blur, blurrad, sigma)

def fbgetwinparams():
    cdef int x, y, wi, he
    getwinparams(&x, &y, &wi, &he)
    return [x, y, wi, he]

def fbfocus(int r):
    return setblurrad(r)

def fbkeepcurrent():
    return keepcurrent()

def fbsetstyle(int style_):
    Style.style = style_

def fbsetup():
    fbinit()
    return setup()

def fbclearbuffer():
    return cleartmpbuffer()

def fbclearscreen():
    return clearscreen()
    
def fbclose():
    return closefb()
    
def fbplot(int x, int y):
    return plot(x,y)

def fbline(int x0, int y0, int x1, int y1):
    return line(x0, y0, x1, y1)

def fbgraticule(int x0, int y0, int w, int h):
    return graticule(x0, y0, w, h)

def fbprint(int x0, int y0, pystring, int size_):
    cdef char *string = pystring
    return printxy(x0, y0, string, size_)

def fbgetWidth():
    return getWidth()

def fbgetHeight():
    return getHeight()

def fbupdate():
    return update()

def fbblit(filename):
    """
        puts a png into the framebuffer
    """
    return read_PNG(filename)

def fbgrab(filename):
    """
        grabs the actual framebuffer
    """
    return write_PNG(filename, 0, 0)

def fbgrabsilent(filename):
    """
        grabs the temp buffer, so it is silent
        do it before update() and you will never
        see the result. good for doctests shit
    """
    return write_PNG(filename, 0, 1)

def fbsettrafo(float m11, float m12,  float m21, float m22, int unity):
    mytrafo.m11 = m11
    mytrafo.m12 = m12
    mytrafo.m21 = m21
    mytrafo.m22 = m22
    mytrafo.unity = <char>unity

    return settrafo(&mytrafo)

def fbsettrafo3(    tetax, tetay, tetaz,
                    ctetax, ctetay, ctetaz,
                    ex, ey, ez,
                    cx, cy, cz):
    mytrafo3.tetax = tetax
    mytrafo3.tetay = tetay
    mytrafo3.tetaz = tetaz
    mytrafo3.ctetax = ctetax
    mytrafo3.ctetay = ctetay
    mytrafo3.ctetaz = ctetaz
    mytrafo3.ex = ex
    mytrafo3.ey = ey
    mytrafo3.ez = ez
    mytrafo3.cx = cx
    mytrafo3.cy = cy
    mytrafo3.cz = cz
    settrafo3(&mytrafo3)
    return 0

def fbsettrafoL(  tetax, tetay, tetaz,
                    dx, dy, dz,
                    np.ndarray[DTYPE_t,ndim=1] order,
                    int numtrafos):
    #mytrafoL.tetax = tetax
    #mytrafoL.tetay = tetay
    #mytrafoL.tetaz = tetaz
    #mytrafoL.dx = dx
    #mytrafoL.dy = dy
    #mytrafoL.dz = dz
    #mytrafoL.order = <int *>malloc(numtrafos*sizeof(int))
    #mytrafoL.order = <int *>order.data
    #mytrafoL.numtrafos = numtrafos
    return settrafoL(tetax, tetay, tetaz, dx,dy,dz,<int *>order.data,numtrafos )

def fbaddpoly(np.ndarray[DTYPE_t, ndim=1] x, 
              np.ndarray[DTYPE_t, ndim=1] y,
              np.ndarray[DTYPE_t, ndim=1] z, polynr):
    length = x.shape[0]
    return addpoly(&morepolys[polynr], <int *>x.data, <int *>y.data, <int *>z.data,<int>length)

def fbprintapoly():
    for i in range(morepolys[0].polyc):
        for j in range(morepolys[0].polyl[i]):
            print "{0} {1} {2}".format(morepolys[0].x[i][j],
                                       morepolys[0].y[i][j],
                                       morepolys[0].z[i][j])

def fbdrawpolys(polynr):
    return drawpolys(&morepolys[polynr])

def fbdraw3dpolys(polynr):
    return draw3dpolys(&morepolys[polynr])

def fbfreepolys():
    return delpolys(morepolys)

def wrapper(int x, int y):
    return helloworld(x, y)

def fbstyledredraw():
    return styledredraw()

def fbinit():
    #inits the poly memalocator
    #and fixes the debug file
    print "surpress debug info"
    #somehow this seems to be tricky...
    #debug = fopen("/dev/shm/log.log","w")
    #set dbgrdr = 0 and visits=0
    setpms(1,0)
    #time.sleep(5)
    return 

def fbjackon():
    #this will become the audio interface
    #stuff...
    print "starting up jack audio engine..."
    r=mainz()
    if r==-1:
        print "only one instance etc..."
        return -1
    return 0
    
def fbjackoff():
    #stopping mainz
    print "killing jack routine"
    kwit()
    return 0

def fbgetnframes():
    return getnframes()
        
def fbreadjack( np.ndarray[np.float64_t, ndim=1] audioL,
                 np.ndarray[np.float64_t, ndim=1] audioR):
    #naming is improving
    #get audio data
    
    #cdef np.ndarray[np.float64_t, ndim=1] audio = np.zeros(1024)
    readout(<double *>audioL.data, <double *>audioR.data)
    #print audio
    return 0
