// vim: tabstop=4:shiftwidth=4:expandtab 
/*
 * fbutils helper library for pythons fbpy module. Draws stuff in the
 * Linux framebuffer.
 * Copyright (C) 2014  Marcell Marosvolgyi aka noisegate
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 *      but WITHOUT ANY WARRANTY; without even the implied warranty of
 *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *      GNU General Public License for more details.
 * 
 *      You should have received a copy of the GNU General Public License
 *      along with this program; if not, write to the Free Software
 *      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *      
 */

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <math.h>
#include "font.h"
#include <png.h>
#include "test.h"
#include "audio.h"
#include "fbutils.h"
#include <time.h>

//TODO: I really have to clean this
//shit. It's getting way too GLOBAL

#ifndef FB_VBLANK_HAVE_STICKY
#define FB_VBLANK_HAVE_STICKY 0
#endif

#ifndef FB_VBLANK_STICKY
#define FB_VBLANK_STICKY 0
#endif

#ifdef FBIOGET_VBLANK
static int vblank_flags;                  /* supports retrace detection? */
#endif

#define TO_BLOCK 1
#define FROM_BLOCK 0

#define FBUTILS_ERROR_OUT_OF_MEMORY -2
#define FBUTILS_ERROR_GENERAL -3
#define FBUTILS_ERROR_NOT_YET_IMPLEMENTED -1

#define max255(x) (((x)>255)?255:(x))
#define MAXBLUR 10
#define MAXBLURHALF 5

#define TON start=clock()
#define TOFF end=clock();printf("elapsed %1d.",(double)(end-start))

#define BPP 4                           //well, bytes per pixel

#define xaxis 0
#define yaxis 9
#define zaxis 18

#define png_infopp_NULL (png_infopp)NULL
#define int_p_NULL (int*)NULL

int fbfd = 0;
struct fb_var_screeninfo orig_vinfo;
struct fb_var_screeninfo vinfo;
struct fb_fix_screeninfo finfo;
long int screensize = 0;
char *fbp = NULL;
char *tmp_buf = NULL;
char *dummy_buf = NULL;
char skipper;				//for linestyle, global 4 continuity
int blur;				    //makes plot dots blurred
int blurrad;                //gauss width or somethin'
int sigma;                  //sigma of the Gaussian
char linestyle;             //0 = solid, 1=dash, 2=dot
int bytes_per_pixel = 0;
int Ox;
int Oy;
int width;
int width4;
int height;
int cur_page = 1;
unsigned char kern[MAXBLUR][MAXBLUR];
clock_t end,start;
struct Color *currentcolor = NULL;
struct Trafo *currenttrafo = NULL;
struct Trafo3 *currenttrafo3 = NULL;
struct TrafoL *currenttrafoL = NULL;
int (*pPlot) (int x, int y);
int (*lintrafo[7])(int *, int *, int *)={NULL};

char gauzz[]={
		0x10,0x10,0x10,0x10, 0x20,0x20,0x20,0x20, 0x10,0x10,0x10,0x10,
		0x20,0x20,0x20,0x20, 0xff,0xff,0xff,0xff, 0x20,0x20,0x20,0x20,
		0x10,0x10,0x10,0x10, 0x20,0x20,0x20,0x20, 0x10,0x10,0x10,0x10};
        
int setup(void)
{
    //http://stackoverflow.com/questions/4996777/paint-pixels-to-screen-via-linux-framebuffer
    //modified

    fbfd = open("/dev/fb0", O_RDWR);
    if (!fbfd) {
        fprintf(stderr, "Error: cannot open framebuffer device.\n");
        return FBUTILS_ERROR_GENERAL;
    }
    //printf("The framebuffer device was opened successfully.\n");

    if (ioctl(fbfd, FBIOGET_VSCREENINFO, &vinfo)) {
      fprintf(stderr, "Error reading variable information.\n");
      return FBUTILS_ERROR_GENERAL;
    }
    //printf("Original %dx%d, %dbpp\n", vinfo.xres, vinfo.yres, 
	//   vinfo.bits_per_pixel );

    // Store for reset (copy vinfo to vinfo_orig)
    // should not be here, but/??
    // maybe before update??? trying...
    // memcpy(&orig_vinfo, &vinfo, sizeof(struct fb_var_screeninfo));

    // Change variable info
    vinfo.bits_per_pixel = 32;
    //vinfo.xres = 1366;
    //vinfo.yres = 768;
    vinfo.xres_virtual = vinfo.xres;
    vinfo.yres_virtual = vinfo.yres * 1; // double the physical

    if (ioctl(fbfd, FBIOPUT_VSCREENINFO, &vinfo)) {
      fprintf(stderr, "Error setting variable information.\n");
      return -1;
    }
    bytes_per_pixel = vinfo.bits_per_pixel / 4;
    // Get fixed screen information
    if (ioctl(fbfd, FBIOGET_FSCREENINFO, &finfo)) {
      fprintf(stderr, "Error reading fixed information.\n");
      return -1;
    }

    // map fb to user mem 
    // TODO:
    //finfo line_length gives 5504
    //5504/4 = 1376 not 1366 hmmm
    //
    //added 4 here!!! 'cos bits per pixel is 32 not 8
    //screensize = 4*vinfo.xres * vinfo.yres;
    //doubling this because of the flipping
    //use virtual is already twice the physical
    //screensize = 4 * vinfo.xres_virtual * vinfo.yres_virtual;
    //screensize = finfo.line_length * vinfo.yres_virtual;
    //screensize = BPP * vinfo.xres * vinfo.yres;
    screensize = finfo.line_length * vinfo.yres;
    fbp = (char*)mmap(0, 
		screensize, 
		PROT_READ | PROT_WRITE, 
		MAP_SHARED, 
		fbfd, 
		0);
    Ox = 0;
    Oy = 0;
    width = vinfo.xres;
    width4 = vinfo.xres * BPP;//yih
    height = vinfo.yres;

    //printf ("screensize %i \n", screensize);
    //printf ("screensize %i \n", finfo.smem_len);


    //allocate temp memory stuff....
    //
    tmp_buf = malloc((size_t)screensize);
    if (tmp_buf == NULL){
		fprintf(stderr, "Out of memory...\n");
		return FBUTILS_ERROR_OUT_OF_MEMORY;
    }

    dummy_buf = malloc((size_t)screensize);
    if (dummy_buf == NULL){
		fprintf(stderr, "Out of memory...\n");
		return FBUTILS_ERROR_OUT_OF_MEMORY;
    }

    memcpy(tmp_buf, fbp, screensize);
    memcpy(dummy_buf, fbp, screensize);
    //memset(tmp_buf, (int)0, screensize+1);
    //printf("screensize %i\n", screensize);
    //printf("size of tmp buf: %i \n", sizeof(tmp_buf));
    //use the fast plotroutine by default.
    //
    pPlot = plot_;

    currentcolor = malloc(sizeof(struct Color));
    currenttrafo = malloc(sizeof(struct Trafo));
    currenttrafo3= malloc(sizeof(struct Trafo3));
    currenttrafoL= malloc(sizeof(struct TrafoL));
    currenttrafoL->order = malloc(sizeof(int));
    kernel();
    printf("yres = %i", vinfo.yres);fflush(stdout);
    return 0;
}

