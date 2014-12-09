all: fblib.so

fblib.c: fblib.pyx
	cython fblib.pyx

fbutils.o: fbutils.c fbutils.h font.h
	gcc -g -O2 -fpic -c fbutils.c -lm -lpng -o fbutils.o

fblib.o: fblib.c
	gcc -g -O2 -fpic -c fblib.c -o fblib.o `python-config --cflags`

fblib.so: fblib.o fbutils.o
	gcc -shared -o fblib.so fbutils.o fblib.o `python-config --libs`

clean:
	rm fblib.so fblib.o fbutils.o fblib.c

