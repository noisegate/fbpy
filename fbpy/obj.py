import numpy as np

class Ddd(object):

    def __init__(self, filename, scale):
        self.filename = filename
        self.xcrds = []
        self.ycrds = []
        self.zcrds = []
        self.x=[]
        self.y=[]
        self.z=[]
        self.scale = scale

    def open(self):

        f = open(self.filename,'r')

        lines = f.readlines()
        f.close()
        x=[]
        y=[]
        z=[]
        for i, l in enumerate(lines):
            if 'v ' in l:
                crd =  l.strip('v')
                xyz = crd.split(' ')
                self.xcrds.append(self.scale*float(xyz[1]))
                self.ycrds.append(self.scale*float(xyz[2]))
                self.zcrds.append(self.scale*float(xyz[3]))

        for i, l in enumerate(lines):
            if 'f ' in l:
                poly = l.strip('f')
                indi = poly.split(' ')
                x=[]
                y=[]
                z=[]
                for j, index in enumerate(indi):
                    try:
                        iindex = int(index)
                        x.append(self.xcrds[iindex-1])
                        y.append(self.ycrds[iindex-1])
                        z.append(self.zcrds[iindex-1])

                    except:
                        pass
                x.append(x[0])
                y.append(y[0])
                z.append(z[0])
                self.x.append(np.array(x,dtype=np.int32))
                self.y.append(np.array(y,dtype=np.int32))
                self.z.append(np.array(z,dtype=np.int32))
                
if __name__ == '__main__':

    instance = Ddd('../examples/sphere.obj',1)
    instance.open()
    print instance.x