int swappage(int i) 
{
	return -1;
}

int keepcurrent()
{
	memcpy(tmp_buf, fbp, screensize);
	return 0;
}

int setblurrad(int r)
{
    blurrad = r;
}

int settrafo (struct Trafo *mytrafo)
{
    currenttrafo->m11 = mytrafo->m11;
    currenttrafo->m12 = mytrafo->m12;
    currenttrafo->m21 = mytrafo->m21;
    currenttrafo->m22 = mytrafo->m22;
    currenttrafo->unity = mytrafo->unity;
    return 0;
}

int settrafo3 (struct Trafo3 *mytrafo)
{
    currenttrafo3->tetax = mytrafo->tetax;
    currenttrafo3->tetay = mytrafo->tetay;
    currenttrafo3->tetaz = mytrafo->tetaz;
    currenttrafo3->ctetax = mytrafo->ctetax;
    currenttrafo3->ctetay = mytrafo->ctetay;
    currenttrafo3->ctetaz = mytrafo->ctetaz;
    currenttrafo3->ex = mytrafo->ex;
    currenttrafo3->ey = mytrafo->ey;
    currenttrafo3->ez = mytrafo->ez;
    currenttrafo3->cx = mytrafo->cx;
    currenttrafo3->cy = mytrafo->cy;
    currenttrafo3->cz = mytrafo->cz;
    return 0;
}

int settrafoL ( double tetax, double tetay, double tetaz,
                int dx, int dy, int dz, 
                int *order, int numtrafos)
{
    int i;
    
    currenttrafoL->tetax = tetax;
    currenttrafoL->tetay = tetay;
    currenttrafoL->tetaz = tetaz;
    currenttrafoL->dx = dx;
    currenttrafoL->dy = dy;
    currenttrafoL->dz = dz;
    int *tmp = (int *)realloc(currenttrafoL->order, numtrafos*sizeof(int));
    currenttrafoL->order = tmp;
    //this is kinda braindamaged, TODO:
    for (i=0;i<numtrafos;i++){
        *(currenttrafoL->order+i) = *(order+i);
    }
    currenttrafoL->numtrafos = numtrafos;
    return 0;
}

int setwinparams(   int x, int y, int width_, int height_, 
                    unsigned char r, unsigned char g, unsigned char b,
                    unsigned char a,
                    unsigned char linestyle_, 
                    int blur_, int blurrad_, int sigma_)
{
    //this function should really be invoked
    //each time a fb method is called
    //maybe move color and style here too
    //TODO: here we need a struct, soooooo
    //many args are UGLY
    Ox = x;
    Oy = y;
    width = width_;
    width4 = width*BPP;
    height = height_;

    currentcolor->r = r;
    currentcolor->g = g;
    currentcolor->b = b;
    currentcolor->a = a;

    linestyle = linestyle_;

    if (blur_ == 0) pPlot = plot_;
    if (blur_ == 1) pPlot = plotalpha_;
    if (blur_ == 2) pPlot = plotblurred_;
    blurrad = blurrad_>5?5:blurrad_;        //decided to put this here anywayzzzz
    sigma = sigma_; 
    kernel();    
    return 0;
}

int getwinparams(int *x, int *y, int *wi, int *he)
{
    *x = Ox;
    *y = Oy;
    *wi = width;
    *he = height;
    return 0;
}

int checkbounds()
{
	int y=0;
	int offset;

	do {
		offset = Ox*BPP + ((Oy+y) * finfo.line_length);
		y++;
	}while((offset<=(screensize-(width4)))&&(y<=height));
	y--;
	//printf("y = %i \n",y);
	return (y);
}

int clearbuffer(char *buffy)
{
    /*
     * utility function
     * either clear buffer
     * or framebuffer
     */

	int c = 0;
	int y;
	int pix_offset = 0;
	int maxheight;
	maxheight = checkbounds();

	for (y=0; y < maxheight; y++){
        pix_offset = (0+Ox*BPP) + ((Oy+y) * finfo.line_length);
        memset(buffy+pix_offset, c, finfo.line_length);
    }
    //update();
    return 0;
}

int cleartmpbuffer()
{
    clearbuffer(tmp_buf);
    return 0;
}

int clearscreen() 
{
    clearbuffer(fbp);
    return 0;
}

int closefb(void)
{
    //memcpy(fbp, dummy_buf, screensize);
    munmap(fbp, screensize);
    //free(fbp);
    fbp=NULL;
    free(currentcolor);
    currentcolor = NULL;
    free(currenttrafo);
    currenttrafo = NULL;
    free(currenttrafo3);
    currenttrafo3 = NULL;
    free(currenttrafoL);
    currenttrafoL = NULL; 
    free(tmp_buf);
    tmp_buf = NULL;
    //if (ioctl(fbfd, FBIOPUT_VSCREENINFO, &orig_vinfo)) {
    //    fprintf(stderr, "Error re-setting variable information.\n");
    //}
    free(dummy_buf);
    dummy_buf = NULL;
    close(fbfd);
    return 0;
}

int kernel()
{
    int i, j;
    float r2;

    for (i=0; i<MAXBLUR; i++){
        for (j=0;j<MAXBLUR;j++){
            r2 = ((i-MAXBLURHALF)*(i-MAXBLURHALF) + (j-MAXBLURHALF)*(j-MAXBLURHALF)+0.02);
            kern[i][j] = (unsigned char)(255.0*expf(-r2/blurrad/sigma));
        }
    }
    return 0;
}

int plotalpha_(int x, int y)
{
    unsigned int pix_offset;
    float opacity;
    float faintb, faintg, faintr, fainta;
    float r,g,b, a;

    //x = Ox + (x % width);
    //y = Oy + (y % height);

    if (x>width) return -1;
    if (x<0) return -1;
    if (y>height) return -1;
    if (y<0) return -1;

    x+=Ox;
    y+=Oy;

    pix_offset = BPP*x + y * finfo.line_length;
   
    if (pix_offset<0) return -1;
    if (pix_offset>screensize) return -1;

    opacity = (float)(1.0 - ((unsigned char)currentcolor->a)/255.0);

    b = (float)(*((unsigned char*)(tmp_buf + pix_offset)));
    g = (float)(*((unsigned char*)(tmp_buf + pix_offset+1)));
    r = (float)(*((unsigned char*)(tmp_buf + pix_offset+2)));

    faintb = (float)((opacity * currentcolor->b) + b);
    faintr = (float)((opacity * currentcolor->r) + r);
    faintg = (float)((opacity * currentcolor->g) + g);

    fainta = (float)(255.0 - ((255-*((unsigned char *)(tmp_buf + pix_offset + 3))) + (255-currentcolor->a)));

    if (fainta<0) fainta = 0;

    // what we want 
    // 0 = opacity., 255 = opaq
    // old + new
    // but we have
    // 0 = opaq, 255 = opacity
    // 255 - ((255-old) + (255-new))
    // 255 - (510 -old -new) = -250 + old + new
    //

    if (faintb>255) faintb = (float)255;
    if (faintr>255) faintr = (float)255;
    if (faintg>255) faintg = (float)255;

    *((char*)(tmp_buf + pix_offset))  = (unsigned char)faintb;
    *((char*)(tmp_buf + pix_offset+1)) =  (unsigned char)faintg;
    *((char*)(tmp_buf + pix_offset+2)) = (unsigned char)faintr;
    *((char*)(tmp_buf + pix_offset+3)) = (unsigned char)fainta;
    return 0;
}

