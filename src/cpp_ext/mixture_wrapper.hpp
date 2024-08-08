#pragma once
#include <vector>
namespace hem
{
class MixtureLevel;

class MixtureCreator
{
public:
    static std::vector<MixtureLevel> CreateMixture(unsigned int clusterLevel, float hemReduction, float distanceDelta, float colorDelta, MixtureLevel &mixtureLevel);
};

}