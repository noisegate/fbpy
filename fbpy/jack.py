#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2014 marcell <marcell@nano>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
import fblib
import numpy as np

class Jackaudio(object):
    
    def __init__(self):
        audio = np.zeros(1024)
        self.dataL = np.array(audio, dtype=np.float64)
        self.dataR = np.array(audio, dtype=np.float64)
        
    def jackon(self):
        r=fblib.fbjackon()
        if r==-1:
            print "SORRY: only one instance allowed at the moment"
            print "Hey, this is pre-alpha..."
            return -1

    def jackoff(self):
        fblib.fbjackoff()

    def jackread(self):
        fblib.fbreadjack(self.dataL, self.dataR)

    @property
    def channels(self):
        self.jackread()
        return (self.dataL, self.dataR)

if __name__ == '__main__':
	pass