int plotblurred_(int x, int y)
{
    struct Color tmpcol;
    int i, j;
    float fucktor;           //r squared, yih
    int r_max = blurrad;
    int startx, starty, endx, endy;

    tmpcol.r = currentcolor->r;
    tmpcol.g = currentcolor->g;
    tmpcol.b = currentcolor->b;
    tmpcol.a = currentcolor->a;

    startx = (x-r_max)<0?0:x-r_max;
    endx = (x+r_max)>(Ox+width)?(Ox+width):x+r_max+1;
    starty = (y-r_max)<0?0:y-r_max;
    endy = (y+r_max)>(Oy+height)?(Oy+height):y+r_max+1;

    fucktor = (1.0-(tmpcol.a/255.0)); 

    //kernel();

    for (i=startx; i<endx;i++){
        for (j=starty; j<endy;j++){
            // if the exp =0 a should be 255
            // if exp =1 a below 255 but not 0
            //
            // 1 - (1-a)gauss
            currentcolor->a =(unsigned char)(255.0 - fucktor * kern[i-x+MAXBLURHALF][j-y+MAXBLURHALF]);
            plotalpha_(i, j);
        }
    }

    currentcolor->a = tmpcol.a;
    currentcolor->r = tmpcol.r;
    currentcolor->g = tmpcol.g;
    currentcolor->b = tmpcol.b;

    return 0;
}

int get_pixel(int x, int y, struct Color *color,  char *buffer)
{
    unsigned int pix_offset;

    x = Ox + (x % width);
    y = Oy + (y % height);

    pix_offset = BPP*x + y * finfo.line_length;

    color->b = *((char *)(buffer + pix_offset));
    color->g = *((char *)(buffer + pix_offset+1));
    color->r = *((char *)(buffer + pix_offset+2));
    color->a = *((char *)(buffer + pix_offset+3));
        
    return 0;
}

int plot_(int x, int y)
{
    //this is gonna be the fast implementation.
    unsigned int pix_offset;

    x = Ox + (x % width);
    y = Oy + (y % height);

    pix_offset = BPP*x + y * finfo.line_length;
    
    *((char*)(tmp_buf + pix_offset)) = currentcolor->b;
    *((char*)(tmp_buf + pix_offset+1)) = currentcolor->g;
    *((char*)(tmp_buf + pix_offset+2)) = currentcolor->r;
    *((char*)(tmp_buf + pix_offset+3)) = currentcolor->a;
    return 0;
}

int plot(int x, int y)
{
    pPlot(x, y);
    return 0;
}

int fillrect(int x0, int y0, int w, int h) 
{
	int x;
	int y;

	for (x=0;x<w;x++)
		for(y=0;y<h;y++)
			pPlot(x0+x, y0+y);

	return 0;
}

int snow() 
{
	//http://stackoverflow.com/questions/2572366/how-to-use-dev-random-or-urandom-in-c
	//int surfsize =0;
	//int pix_offset;
	//int sub_offset;	
	//int y;
	//char *snow_buf;
	//FILE *fp;

    tvsnow();
    return 0;
    /*
	surfsize = height * width4;

	snow_buf = malloc((size_t)surfsize);

	fp = fopen("/dev/urandom", "r");
	fread(snow_buf, 1, surfsize, fp);
	fclose(fp);
	for (y=0; y<height;y++){
		pix_offset = (0+Ox*4) + ((Oy+y)*finfo.line_length);
		sub_offset = y*width4;
		memcpy(tmp_buf+pix_offset, snow_buf+sub_offset, width4);
	}
	free(snow_buf);
	snow_buf=NULL;
	return 0;
    */
}

int tvsnow()
{
    int surfsize=0;
    int x, y;
    unsigned char *snow_buf=NULL;
    struct Color tmpcol;
    FILE *fp;
    surfsize=height*width4;
    snow_buf = malloc((size_t)surfsize);

    fp = fopen("/dev/urandom", "r");
	fread(snow_buf, 1, surfsize, fp);
	fclose(fp);

    tmpcol.r = currentcolor->r;
    tmpcol.g = currentcolor->g;
    tmpcol.b = currentcolor->b;
    tmpcol.a = currentcolor->a;

    for (x=2; x<(width);x+=5){
        for (y=2;y< (height);y+=5){
            currentcolor->r = *((unsigned char*)(snow_buf+BPP*x+(y*width4)));
            currentcolor->g = *((unsigned char*)(snow_buf+BPP*x+(y*width4)+1));
            currentcolor->b = *((unsigned char*)(snow_buf+BPP*x+(y*width4)+2));
            currentcolor->a = (unsigned char)0;//*((char*)(snow_buf+BPP*x+(y*width4)));
            
            plotblurred_(x+Ox, y+Oy);
        }
    }
    free(snow_buf);
    snow_buf=NULL;

    currentcolor->a = tmpcol.a;
    currentcolor->r = tmpcol.r;
    currentcolor->g = tmpcol.g;
    currentcolor->b = tmpcol.b;

    return 0;
}

int waitforvsync(void)
{

/* fb_vsync:
 *  Waits for a retrace.
 *  straight from fbcon.c //cellom
 */
    unsigned int prev;

    #ifdef FBIOGET_VBLANK

    struct fb_vblank vblank;

    if (vblank_flags & FB_VBLANK_HAVE_STICKY) {
       /* it's really good if sticky bits are available */
       if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
      return -3;

       do { 
		if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
			break;
       } while (!(vblank.flags & FB_VBLANK_STICKY));
   }
   else if (vblank_flags & FB_VBLANK_HAVE_VCOUNT) {
      /* we can read the exact scanline position, which avoids skipping */
      if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
     return -3;

      do {
     prev = vblank.vcount;
     if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
        break;
      } while (vblank.vcount >= prev);
   }
   else if (vblank_flags & FB_VBLANK_HAVE_VBLANK) {
      /* boring, normal style poll operation */
      do {
     if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
        break;
      } while (vblank.flags & FB_VBLANK_VBLANKING);

      do {
     if (ioctl(fbfd, FBIOGET_VBLANK, &vblank) != 0)
        break;
      } while (!(vblank.flags & FB_VBLANK_VBLANKING));
   }
   else {}//no need for swearing printf("No SUPPORT for vsync shit, you FUCK\nAARHGGGHH!!!!");

 #endif

   /* bodged implementation for when the framebuffer doesn't support it */
   /* We must not to run this loop while returning from a VT switch as timer
    * "interrupts" will not be running at that time so retrace_count will
    * remain constant.
    
   if (_timer_installed && !in_fb_restore) {
      prev = retrace_count;

      do {
      } while (retrace_count == (int)prev);
   }*/
      return 0;
}    

