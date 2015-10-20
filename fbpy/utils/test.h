#ifndef __TEST_H__
#define __TEST_H__

typedef struct _Polys{
	int **x;
	int **y;
	int **z;
	int *polyl;	//length of each
	int polyc;	//number of polies
};

typedef struct _Polys Polys;

FILE *debug;
char dbgrdr;
int visits;

int addpoly(Polys *, int x[], int y[], int z[], int lenxy);
int setpms(int dbgrdr_, int visits_);
int delpolys(Polys *);

#endif //__TEST_H__
