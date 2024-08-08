#include "featurevector.hpp"

namespace hem
{

FeatureVector::FeatureVector() : valueVector() {}
FeatureVector::FeatureVector(int size) : valueVector(size) {}
FeatureVector::FeatureVector(std::vector<float> valueVector) : valueVector(valueVector) {}

int FeatureVector::GetSize() const
{
    return valueVector.size();
}

const std::vector<float>& FeatureVector::GetVector() const
{
    return valueVector;
}

FeatureVector FeatureVector::operator+(const FeatureVector& other) const
{
    std::vector<float> result(valueVector.size());
    for (size_t i = 0; i < valueVector.size(); ++i) {
        result[i] = valueVector[i] + other.valueVector[i];
    }

    return FeatureVector(result);
}

FeatureVector FeatureVector::operator*(const float& value) const
{
    std::vector<float> result(valueVector.size());
    for (size_t i = 0; i < valueVector.size(); ++i) {
        result[i] = valueVector[i] * value;
    }
    return FeatureVector(result);
}

const FeatureVector operator*(const float value, const FeatureVector& featureVector)
{
    return featureVector * value;
}

FeatureVector& FeatureVector::operator=(const FeatureVector& other) {
    if (this != &other) {
        valueVector = other.valueVector;
    }
    return *this;
}
/*
FeatureVector& FeatureVector::operator=(std::vector<float> other)
{
    valueVector = other;
    return *this;
}*/

FeatureVector& FeatureVector::operator+=(const FeatureVector& other)
{
    for (size_t i = 0; i < valueVector.size(); ++i) {
        valueVector[i] += other.valueVector[i];
    }
    return *this;
}

}