int styledredraw()
{
    /*
     * this function redraws the canvas using 
     * the plot function, thus applying
     * pixelstyle
     */
    int x;
    int y;
    int xr;
    int yr;

    struct Color tempcolor;

    //store buffer in temp mem  
    memcpy(dummy_buf, tmp_buf, screensize); 
  
    tempcolor.r = currentcolor->r;
    tempcolor.g = currentcolor->g;
    tempcolor.b = currentcolor->b;
    tempcolor.a = currentcolor->a;
  
    //redraw buffer form temp mem
    //first clear it

    clearbuffer(tmp_buf);

    for (x=0; x<width;x++){
        for (y=0;y<height;y++){
            get_pixel(x, y, currentcolor, dummy_buf); 
            currentcolor->a = tempcolor.a; 
            xr = x;
            yr = y;  
            if ((currentcolor->r!=0) || (currentcolor->g!=0) || (currentcolor->b!=0)){
            //aint gonna tranform nonvisible pixels pixels. cmon.
                transform(&xr, &yr);
                if ((xr>0) && (xr<width)){
                    if ((yr>0)&&(yr<height)){
                        pPlot(xr,yr);
                    }
                }
            }
        }
    } 
    
    currentcolor->a = tempcolor.a;
    currentcolor->r = tempcolor.r;
    currentcolor->g = tempcolor.g;
    currentcolor->b = tempcolor.b;
    
    return 0;
}

int update(void)
{
    int y;
    int pix_offset = 0;
    int maxheight;
    maxheight = checkbounds();
    for (y=0; y < maxheight; y++){
        pix_offset = (0+Ox*BPP) + ((Oy+y) * finfo.line_length);
	    waitforvsync();
        memcpy(fbp+pix_offset, tmp_buf+pix_offset, width4);
    }
    return 0;
}

int poly(int *x, int *y, int l) 
{
    int i;
    l-=1;
    for (i=0; i<l; i++){
	    line(x[i],y[i],x[i+1],y[i+1]);
    }
    return 0;
}

int matrixvec3(double m[9], int *x, int *y, int *z)
{
    double xl,yl,zl;

    xl = (double)(m[0]* *x + m[1]* *y + m[2]* *z);
    yl = (double)(m[3]* *x + m[4]* *y + m[5]* *z);
    zl = (double)(m[6]* *x + m[7]* *y + m[8]* *z);
    
    *x = (int)xl;
    *y = (int)yl;
    *z = (int)zl;
    return 0;
}

int rotate(double angle, int *x, int *y, int *z, char axis)
{
    /*
     * positioning values in rotation matrix
     * value    Z   Y   X
     * ------------------
     * cos      0   0   4
     * cos      4   8   8
     * sin      3   2   7
     * -sin     1   6   5   
     * 1        8   4   0
     * 0        2   1   1
     * 0        5   3   2
     * 0        6   5   3
     * 0        7   7   6
     */ 

    double m[9];
    double C,S,nS;
    static R[27]={4,8,7,5,0,1,2,3,6,
                  0,8,2,6,4,1,3,5,7,
                  0,4,3,1,8,2,5,6,7};
    C = cos(-angle);
    S = sin(-angle);
    nS= -S;

    *(m+*(R+0+axis)) = C;
    *(m+*(R+1+axis)) = C;
    *(m+*(R+2+axis)) = S;
    *(m+*(R+3+axis)) = nS;
    *(m+*(R+4+axis)) = 1.0;
    *(m+*(R+5+axis)) = 0.0;
    *(m+*(R+6+axis)) = 0.0;
    *(m+*(R+7+axis)) = 0.0;
    *(m+*(R+8+axis)) = 0.0;

    matrixvec3(m, x, y, z);    

    return 0;
}

int project(int *x, int *y, int *z)
{
    double bx,by;

    if (    
            (currenttrafo3->tetaz==0.0) &&
            (currenttrafo3->tetay==0.0) &&
            (currenttrafo3->tetax==0.0) ){
        goto Translate;
    }
    else{
        rotate(currenttrafo3->tetaz,x, y, z,zaxis);
        rotate(currenttrafo3->tetay,x, y, z,yaxis);
        rotate(currenttrafo3->tetax,x, y, z,xaxis);
    }
Translate:
    *x -= (int)currenttrafo3->cx;
    *y -= (int)currenttrafo3->cy;
    *z -= (int)currenttrafo3->cz;
    if (
            (currenttrafo3->ctetaz==0.0) &&
            (currenttrafo3->ctetay==0.0) &&
            (currenttrafo3->ctetax==0.0) ){
        goto projection;
    }
    else{
        rotate(currenttrafo3->ctetaz,x, y, z,zaxis);
        rotate(currenttrafo3->ctetay,x, y, z,yaxis);
        rotate(currenttrafo3->ctetax,x, y, z,xaxis);
    }
projection:    
    if ((*z>-1)) return -1;
    bx = (double)(currenttrafo3->ez/ *z * *x - currenttrafo3->ex);
    by = (double)(currenttrafo3->ez/ *z * *y - currenttrafo3->ey);

    if (bx<0) return -1;
    if (bx>width) return -1;
    if (by<0) return -1;
    if (by>height) return -1;

    *x = (int)bx;
    *y = (int)by;
    return 0;
}

int poly3d( int *x, int *y, int *z, int l)
{
    /*
     * TODO:
     * I am going to pass by ref
     * and the project decides whether
     * to mess up or not...
     * you might wanna have a 'state'
     * gott think this over...
     */

    int i,k;
    int xi,yi,zi;   //local copies for messup
    int xf,yf,zf;

    lintrafo[0] = identity;
    lintrafo[1] = rotateX;
    lintrafo[2] = rotateY;
    lintrafo[3] = rotateZ;
    lintrafo[4] = translateX;
    lintrafo[5] = translateY;
    lintrafo[6] = translateZ;

    l-=1;
    for (i=0; i<l; i++){
        xi=x[i];
        yi=y[i];
        zi=z[i];
        xf=x[i+1];
        yf=y[i+1];
        zf=z[i+1];
        for (k=0;k<currenttrafoL->numtrafos;k++){
            lintrafo[*(currenttrafoL->order+k)](&xi,&yi,&zi);
            lintrafo[*(currenttrafoL->order+k)](&xf,&yf,&zf);
        }
        if (!project(&xi,&yi,&zi))
            if (!project(&xf,&yf,&zf))
                line(xi,yi,xf,yf);
    }

    return 0;
}

