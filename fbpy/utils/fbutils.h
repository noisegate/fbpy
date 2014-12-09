#ifndef __FBUTILS_H__
#define __FBUTILS_H__

extern struct Color {
    unsigned char r;
    unsigned char g;
    unsigned char b;
    unsigned char a;
};

extern struct Trafo {
    float m11;
    float m12;
    float m21;
    float m22;
    char unity;
};

extern struct TrafoL {
    double tetax;
    double tetay;
    double tetaz;
    int dx;
    int dy;
    int dz;
    int *order;
    int numtrafos;
};

extern struct Trafo3 {
    double tetax;
    double tetay; 
    double tetaz;
    double ctetax;
    double ctetay;
    double ctetaz;
    double ex;
    double ey;
    double ez;
    double cx;
    double cy;
    double cz;
};

extern int setup(void);
extern int swappage(int i);
extern int setblurrad(int r);
extern int settrafo(struct Trafo *);
extern int settrafo3(struct Trafo3 *);
extern int settrafoL(double, double, double, int, int, int, int *, int);
extern int setwinparams(int x, int y, int width, int height, 
			unsigned char r, unsigned char g, unsigned char b, 
			unsigned char a,
			unsigned char linestyle,
			int blur_, int blurrad, int sigma);
extern int getwinparams(int *x, int *y, int *wi, int *he);
extern int keepcurrent();
extern int clearbuffer(char *buffy);
extern int cleartmpbuffer();
extern int clearscreen();
extern int update(void);
extern int closefb(void);
extern int get_pixel(int x, int y, struct Color* tmpclr, char *buffer);
extern int kernel();
extern int plot(int x, int y);
extern int plot_(int x, int y);
extern int plotalpha_(int x, int y);
extern int plotblurred_(int x, int y);
extern int fillrect(int x0, int y0, int w, int h);
extern int snow();
extern int matrixvec3(double m[9], int *x, int *y, int *z);
extern int rotate(double angle, int *x, int *y, int *z, char direction);
extern int project(int *x, int *y, int *z);
extern int poly(int *x, int *y, int l);
extern int poly3d(int *x, int *y, int *z, int l);
extern int drawpolys(Polys *);
extern int draw3dpolys(Polys *); 
extern int identity(int *, int *, int*);
extern int translateX(int *x, int *y, int *z);
extern int translateY(int *x, int *y, int *z);
extern int translateZ(int *x, int *y, int *z);
extern int rotateX(int *x, int *y, int *z);
extern int rotateY(int *x, int *y, int *z);
extern int rotateZ(int *x, int *y, int *z);
//extern int transform3d(Polys *, struct TrafoL *, int *order, int numt);
extern int memblockcpy(char *sprite, int l, char DIRECTION);
extern int overlay(char *res_buf, char *sprite, int xo, int yo, char sprmode);
extern int get_raw(char *sprite, int l);
extern int set_raw(char *sprite, int l);
extern int line(int x0, int y0, int x1, int y1);
extern int arc(int x0, int y0, int r1, int r2, int startseg, int endseg, int segs);
extern int circle(int x0, int y0, int r1, int segs);
extern int printxy(int x0, int y0, char string[], int size_);
extern int graticule(int x0, int y0, int w, int h);
extern int getHeight();
extern int getWidth();
extern int styledredraw();
extern int helloworld (int x, int y);
extern int read_PNG(char *filename);
extern int write_PNG(char *filename, int interlace, char borfb);
#endif //__FBUTILS_H__
