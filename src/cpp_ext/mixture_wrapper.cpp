#include "mixture_wrapper.h"
#include "json.hpp"
#include "mixturelevel.hpp"
#include "mixture.hpp"
#include "vec.hpp"
#include <string>

using namespace hem;
using json = nlohmann::json;

extern "C" {
    std::string call_mixture_creation(std::string gaussianJson) {
	    // Parse the JSON data
	    json data;
	    try {
	    	data = json::parse(gaussianJson);
	    }
	    catch (const json::parse_error& e) {
	    	return "Failed to parse JSON";
	    }

	    uint clusterLevel = data["cluster_level"];
	    float hemReduction = data["hem_reduction"];
	    float distanceDelta = data["distance_delta"];
	    float colorDelta = data["color_delta"];

	    MixtureLevel mixtureLevel = data.get<MixtureLevel>();

	    Mixture* mixture = new Mixture(mixtureLevel, hemReduction, distanceDelta, colorDelta);
	    mixture->CreateMixture(clusterLevel);

	    auto result = mixture->GetResult();
	    result.erase(result.begin());

	    json resultJson = result;
	    return resultJson.dump();
    }
}