int drawpolys(Polys *p)
{
    int i;
    int l;

    for (i=0; i<p->polyc;i++){
        l = *(p->polyl+i);
        poly(*(p->x+i), *(p->y+i), l);
    }

    return 0;
}

int draw3dpolys(Polys *p)
{
    int i;
    int l;

    for (i=0;i<p->polyc;i++){
        l=*(p->polyl+i);
        poly3d(*(p->x+i),*(p->y+i),*(p->z+i),l);
    }
    return 0;
}

int rotateX(int *x, int *y, int *z)
{
    rotate(currenttrafoL->tetax, x, y, z,xaxis);
    return 0;
}

int rotateY(int *x, int *y, int *z)
{
    rotate(currenttrafoL->tetay, x, y, z,yaxis);
    return 0;
}

int rotateZ(int *x, int *y, int *z)
{
    rotate(currenttrafoL->tetaz, x, y, z,zaxis);
    return 0;
}

int identity(int *x, int *y, int *z)
{
    return 0;
}

int translateX(int *x, int *y, int *z)
{
    *x += currenttrafoL->dx;
    return 0;
}
int translateY(int *x, int *y, int *z)
{
    *y += currenttrafoL->dy;
    return 0;
}
int translateZ(int *x, int *y, int *z)
{
    *z += currenttrafoL->dz;
    return 0;
}
/*
int seltrafo(   Polys *p, struct TrafoL *trpms, 
                int (*lintrafo[]) (int *, int*, int *, struct TrafoL *),
                int *order, int numtrafo)
{
    int i, j, k, l;
    int *x;
    int *y;
    int *z;

    for (i=0;i<p->polyc;i++){
        l=*(p->polyl+i);
        for (j=0;j<l;j++){
            x = (*(p->x+i)+j);
            y = (*(p->y+i)+j);
            z = (*(p->z+i)+j);
            for (k=0;k<numtrafo;k++)
                lintrafo[*(order+k)](x, y, z, trpms);
        }
    }
    return 0;
}

int transform3d(Polys *p, struct TrafoL *trpms, int *order,int numtrafo)
{   
    lintrafo[0] = identity;
    lintrafo[1] = rotateX;
    lintrafo[2] = rotateY;
    lintrafo[3] = rotateZ;
    lintrafo[4] = translateX;
    lintrafo[5] = translateY;
    lintrafo[6] = translateZ;
    seltrafo(p, trpms, lintrafo, order, numtrafo);
    return 0;
}
*/

int memblockcpy(char *to_buffer, int l, char DIRECTION)
{ 
	//this is a helper function
	//will probably put in separate
	//lib function, with optimized
	//compiler settings?
	//NOT YET FINNISHED!!!!!!!!!!
	int y;
	int pix_offset;
	int sub_offset;
	//sub_offset = y * width * BPP
	//and cannot exceed l
	//l = y * width * BPP => y_max = l / (width * BPP)
	//because of tmp_buff on the other hand, y_max cannot
	//exceed height
	
	y = l / width4;
	if (y>height) y=height;

	//guess this covers it for the moment.

	if (DIRECTION == TO_BLOCK){
		while(y--){
			pix_offset = (Ox*BPP) + ((Oy+y)*finfo.line_length);
			sub_offset = y*width4;
			memcpy(to_buffer+sub_offset, tmp_buf+pix_offset, width4);
		}	
	}

	if (DIRECTION == FROM_BLOCK){
		while(y--){
			pix_offset = (Ox*BPP) + ((Oy+y)*finfo.line_length);
			sub_offset = y*width4;
			memcpy(tmp_buf+pix_offset, to_buffer+sub_offset, width4);
		}	
	}
	
	return 0;

}

int get_raw(char *sprite_buf, int l)
{
	memblockcpy(sprite_buf, l, TO_BLOCK);
	return 0;
}

int set_raw(char *sprite_buf, int l)
{
	memblockcpy(sprite_buf, l, FROM_BLOCK);
	return 0;
}

int transform(int *x, int *y)
{
    //here we do some linalg. it is soooo
    //simple: no gsl or thelike used
    //TODO:
    //apply petit 1998 stuff

    float tmpx, tmpy,X, Y;
    float centerX, centerY;

    //come on, wont go through the trouble
    //if it is a unity transform really
    //mayB some otha trick in the future
    //TODO:
    if (currenttrafo->unity) return 0;

    //for the moment we assume rotation around
    //the center of the surface.
    centerX = width/2.0;
    centerY = height/2.0;

    X = *x - centerX;
    Y = *y - centerY;

    tmpx = (currenttrafo->m11 * X) + (currenttrafo->m12 * Y);
    tmpy = (currenttrafo->m21 * X) + (currenttrafo->m22 * Y);

    *x = (int)(tmpx + centerX);
    *y = (int)(tmpy + centerY);

    return 0;
}

int line(int x0, int y0, int x1, int y1) 
{
    //http://rosettacode.org/wiki/Bitmap/Bresenham's_line_algorithm

    int dx, dy, err;
    int sx, sy, e2;

    /*
    if(transform(&x0, &y0)||transform(&x1, &y1)){
        fprintf(stderr, "Transformation ERROR\n");
        return -1;
    }
    */
    
    transform(&x0, &y0);
    transform(&x1, &y1);

    dx = abs(x1-x0);
    sx = x0<x1 ? 1 : -1;
    dy = abs(y1-y0);
    sy = y0<y1 ? 1 : -1; 
    err = (dx>dy ? dx : -dy)/2;
    //e2;
    //char skipper = 0;

    //not sure about this yet, but
    //for the moment trafo is implemented 
    //here

    for(;;){
	//the style shit should become global, 
	//if you do poly s you want continuity etc..
	//Right??    
        if (linestyle == 1) {
                skipper++;
            if (skipper<5) pPlot(x0, y0);
            else if (skipper==10) skipper = 0;
        
        }
        if (linestyle == 2) {
            if (skipper==1) {
                pPlot(x0,y0);
                skipper=0;
            }else skipper++;	
        }
        if (linestyle == 0) pPlot(x0, y0);

        if (x0==x1 && y0==y1) break;
        e2 = err;
        if (e2 >-dx) { err -= dy; x0 += sx; }
        if (e2 < dy) { err += dx; y0 += sy; }
    }
    return 0;
}

int arc(int x0, int y0, int r1, int r2, int startseg, int endseg, int segs) 
{
    int i;
    double alpha;
    int x_old, y_old;
    int x, y;

    alpha = 2 * M_PI * startseg/segs;
    x_old = (int)(r1*cos(alpha)+x0);
    y_old = (int)(r2*sin(alpha)+y0);

    for (i=(startseg+1); i<=endseg; i++){
        alpha = 2 * M_PI * i/segs;
        x = (int)(r1*cos(alpha)+x0);
	y = (int)(r2*sin(alpha)+y0);
	line(x_old, y_old, x, y);
	x_old = x;
	y_old = y;
    }
    return 0;
}

