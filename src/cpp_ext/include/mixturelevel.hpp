#pragma once

#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "aliases.hpp"

namespace hem
{
class FeatureVector;

class MixtureLevel
{
public:
	MixtureLevel();

	static MixtureLevel CreateMixtureLevel(
    const pybind11::list& xyz,
    const pybind11::list& colors,
    const pybind11::list& opacities,
    const pybind11::list& covariance,
    const pybind11::list& features);

    static pybind11::tuple MixtureLevel::CreatePythonLists(MixtureLevel &mixtureLevel);

public:
	PointSet pointSet;
	ColorSet colorSet;
	CovarianceSet covarianceSet;
	std::vector<float> opacities;
	std::vector<FeatureVector> features;
};

}
