#include "mixturelevel.hpp"
#include "featurevector.hpp"

namespace hem
{
	MixtureLevel::MixtureLevel(): pointSet(), covarianceSet(), colorSet(), opacities(), features()
	{

	}

	void from_json(const nlohmann::json& j, MixtureLevel& mixtureLevel)
	{
		mixtureLevel.pointSet = j.at("xyz").get<PointSet>();
		mixtureLevel.colorSet = j.at("colors").get<ColorSet>();
		mixtureLevel.covarianceSet = j.at("covariance").get<CovarianceSet>();
		mixtureLevel.opacities = j.at("opacities").get<std::vector<float>>();
		mixtureLevel.features = j.at("features").get<std::vector<FeatureVector>>();
	}

	void to_json(nlohmann::json& j, const MixtureLevel& mixtureLevel)
	{
		j = nlohmann::json{ {"xyz", mixtureLevel.pointSet}, {"colors", mixtureLevel.colorSet}, {"covariance", mixtureLevel.covarianceSet}, {"opacities", mixtureLevel.opacities},
			{"features", mixtureLevel.features}};
	}
}