int circle(int x0, int y0, int r1, int segs)
{
    return arc(x0, y0, r1, r1, 0, segs, segs);
}

int printxy(int x0, int y0, char *text, int size_)
{
	int w=0;
	int i,j;
    int tx;
    int ty;
	static unsigned char mask[] = {128, 64, 32, 16, 8, 4, 2, 1};
    struct Color backgrnd;

	while (*(text+w)!=0){
		for (i=0;i<CHARH;i++)
			for (j=0;j<CHARW;j++)
				if (CHARMAP[CHARH* *(text+w) + i] & mask[j]){
					if (size_ == 1){
                        tx = x0+j+(CHARW*w);
                        ty = y0+i;
                        transform(&tx, &ty);
						pPlot(tx, ty); 
                    }
					else{
						pPlot(x0+j*3+(CHARW*w*3), y0+(i*3));
						pPlot(x0+j*3+(CHARW*w*3)+1, y0+(i*3));
						pPlot(x0+j*3+(CHARW*w*3), y0+(i*3)+1);
						pPlot(x0+j*3+(CHARW*w*3)+1, y0+(i*3)+1);
					}
				}
		w++;
		if (w>255) return -1;//dont make long sentences...
	}
	return 0;
}

int graticule(int x0, int y0, int w, int h)
{
	int i;
	int j;
    unsigned char tmpls;    //line style store
	int dx,dy;
	double xstep;
	double ystep;
    int grid = 10;

	struct Color dummycolor;
    tmpls = linestyle;

	xstep = 1.0*w/grid;
	ystep = 1.0*h/grid;	

    for (i=0; i<=grid;i++){
        dx = (int)(i*xstep);
        dy = (int)(i*ystep);
        if (i==5) {
            linestyle = 0;
            //dummycolor = *mycolor2;
        }
        else {
            linestyle = 2;
            //dummycolor = *mycolor;
        }
        //main cross
        line(x0+dx,y0,x0+dx,y0+h);     
        line(x0,y0+dy,x0+w,y0+dy);
        //ticks
        line(x0+dx,y0+(int)(4.8*ystep), x0+dx, y0+(int)(5.2*ystep));
        line(x0+(int)(4.8*xstep),y0+dy,x0+(int)(5.2*xstep),y0+dy);
    }

    linestyle = tmpls;
    //currentcolor = 
	return 0;
}

int getHeight()
{
    return vinfo.yres;
}

int getWidth()
{
    return vinfo.xres;
}

int overlay(char *res_buf, char *sprite_buf, int xo, int yo, char sprmode)
{
    int offset;
    int offn4,offo4;                //offn * 4
    int voffo, voffn;
    int pix_offset;
    int l;
    int Oxsb, Oysb, wsb4, hsb;
    int LOx, LOy;               //local winparams
    int tailn, tailo;               //tail + offset = width
    int vtailn, vtailo;
    int tmpL;                       //mod tails
    int xi,yi;
    /*
     * Determine the major square containing sprite @
     * old position and new position,
     * I'll call this me scratchbook sb
     * Ill copy current fb to sb
     * restore with res_buf, grab the new res_buf
     * patch N draw the sprite @ new R in tmp_buf. 
     * finaly copy tmp_buf to fb
     *
     * returns -1 if new crds are outabounds
     * returns -2 if old      ---,,---
     */

    /* 
     * and prevent segfaultHELLLLL
     *
     * and leave stage gracefully...
     */

    if (-Ox>=width) return -1;
    //negative Ox would be > line_length wo
    //(int)
    if (Ox>=(int)vinfo.xres) return -1;

    if (-Oy>=height) return -1;
    if (Oy>=(int)vinfo.yres) return -1;

    if (-xo>=width) return -2;
    if (xo>=(int)vinfo.xres) return -2;

    if (-yo>=height) return -2;
    if (yo>=(int)vinfo.yres) return -2;

    if (Ox<0){
        LOx = 0;
        offn4 = BPP*-Ox;
    }
    else{
        LOx = Ox;
        offn4 = 0;
    }

    if (Oy<0){
        LOy=0;
        voffn = -Oy;
    }
    else{
        LOy = Oy;
        voffn = 0;
    }

    if (xo<0){
        offo4 = -BPP*xo;
        xo = 0;
    }
    else{
        offo4 =0;
    }

    if (yo<0){
        voffo = -yo;
        yo=0;
    }
    else{
        voffo=0;
    }

    tmpL=finfo.line_length-BPP*xo;
    if (tmpL<width4)
        tailo = tmpL;
    else
        tailo = width4-offo4;

    tmpL=finfo.line_length-BPP*Ox;
    if (tmpL < width4){
        tailn = tmpL;
    }
    else{
        tailn = width4-offn4;
    }

    tmpL = vinfo.yres - yo;
    if (tmpL<height)
        vtailo = tmpL;
    else
        vtailo = height-voffo;

    tmpL = vinfo.yres -Oy;
    if (tmpL<height)
        vtailn = tmpL;
    else
        vtailn = height-voffn;    

    if (Ox>xo){
        Oxsb = xo;
        wsb4 = BPP*(LOx-xo)+tailn;
    }
    else{
        Oxsb = LOx;
        wsb4 = BPP*(xo-LOx)+tailo;
    }

    if (Oy>yo){
        Oysb = yo;
        hsb = LOy-yo+vtailn;
    }
    else{
        Oysb = LOy;
        hsb = yo-LOy+vtailo;
    }
    
    /*
     * Dump current framebuffer to a dummy buffer
     * then I'll restore the old sprite patch
     * here. This will give a pre sprite era
     * /situation
     */
    pix_offset = Oxsb*BPP + Oysb*finfo.line_length;
    l=hsb;
    while(l--){
        memcpy(dummy_buf+pix_offset, fbp+pix_offset, wsb4);
        pix_offset+=finfo.line_length;
    }

    /* restore dummy (current) frambefuffer
     * Like no sprite had ever messed up my
     *background
     */ 

    pix_offset = xo*BPP + yo*finfo.line_length;
    offset = offo4+(voffo*width4);
    l=vtailo;    
    while(l--){
        memcpy(tmp_buf+pix_offset, res_buf+offset, tailo);
        memcpy(dummy_buf+pix_offset, res_buf+offset, tailo);
        pix_offset += finfo.line_length;
        offset+=width4;
    }
    /* prepare new patch 
     * by grabn new sprite 
     * pos from restored fb
     * AND
     * draw new sprite into tmp_buffer
     */
     
    if (sprmode==1){
        //TON;
        for (yi=0;yi<vtailn;yi++){
            offset = (yi+voffn)*width4+offn4;
            pix_offset = LOx*BPP+(LOy+yi)*finfo.line_length;
            for(xi=0;xi<tailn;xi++){
               *(res_buf+offset) = *(dummy_buf+pix_offset);
                if (*(sprite_buf+offset)!=0){
                    *(tmp_buf+pix_offset) = *(sprite_buf+offset);
                }
                offset++;
                pix_offset++;
            }
        }
        //TOFF;
    }
    
    //dumps tmp_buff into frambebuffer
    //only scratchbook size ofcourse
    pix_offset = Oxsb*BPP + Oysb*finfo.line_length;
    l=hsb;
    waitforvsync();
    while(l--){
        memcpy(fbp+pix_offset, tmp_buf+pix_offset, wsb4);
        pix_offset+=finfo.line_length;
    }
    return 0;
}

