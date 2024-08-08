#include "vec.hpp"
#include "mixturelevel.hpp"
#include "featurevector.hpp"
#include "mixture_wrapper.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(mixture_bind, m) {
    m.doc() = "pybind11 example plugin"; // Optional docstring

    py::class_<hem::vec3>(m, "vec3")
        .def(py::init<>())
        .def(py::init<float, float, float>())
        .def(py::init<std::vector<float>>())
        .def_readwrite("x", &hem::vec3::x)
        .def_readwrite("y", &hem::vec3::y)
        .def_readwrite("z", &hem::vec3::z)
        .def("__repr__", [](const hem::vec3 &v) {
            return "<vec3(" + std::to_string(v.x) + ", " + std::to_string(v.y) + ", " + std::to_string(v.z) + ")>";
        });

    py::class_<hem::smat3>(m, "smat3")
        .def(py::init<>())
        .def(py::init<float, float, float, float, float, float>())
        .def(py::init<std::vector<float>>())
        .def_readwrite("e00", &hem::smat3::e00)
        .def_readwrite("e01", &hem::smat3::e01)
        .def_readwrite("e02", &hem::smat3::e02)
        .def_readwrite("e11", &hem::smat3::e11)
        .def_readwrite("e12", &hem::smat3::e12)
        .def_readwrite("e22", &hem::smat3::e22)
        .def("__repr__", [](const hem::smat3 &m) {
            return "<smat3(" + std::to_string(m.e00) + ", " + std::to_string(m.e01) + ", " + std::to_string(m.e02) + ", "
             + std::to_string(m.e11) + ", " + std::to_string(m.e12) + ", " + std::to_string(m.e22)+ ")>";
        });

    py::class_<hem::FeatureVector>(m, "FeatureVector")
        .def(py::init<>())
        .def(py::init<int>())
        .def(py::init<std::vector<float>>());

    py::class_<hem::MixtureLevel>(m, "MixtureLevel")
        .def(py::init<>())
        .def_readwrite("pointSet", &hem::MixtureLevel::pointSet)
        .def_readwrite("colorSet", &hem::MixtureLevel::colorSet)
        .def_readwrite("opacities", &hem::MixtureLevel::opacities)
        .def_readwrite("covarianceSet", &hem::MixtureLevel::covarianceSet)
        .def_readwrite("features", &hem::MixtureLevel::features)
        .def_static("CreateMixtureLevel", &hem::MixtureLevel::CreateMixtureLevel, "Create a MixtureLevel from Python lists.")
        .def_static("CreatePythonLists", &hem::MixtureLevel::CreatePythonLists, "Create python lists from MixtureLevel.");

    py::class_<hem::MixtureCreator>(m, "MixtureCreator")
        .def_static("CreateMixture", &hem::MixtureCreator::CreateMixture, "The function creates gaussian mixtures from the point cloud");

    py::implicitly_convertible<py::list, hem::vec3>();
    py::implicitly_convertible<py::list, hem::smat3>();
    py::implicitly_convertible<py::list, hem::FeatureVector>();
}