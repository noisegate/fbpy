#http://stackoverflow.com/questions/15857818/python-svg-parser
from xml.dom import minidom
import re

class Poly(object):

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []

class Svg2Poly(object):

    def __init__(self, filename, layer):
        self.filename = filename
        self.path_strings = ''
        self.polys = []
        self.layer = layer
        self.fetch()
        self.parse()

    def fetch(self):
        doc = minidom.parse("./test.svg")  # parseString also exists
        self.path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
        doc.unlink()

    def parse(self):
        for i, l in enumerate(self.path_strings):
            print "Item {0}:".format(i)
            self.polys.append(Poly())
            currentpoly = self.polys[-1]
            crds = re.findall("([0-9]+(\.[0-9]+)?|\.[0-9]+),([0-9]+(\.[0-9]+)?|\.[0-9]+)", l)
            for j, m in enumerate(crds):
                print "Coordinate {0}".format(j), 
                currentpoly.x.append(float(m[0]))
                currentpoly.y.append(float(m[2]))
                currentpoly.z.append(float(self.layer))

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
    converter = Svg2Poly("./test.svg",1)
    print converter    