int helloworld(int x, int y)
{
    printf("Hello world %i + %i = %i!!\n", x, y, x+y);
    return 0;
}

int mandelbrot()
{
    //just a gimick, 
    //but fun
    

    return 0;
}

int read_PNG(char *file_name)
{
    /*
     * Took this code from doc/fblib
     * and adjusted it to the likings
     * of this program.
     * ?i
     * It is really awesome that a NOOB
     * like me, Noisegate can actually
     * make useable software on an open
     * system like this Linux...
     *
     * openSOFtWARE rocKS
     */

    png_structp png_ptr;
    png_infop info_ptr;
    unsigned int sig_read = 0;
    png_uint_32 _width, _height, row;
    int bit_depth, color_type, interlace_type;
    FILE *fp;

    float screen_gamma;

    if ((fp = fopen(file_name, "rb")) == NULL)
          return -1;

    /* Create and initialize the png_struct with the desired error handler
     * functions.  If you want to use the default stderr and longjump method,
     * you can supply NULL for the last three parameters.  We also supply the
     * the compiler header file version, so that we know if the application
     * was compiled with a compatible version of the library.  REQUIRED
     */
    //png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, png_voidp user_error_ptr, user_error_fn, user_warning_fn);
    png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, 
            (png_voidp)NULL, 
            (png_error_ptr)NULL, 
            (png_error_ptr)NULL);

    if (png_ptr == NULL){
        fclose(fp);
        return -1;
    }

    /* Allocate/initialize the memory for image information.  REQUIRED. */
    info_ptr = png_create_info_struct(png_ptr);
    if (info_ptr == NULL) {
        fclose(fp);
        png_destroy_read_struct(&png_ptr, png_infopp_NULL, png_infopp_NULL);
        return -1;
    }

    /* Set error handling if you are using the setjmp/longjmp method (this is
    * the normal method of doing things with libpng).  REQUIRED unless you
    * set up your own error handlers in the png_create_read_struct() earlier.
    */

    if (setjmp(png_jmpbuf(png_ptr))) {
        /* Free all of the memory associated with the png_ptr and info_ptr */
        png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);
        fclose(fp);
        /* If we get here, we had a problem reading the file */
        fprintf(stderr, "Error: Couldn't read the file.");
        return -1;
    }

    /* One of the following I/O initialization methods is REQUIRED */
    /* Set up the input control if you are using standard C streams */
    png_init_io(png_ptr, fp);

    /* If we have already read some of the signature */
    png_set_sig_bytes(png_ptr, sig_read);

   /* OK, you're doing it the hard way, with the lower-level functions */

   /* The call to png_read_info() gives us all of the information from the
    * PNG file before the first IDAT (image data chunk).  REQUIRED
    */
   png_read_info(png_ptr, info_ptr);

   png_get_IHDR(png_ptr, info_ptr, &_width, &_height, &bit_depth, &color_type,
       &interlace_type, int_p_NULL, int_p_NULL);

   /* Set up the data transformations you want.  Note that these are all
    * optional.  Only call them if you want/need them.  Many of the
    * transformations only work on specific types of images, and many
    * are mutually exclusive.
    */

   /* Tell libpng to strip 16 bit/color files down to 8 bits/color */
   png_set_strip_16(png_ptr);

   /* Strip alpha bytes from the input data without combining with the
    * background (not recommended).
    */
   //png_set_strip_alpha(png_ptr);

   /* Extract multiple pixels with bit depths of 1, 2, and 4 from a single
    * byte into separate bytes (useful for paletted and grayscale images).
    */
   png_set_packing(png_ptr);

   /* Change the order of packed pixels to least significant bit first
    * (not useful if you are using png_set_packing). */
   png_set_packswap(png_ptr);

   /* Expand paletted colors into true RGB triplets */
   if (color_type == PNG_COLOR_TYPE_PALETTE)
      png_set_palette_to_rgb(png_ptr);

   /* Expand grayscale images to the full 8 bits from 1, 2, or 4 bits/pixel */
   if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
      png_set_expand_gray_1_2_4_to_8(png_ptr);

   /* Expand paletted or RGB images with transparency to full alpha channels
    * so the data will be available as RGBA quartets.
    */
   if (png_get_valid(png_ptr, info_ptr, PNG_INFO_tRNS))
      png_set_tRNS_to_alpha(png_ptr);

   /* Set the background color to draw transparent and alpha images over.
    * It is possible to set the red, green, and blue components directly
    * for paletted images instead of supplying a palette index.  Note that
    * even if the PNG file supplies a background, you are not required to
    * use it - you should use the (solid) application background if it has one.
    */

   png_color_16 my_background, *image_background;

   if (png_get_bKGD(png_ptr, info_ptr, &image_background))
      png_set_background(png_ptr, image_background,
                         PNG_BACKGROUND_GAMMA_FILE, 1, 1.0);
   else
      png_set_background(png_ptr, &my_background,
                         PNG_BACKGROUND_GAMMA_SCREEN, 0, 1.0);


   screen_gamma = 1.0;

   int intent;

   if (png_get_sRGB(png_ptr, info_ptr, &intent))
      png_set_gamma(png_ptr, screen_gamma, 0.45455);
   else
   {
      double image_gamma;
      if (png_get_gAMA(png_ptr, info_ptr, &image_gamma))
         png_set_gamma(png_ptr, screen_gamma, image_gamma);
      else
         png_set_gamma(png_ptr, screen_gamma, 0.45455);
   }

   /* Invert monochrome files to have 0 as white and 1 as black */
   png_set_invert_mono(png_ptr);

   /* If you want to shift the pixel values from the range [0,255] or
    * [0,65535] to the original [0,7] or [0,31], or whatever range the
    * colors were originally in:
    */
   if (png_get_valid(png_ptr, info_ptr, PNG_INFO_sBIT))
   {
      png_color_8p sig_bit_p;

      png_get_sBIT(png_ptr, info_ptr, &sig_bit_p);
      png_set_shift(png_ptr, sig_bit_p);
   }

   /* Flip the RGB pixels to BGR (or RGBA to BGRA) */
   if (color_type & PNG_COLOR_MASK_COLOR)
      png_set_bgr(png_ptr);

   /* Swap the RGBA or GA data to ARGB or AG (or BGRA to ABGR) */
   png_set_swap_alpha(png_ptr);

   /* Swap bytes of 16 bit files to least significant byte first */
   png_set_swap(png_ptr);

   /* Add filler (or alpha) byte (before/after each RGB triplet) */
   png_set_filler(png_ptr, 0x00, PNG_FILLER_AFTER);

   /* Turn on interlace handling.  REQUIRED if you are not using
    * png_read_image().  To see how to handle interlacing passes,
    * see the png_read_row() method below:
    */
   //number_passes = png_set_interlace_handling(png_ptr);

   /* Optional call to gamma correct and add the background to the palette
    * and update info structure.  REQUIRED if you are expecting libpng to
    * update the palette for you (ie you selected such a transform above).
    */
   png_read_update_info(png_ptr, info_ptr);

   /* Allocate the memory to hold the image using the fields of info_ptr. */

   /* The easiest way to read the image: */
   png_bytep row_pointers[_height];

   /* Clear the pointer array */
   for (row = 0; row < _height; row++)
      row_pointers[row] = NULL;

   for (row = 0; row < _height; row++)
      row_pointers[row] = png_malloc(png_ptr, png_get_rowbytes(png_ptr,
         info_ptr));

   /* Now it's time to read the image.  One of these methods is REQUIRED */
   png_read_image(png_ptr, row_pointers);


   /* Now mess this rowpointer thing into the tmp_buf
    * U dont know if width>_width and height>_height
    * so we trunc the guy
    */
    
   int maxY = _height>height?height:_height;
   int maxX = _width>width?finfo.line_length:_width;
   int pix_offset=0;

   for (row=0; row<maxY;row++){
       pix_offset = Ox*BPP + ((Oy+row)*finfo.line_length);
       memcpy(tmp_buf+pix_offset, row_pointers[row], maxX*BPP);
   }

   /* Read rest of file, and get additional chunks in info_ptr - REQUIRED */
   png_read_end(png_ptr, info_ptr);

   /* At this point you have read the entire image */

   /* Clean up after the read, and free any memory allocated - REQUIRED */
   png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);

   /* Close the file */
   fclose(fp);


   //printf("png W x H = %i x %i\n", _width, _height);
   /* That's it */
    return 0;
}


