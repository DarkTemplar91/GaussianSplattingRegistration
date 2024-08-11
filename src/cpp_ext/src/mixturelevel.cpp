#include "mixturelevel.hpp"
#include "featurevector.hpp"
#include "vec.hpp"

namespace py = pybind11;

namespace hem
{
	MixtureLevel::MixtureLevel(): pointSet(), covarianceSet(), colorSet(), opacities(), features()
	{

	}

	MixtureLevel MixtureLevel::CreateMixtureLevel(
	const py::list& xyz,
    const py::list& colors,
    const py::list& opacities,
    const py::list& covariance,
    const py::list& features)
    {
        hem::MixtureLevel mixtureLevel;
        mixtureLevel.pointSet = xyz.cast<std::vector<vec3>>();
        mixtureLevel.colorSet = colors.cast<std::vector<vec3>>();
        mixtureLevel.opacities = opacities.cast<std::vector<float>>();
        mixtureLevel.covarianceSet = covariance.cast<std::vector<smat3>>();
        mixtureLevel.features = features.cast<std::vector<FeatureVector>>();
        return mixtureLevel;
    }

    pybind11::tuple MixtureLevel::CreatePythonLists(MixtureLevel &mixtureLevel)
    {
        py::list xyz;
        for (const auto& point : mixtureLevel.pointSet) {
            xyz.append(py::make_tuple(point.x, point.y, point.z));
        }

        py::list colors;
        for (const auto& color : mixtureLevel.colorSet) {
            colors.append(py::make_tuple(color.x, color.y, color.z));
        }

        py::list opacities = py::cast(mixtureLevel.opacities);

        py::list covariance;
        for (const auto& cov : mixtureLevel.covarianceSet) {
            covariance.append(py::make_tuple(cov.e00, cov.e01, cov.e02, cov.e11, cov.e12, cov.e22));
        }

        py::list features;
        for (const auto& feature : mixtureLevel.features) {
            features.append(py::cast(feature.GetVector()));
        }

        return py::make_tuple(xyz, colors, opacities, covariance, features);
    }
}