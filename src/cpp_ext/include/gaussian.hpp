//=============================================================================
// CLOP Source
//-----------------------------------------------------------------------------
// Reference Implementation for
// Preiner et al., Continuous Projection for Fast L1 Reconstruction, In 
// Proceedings of ACM SIGGRAPH 2014
// www.cg.tuwien.ac.at/research/publications/2014/preiner2014clop
//-----------------------------------------------------------------------------
// (c) Reinhold Preiner, Vienna University of Technology, 2014
// All rights reserved. This code is licensed under the New BSD License:
// http://opensource.org/licenses/BSD-3-Clause
// Contact: rp@cg.tuwien.ac.at
//=============================================================================


#pragma once

#include <vector>
#include <iostream>

#include "vec.hpp"
#include "featurevector.hpp"


using namespace std;



namespace hem
{
	class FeatureVector;

#pragma region covariance matrix operators

	// Conditioning by off diagonal dampening
	inline smat3 conditionCov(const smat3& cov, vec3& outEvalues, float epsilon = 1e-10f)
	{
		smat3 newCov;
		float abseps = fabsf(epsilon);

		// condition diagonal elements
		newCov.e00 = fmaxf(cov.e00, abseps);
		newCov.e11 = fmaxf(cov.e11, abseps);
		newCov.e22 = fmaxf(cov.e22, abseps);

		// condition off diagonal elements
		float sx = sqrtf(cov.e00);
		float sy = sqrtf(cov.e11);
		float sz = sqrtf(cov.e22);

		for (float rho = 0.99f; rho >= 0; rho -= 0.01f)
		{
			float rxy = rho * sx * sy;
			float rxz = rho * sx * sz;
			float ryz = rho * sy * sz;
			newCov.e01 = clamp(cov.e01, -rxy, rxy);
			newCov.e02 = clamp(cov.e02, -rxz, rxz);
			newCov.e12 = clamp(cov.e12, -ryz, ryz);

			outEvalues = cov.eigenvalues();
			if (outEvalues.x > 0.0f)
				break;
		}

		if (outEvalues.x <= 0.0f)
		{
			std::cout << "Warning: cov still non-psd despite conditioning! det: " << det(cov) << ", cov: " << cov.toString();
			std::cout << ", evalues: " << outEvalues << ", " << std::endl;
		}

		return cov;
	}

	inline smat3 conditionCov(const smat3& cov, float epsilon = 1e-10f)
	{
		vec3 evd;
		return conditionCov(cov, evd, epsilon);
	}
	

	// squared Mahalanobis distance between two points X and Y, given the covariance matrix cov
	inline float SMD(const vec3& X, const vec3& Y, const smat3& cov)
	{
		return dot(X - Y, inverse(cov) * (X - Y));
	}

#pragma endregion


	struct Gaussian
	{
		vec3 mean;		             // xyz coordinates of the Gaussian
		vec3 color;		             // color values of the Gaussian
		smat3 cov;		             // symmetric covariance matrix
		float opacity;               // opacity of splat
		float weight;	             // weight
		FeatureVector featureVector; // Spherical Harmonics

		Gaussian(){}
		Gaussian(const vec3& mean, const vec3& color, const smat3& cov, const FeatureVector featureVector, float opacity, float weight = 1.0f)
			: mean(mean), color(color), cov(cov), featureVector(featureVector), opacity(opacity), weight(weight){}

	};

	// Kullback-Leibler distance between two Gaussians
	inline float KLD(const Gaussian& gc, const Gaussian& gp)
	{
		return 0.5f * (SMD(gc.mean, gp.mean, gp.cov) + trace(inverse(gp.cov) * gc.cov) - 3.0f - log(det(gc.cov) / det(gp.cov)));
	}

	inline float ColorDelta(const Gaussian& gc, const Gaussian& gp)
	{
		return dist(gc.color, gp.color);
	}


}

