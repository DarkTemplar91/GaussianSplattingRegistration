#pragma once

#include <vector>
#include <json.hpp>
#include "aliases.hpp"

namespace hem
{
	class FeatureVector;
class MixtureLevel
{
public:
	MixtureLevel();

public:
	PointSet pointSet;
	ColorSet colorSet;
	CovarianceSet covarianceSet;
	std::vector<float> opacities;
	std::vector<FeatureVector> features;
};

void from_json(const nlohmann::json& j, MixtureLevel& mixtureLevel);
void to_json(nlohmann::json& j, const MixtureLevel& mixtureLevel);

}
