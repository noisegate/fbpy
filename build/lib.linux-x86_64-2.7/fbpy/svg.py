# * svg.py module for pythons fbpy package. Very basic svg support.
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
# http://stackoverflow.com/questions/15857818/python-svg-parser

from xml.dom import minidom
import re
import numpy as np
import time

REGFLOAT ="" 

class Poly(object):
    """
        Helper object to store polys data.

    """
    def __init__(self):
        self.x_ = []
        self.y_ = []
        self.z_ = []

    def appendx(self,x):
        self.x_.append(x)

    def appendy(self,y):
        self.y_.append(y)

    def appendz(self,z):
        self.z_.append(z)

    @property
    def x(self):
        #return np.array(self.x_, np.int32)    
        return self.x_
    @property
    def y(self):
        #return np.array(self.y_, np.int32)
        return self.y_
    @property
    def z(self):
        #return np.array(self.z_, np.int32)
        return self.z_

class Text(object):

    """
        Will return svg text and an object as handle

        Text(<tuple Ox,Oy>, <string>, <size>, <surface>)

        .. doctest::

           import fbpy.fb as fb
           import fbpy.svg as svg

           main = fb.Surface()
           win = fb.Surface((0,0),(800,100))

           mytext = svg.Text((0,0),"TESTING THIS STUFF",1.5, win)
        
           win.grabsilent("./source/images/svgtext.png")

           fb.Surface.close()

        .. image:: ./images/svgtext.png

    """

    def __init__(self, O, text, sze, surf):
        self.text = text.upper()
        self.surf = surf
        self.Ox = O[0]
        self.Oy = O[1]
        self.factor = sze/20.0
        self.printtext()

    def printtext(self):
        cursor =0
        for i,kar in enumerate(self.text):
            #print "loading {0}\n".format(kar)
            cursor +=1
            if kar == " ":
                pass
            else:
                polies = Svg2Poly("../font/{0}.svg".format(ord(kar)),1)
                for j, p in polies.get_poly():
                    for k,n in enumerate(p.x):
                        p.x[k] = p.x[k]*self.factor + (cursor*self.factor*200) + self.Ox
                        p.y[k] = p.y[k]*self.factor + self.Oy
                        
                    self.surf.addpoly(p.x,p.y,p.z)
                self.surf.drawpolys()
                time.sleep(0.1)
                self.surf.update()
                self.surf.freepolys()
        #self.surf.update()

class Svg2Poly(object):
    """
        very basic svg to poly converter

        Svg2Poly(<filename, str>, <layer, int>)

        returns object with get_poly method, which is 
        a enumerated list generator.


    """

    def __init__(self, filename, layer):
        self.filename = filename
        self.path_strings = ''
        self.polys = []
        self.layer = layer
        self.fetch()
        self.parse()

    def fetch(self):
        doc = minidom.parse(self.filename)  # parseString also exists
        self.path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
        doc.unlink()

    def parse(self):
        norm = 1.0
        x_pen = 0.0
        y_pen = 0.0

        for i, l in enumerate(self.path_strings):
            self.polys.append(Poly())
            currentpoly = self.polys[-1]
 
            resM = re.search(r"M( ([-+]?[0-9]+(\.[0-9]+)?|\.[0-9]+),([-+]?[0-9]+(\.[0-9]+)?|\.[0-9]+)){1,}",l)
            resm = re.search(r"m( ([-+]?[0-9]+(\.[0-9]+)?|\.[0-9]+),([-+]?[[0-9]+(\.[0-9]+)?|\.[0-9]+)){1,}",l)
            resl = re.search(r"l( ([-+]?[0-9]+(\.[0-9]+)?|\.[0-9]+),([-+]?[[0-9]+(\.[0-9]+)?|\.[0-9]+)){1,}",l)
            
            if resM:
                mvabsto = resM.group().split()
                for j, el in enumerate(mvabsto[1::]):
                    m = el.split(',')
                    #print m
                    x_pen =float(m[0])/norm
                    y_pen =float(m[1])/norm
                    if j==0:
                        #print "start"
                        x_start = x_pen
                        y_start = y_pen
                    currentpoly.appendx(x_pen)
                    currentpoly.appendy(y_pen)
                    currentpoly.appendz(float(self.layer))
                    #print x_pen, y_peni
                if re.search(r".* z", l):
                    #print "close"
                    currentpoly.appendx(x_start)
                    currentpoly.appendy(y_start)
                    currentpoly.appendz(float(self.layer)) 
            if resm:
                mvrelto = resm.group().split()
                x_pen = 0.0
                y_pen = 0.0
                for j,el in enumerate(mvrelto[1::]):
                    m = el.split(',')
                    x_pen += float(m[0])
                    y_pen += float(m[1])
                    if j==0:
                        #print "start"
                        x_start = x_pen
                        y_start = y_pen

                    currentpoly.appendx(x_pen/norm)
                    currentpoly.appendy(y_pen/norm)
                    currentpoly.appendz(float(self.layer))
        
                if re.search(r".* z", l):
                    #print "close"
                    currentpoly.appendx(x_start)
                    currentpoly.appendy(y_start)
                    currentpoly.appendz(float(self.layer)) 

            if resl:
                #print "found line"
                lnto = resl.group().split()
                for j, el in enumerate(lnto[1::]):
                    m = el.split(',')
                    x_pen += float(m[0])
                    y_pen += float(m[1])
                    currentpoly.appendx(float(x_pen/norm))
                    currentpoly.appendy(float(y_pen/norm))
                    currentpoly.appendz(float(self.layer))
                

    def get_poly(self):
        for i, p in enumerate(self.polys):
            yield i, p

    def report(self):
        s=""
        s+="svg poly container object\n"
        s+="file {0}\n".format(self.filename)
        s+="number of polys {0}\n".format(len(self.polys))
        return s 

    def __repr__(self):
        return self.report()

    def __str__(self):
        return self.report()

if __name__ == '__main__':
    converter = Svg2Poly("../examples/test.svg",1)
    print converter   
    """
    for i, poly in converter.get_poly():
        print "Poly {0}\n".format(i)
        print poly.x
        print poly.y

    """
