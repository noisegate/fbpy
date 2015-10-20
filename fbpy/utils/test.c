/*
 * test.c lib for pythons fbpy package. Some mem play for
 * multiple polygon functionality in fbutils. 
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
 *version: 0.1
 *profanities included 4 xtra power/*
 * test module
 * just wanna clean up
 * fbutils a bit
 * so add extra functions
 * here
 *
 * http://stackoverflow.com/questions/14768230/malloc-for-struct-and-pointer-in-c
*/

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include "test.h"

#define DEBUG 0

int addpoly(Polys *ret, int *x, int *y, int *z, int lenxy)
{
	/*
	 * TODO:
	 * read form Undersanding and using c pointers on allocating
	 * contiguous memory, page 100 or somethin..
	 */

	int i;
	//Polys *ret = (Polys*) malloc(sizeof(Polys));

	if (dbgrdr == 0)
		debug = stdout;
	else
		debug = fopen("/dev/null","w");


	fprintf(debug, "size of x and y: %i \n",lenxy);
	fprintf(debug, "visit %i\n", visits);

	if (visits==0){
		ret->x = (int **) malloc(sizeof(int *));
		ret->y = (int **) malloc(sizeof(int *));
		ret->z = (int **) malloc(sizeof(int *));
		ret->polyl = (int *) malloc(sizeof(int));
	}else{
		fprintf(debug, "Reallocating...\n");
		int ** newx = (int **) realloc(ret->x, (visits+1) * sizeof(int *));
		int ** newy = (int **) realloc(ret->y, (visits+1) * sizeof(int *));
		int ** newz = (int **) realloc(ret->z, (visits+1) * sizeof(int *));
		int * newpolyl = (int *) realloc(ret->polyl, (visits+1) * sizeof(int));
		ret->x = newx;
		ret->y = newy;
		ret->z = newz;
		ret->polyl = newpolyl;
	}

	if (	(ret->x == NULL) || 
		(ret->y == NULL) || 
		(ret->z == NULL) ||
		(ret->polyl == NULL)){
		fprintf(stderr, "memory allocation problem case I\n");
		return -1;
	}

	*(ret->x + visits) = (int *)malloc(lenxy*sizeof(int));
	*(ret->y + visits) = (int *)malloc(lenxy*sizeof(int));
	*(ret->z + visits) = (int *)malloc(lenxy*sizeof(int));
	*(ret->polyl + visits) = lenxy;
	
	if ((*(ret->x + visits)==NULL) || 
	    (*(ret->y + visits)==NULL) || 
	    (*(ret->z + visits)==NULL) ||
	    (*(ret->polyl + visits)==NULL))
		fprintf(stderr, "memory allocation problem case II\n");

	//copy x and y to me

	fprintf(debug, "done allocations, commencing copy\n");	
	for (i=0; i<lenxy;i++){
		*((*(ret->x + visits)+i)) = x[i];
		*((*(ret->y + visits)+i)) = y[i];
		*((*(ret->z + visits)+i)) = z[i];
	}
	fflush(debug);
	visits++;
	ret->polyc = visits;
	fclose(debug);
	return 0;
}

int setpms(int dbgrdr_, int visits_)
{
	visits = visits_;
	dbgrdr = dbgrdr_;
	return 0;
}

int delpolys(Polys *p)
{
	//clears ALL polies!!!
	
	int i;

	if (dbgrdr==1)
		debug = stdout;
	else
		debug = fopen("/dev/null","w");
	if (p==NULL) {
		fprintf(stderr, "vector does not exist");
		return -1;
	}
	
	for (i=0; i<p->polyc;i++){
		fprintf(debug, "freeing set %i\n", i);
		fprintf(debug, "the address of the one to be freed %p\n", *(p->x+i));
		if (*(p->x+i)!=NULL) free(*(p->x+i));
		if (*(p->y+i)!=NULL) free(*(p->y+i));
		if (*(p->z+i)!=NULL) free(*(p->z+i));
	}
	free(p->polyl);
	visits = 0;
	fclose(debug);	
	return 0;
}

int main()
{

	int i, j;

	int x1[3] = {1,2,3};
	int y1[3] = {1,4,9};
	int z1[3] = {0,0,0};
	
	int x2[5] = {0,2,3,4,5};
	int y2[5] = {0,4,9,16,25};
	int z2[5] = {0,0,0,0,0};
	Polys p;

	if (DEBUG)
		debug = stdout;
	else
		debug = fopen("/dev/null","w");


	if (addpoly(&p, x1, y1, z1, 3)) return -1;
	if (addpoly(&p, x2, y2, z2, 5)) return -1;

	printf("number of polies in p: %i\n",p.polyc);

	for (i=0; i<p.polyc;i++){
		printf("vector %i\n", i);
		printf("===============\n");
		for(j=0;j<*(p.polyl+i);j++){
			printf("x=%i \t y=%i z=%i\n",
				*(*(p.x+i)+j), *(*(p.y+i)+j),
				*(*(p.z+i)+j));
		}
	}
	
	delpolys(&p);
	fclose(debug);
	return 0;
}
