# * sprite.py module for pythons fbpy package. Draws sprites without 
# * using hw blitterzz
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
# profanities included 4 xtra powerimport fbpy.fb as fb

import fbpy.fb as fb
import copy
import numpy as np
import time

class Needmain(type):
    """
        Dont instantiate the sprite if 
        there is no main surface.


    """
    def __call__(self, *args, **kwargs):
        if fb.Surface.isalive():
            return super(Needmain, self).__call__(*args, **kwargs)
        else:
            raise TypeError("Need main surface")

class Sprite(object):
    """
        A drawing surface, which can be moved around
        without destructing the background.
    
        Full example:

        .. doctest::
           >>> import fbpy.fb

           >>> import fbpy.sprite



    """

    __metaclass__ = Needmain

    def __init__(self, (x,y),(w,h)):
        
        self.surface = fb.Surface((x,y),(w,h))
        self.backgr = fb.Surface((x,y),(w,h))
        self.newstamp = None
        self.spritedata = []
        self.oldR = (x,y)
        self.R = (x,y)
        self.backgr.keepbackground()
        self.oldstamp = self.backgr.get_raw()
        #self.oldstamp = np.zeros(w*h*4,dtype=np.int8)


    def moveto(self, R, sprite_no):
        """
            move to new position using
            FTL drive
            it jumps. for smooth moves, fast
            a low level iface will be implemented

            moveto(<tuple>, sprite_nr)
        """

        self.R = R

        self.surface.origo = self.R
        res = self.surface.overlay(self.oldstamp,self.spritedata[sprite_no], self.oldR[0], self.oldR[1], 1)
        
        if res == 0 : self.oldR = self.R

    def save(self):
        """
            save current surface to list
        """
        self.spritedata.append(self.surface.get_raw())

    def hide(self):
        """
            hide this sprite

        """
        self.surface.overlay(self.oldstamp,self.spritedata[0], self.oldR[0],self.oldR[1], 0)

    @property
    def x(self):
        return self.surface.origo[0]

    @x.setter
    def x(self,x):
        temp = self.surface.origo
        temp = (x, temp[0])
        
    @property
    def y(self):
        return self.surface.origo[1]

    @y.setter
    def y(self,y):
        temp = self.surface.origo
        temp = (y, temp[1])

    def redraw(self):
        pass

if __name__ == '__main__':
    main = fb.Surface()

    sprite = Sprite((10,10),(100,100))
    sprite.surface.clear()
    sprite.surface.line((0,0),(100,100))
    sprite.moveto(20,20)

    fb.Surface.close()

