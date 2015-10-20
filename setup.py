from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


sourcefiles = ['./fbpy/utils/fblib.pyx']

extensions = [
                Extension(  "fblib",
                            libraries = ['png','jack'],
                            sources = [ './fbpy/utils/fblib.pyx', 
                                        './fbpy/utils/fbutils.c', 
                                        './fbpy/utils/test.c',
                                        './fbpy/utils/audio.c']
                            )
            ]

setup(  name='fbpy',
        version='0.1',
        author='marcell marosvolgyi',
        author_email='marcell@noisegate.org',
        url='http://transistorlove.wordpress.com',
        packages=['fbpy','fbpy.utils'],
        cmdclass = { 'build_ext' : build_ext },
        #ext_modules = cythonize([module0, module1])
        ext_modules = cythonize(extensions)
        )

