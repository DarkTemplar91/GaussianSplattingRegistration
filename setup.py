from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "mixture_bind",  # Name of the Cython module
        sources=["src/cpp_ext/mixture_bind.pyx", "src/cpp_ext/mixture_wrapper.cpp",
                 "src/cpp_ext/src/mixture.cpp", "src/cpp_ext/src/mixturelevel.cpp",
                 "src/cpp_ext/src/pointindex.cpp",
                 "src/cpp_ext/src/featurevector.cpp"],  # List of source files
        include_dirs=["src/cpp_ext/include/"],  # Optional: Include directories for header files
        language="c++",  # Language for compilation
        extra_compile_args=["/O2", "/std:c++14", "/openmp", "/Ot"]
    )
]

setup(
    name='mixture_bind',
    ext_modules=cythonize(extensions),
)