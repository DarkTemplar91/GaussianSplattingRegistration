#ifndef MIXTURE_WRAPPER_H
#define MIXTURE_WRAPPER_H
#include <iostream>
#include <string>
extern "C" {
    std::string call_mixture_creation(std::string gaussianJson);
}

#endif  // MIXTURE_WRAPPER_H