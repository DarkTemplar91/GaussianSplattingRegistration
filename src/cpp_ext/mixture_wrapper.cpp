#include "mixture_wrapper.hpp"
#include "mixturelevel.hpp"
#include "mixture.hpp"
#include "vec.hpp"
#include <string>

using namespace hem;


std::vector<MixtureLevel> MixtureCreator::CreateMixture(unsigned int clusterLevel, float hemReduction, float distanceDelta, float colorDelta, MixtureLevel &mixtureLevel) {

    std::cout << "cluster level: " << clusterLevel << std::endl;
    std::cout << "hem reduction: " << hemReduction << std::endl;
    std::cout << "distance delta: " << distanceDelta << std::endl;
    std::cout << "color delta: " << colorDelta << std::endl;

    Mixture* mixture = new Mixture(mixtureLevel, hemReduction, distanceDelta, colorDelta);
    mixture->CreateMixture(clusterLevel);

    auto result = mixture->GetResult();
    result.erase(result.begin());

    return result;
}