int write_PNG(char *filename, int interlace, char borfb)
{
    //hardcore theft from fbgrab.c
	/*
	 * fbgrab - takes screenshots using the framebuffer.
	 *
	 * (C) Gunnar Monell <gmo@linux.nu> 2002
	 *
	 * This program is free Software, see the COPYING file
	 * and is based on Stephan Beyer's <fbshot@s-beyer.de> FBShot
	 * (C) 2000.
	 *
	 * For features and differences, read the manual page. 
	 *
	 * This program has been checked with "splint +posixlib" without
	 * warnings. Splint is available from http://www.splint.org/ .
	 * Patches and enhancements of fbgrab have to fulfill this too.
	 */

    png_uint_32 i;
    int bit_depth=0, color_type;
    png_uint_32 uheight, uwidth;

    uheight = (png_uint_32)height;
    uwidth = (png_uint_32)width;

    png_bytep row_pointers[uheight];
    png_structp png_ptr;
    png_infop info_ptr;
    FILE *outfile = fopen(filename, "wb");

    interlace = PNG_INTERLACE_NONE;    

    //printf ("%d, %d\n", uheight, uwidth);

    //well, either from the buffer or the framebuffer...
    //yih, gotta clean this one up, reallyyyyy
    //
    if (borfb == 0)
        for (i=0; i<uheight; i++)
	        row_pointers[i] = (unsigned char *)(fbp + (BPP*Ox) + (Oy + i) * 1 * (finfo.line_length/*uwidth+10*/));
    if (borfb == 1)
        for (i=0; i<uheight; i++)
	        row_pointers[i] = (unsigned char *)(tmp_buf + (BPP*Ox) + (Oy + i) * 1 * (finfo.line_length/*uwidth+10*/));
 
    if (!outfile){ 
	    fprintf (stderr, "Error: Couldn't fopen %s.\n", filename);
	    return -1;
    }
    
    png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING,
        (png_voidp) NULL, (png_error_ptr) NULL, (png_error_ptr) NULL);
    
    if (!png_ptr){
	    fprintf(stderr,"Error: Couldn't create PNG write struct.");
        return -1;
    }

    info_ptr = png_create_info_struct(png_ptr);

    if (!info_ptr){
	    png_destroy_write_struct(&png_ptr, (png_infopp) NULL);
	    fprintf(stderr, "Error: Couldn't create PNG info struct.");
        return -1;
    }
    if (setjmp(png_jmpbuf(png_ptr))){
        fclose(outfile);
        png_destroy_write_struct(&png_ptr, &info_ptr);
        return -2;
    }
 
    png_init_io(png_ptr, outfile);
    
    //png_set_compression_level(png_ptr, Z_BEST_COMPRESSION);
    
    bit_depth = 8;
    color_type = PNG_COLOR_TYPE_RGB_ALPHA;
    
    png_set_IHDR(png_ptr, info_ptr, uwidth, uheight, 
		 bit_depth, PNG_COLOR_TYPE_RGBA, PNG_INTERLACE_NONE, 
		 PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);

    //png_set_packing(png_ptr);
    png_set_invert_alpha(png_ptr);
    //
    //png_set function must be after set_IHDR
    //according to libpng-manual
    png_set_filter(png_ptr, 0, PNG_FILTER_NONE);
    png_set_filler(png_ptr, 0 , PNG_FILLER_BEFORE);
    png_set_bgr(png_ptr);
    
    png_write_info(png_ptr, info_ptr);
    
    //printf ("Now writing PNG file\n");
    png_write_image(png_ptr, row_pointers);
    //png_write_rows(png_ptr, row_pointers, uheight);
    png_write_end(png_ptr, info_ptr);
    //puh, done, now freeing memory... 
    png_destroy_write_struct(&png_ptr, &info_ptr);
    
    if (outfile != NULL)
	    (void) fclose(outfile);
    //printf("Done writing...\n");
    return 0;
}

/*
 * TODO:
    double Sx[3][3];
    double Sy[3][3];

    Sx[0][0] = 1.0;
    Sx[0][1] = 0.0;
    Sx[0][2] = 0.0;
    Sx[1][0] = 0.0;
    Sx[1][1] = 1.0;
    Sx[1][2] = 0.0;
    Sx[2][0] = -tan(-angle/2.0);
    Sx[2][1] = 0.0;
    Sx[2][2] = 1.0;

    Sy[0][0] = 1.0;
    Sy[0][1] = 0.0;
    Sy[0][2] = sin(-angle);
    Sy[1][0] = 0.0;
    Sy[1][1] = 1.0;
    Sy[1][2] = 0.0;
    Sy[2][0] = 0.0;
    Sy[2][1] = 0.0;
    Sy[2][2] = 1.0;

    matrixvec3(Sx, x, y, z);
    matrixvec3(Sy, x, y, z);
    matrixvec3(Sx, x, y, z);    
 */
