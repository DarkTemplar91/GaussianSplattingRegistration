from libcpp.string cimport string

cdef extern from "mixture_wrapper.h":
    string call_mixture_creation(string gaussianJson)

def create_mixture(gaussian):
    gaussianJson = gaussian.encode('utf-8')
    return call_mixture_creation(gaussianJson).decode()