#pragma once
#include <vector>

namespace hem
{
class MixtureLevel;
class FeatureVector
{
public:
    FeatureVector();
    FeatureVector(int size);
	FeatureVector(std::vector<float> valueVector);

    int GetSize() const;
    const std::vector<float>& GetVector() const;

    FeatureVector operator+(const FeatureVector& other) const;
    FeatureVector operator*(const float& value) const;
    FeatureVector& operator=(const FeatureVector& other);
    //FeatureVector& operator=(std::vector<float> other);
    FeatureVector& operator+=(const FeatureVector& other);

private:
	std::vector<float> valueVector;
};

const FeatureVector operator*(const float n, const FeatureVector& featureVector);

}
