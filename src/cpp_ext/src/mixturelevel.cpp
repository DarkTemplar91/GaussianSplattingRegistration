#include "mixturelevel.hpp"

namespace hem
{
	MixtureLevel::MixtureLevel(): pointSet(), covarianceSet(), colorSet()
	{

	}

	void from_json(const nlohmann::json& j, MixtureLevel& mixtureLevel)
	{
		mixtureLevel.pointSet = j.at("xyz").get<PointSet>();
		mixtureLevel.colorSet = j.at("colors").get<ColorSet>();
		mixtureLevel.covarianceSet = j.at("covariance").get<CovarianceSet>();
	}

	void to_json(nlohmann::json& j, const MixtureLevel& mixtureLevel)
	{
		j = nlohmann::json{ {"xyz", mixtureLevel.pointSet}, {"colors", mixtureLevel.colorSet}, {"covariance", mixtureLevel.covarianceSet} };
	}
}