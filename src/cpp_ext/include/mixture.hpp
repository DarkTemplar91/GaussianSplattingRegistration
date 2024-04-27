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
#include <algorithm>
#include <cassert>
#include <iostream>
#include <omp.h>

#include "gaussian.hpp"
#include "pointindex.hpp"
#include "aliases.hpp"
#include "mixturelevel.hpp"

using namespace std;

namespace hem
{
	struct Component : Gaussian
	{
		Component();
		Component(const Gaussian& g, const vec3& nvar = vec3(0, 0, 0));

		// models the distribution of the Gaussian's normals using a spherical Gaussian
		// direction: mean normal. length: variance of spherical Gaussian
		vec3 nvar;	

		// Indicates if the component has been selected for the parent role or not in the case of HEM clustering
		bool is_parent;
	};


	/// Mixture of Gaussians
	class Mixture
	{
	public:
		Mixture();
		Mixture(MixtureLevel &initialMixture, float hemReductionFactor, float distanceDelta, float colorDelta);

		void CreateMixture(uint clusterLevel);

		std::vector<MixtureLevel> GetResult();
	protected:

		float hemLikelihood(const Gaussian& parent, const Gaussian& child);
		void createClusterLevel(vector<Component>& newComponents);
		void initMixture(MixtureLevel &initialMixtureLevel);

	private:
		float	distanceDelta;
		float	colorDelta;
		float	hemReductionFactor;

		std::vector<Component> initialMixture;
		std::vector<std::vector<Component>> mixtureList;

		int featureSize;

	};

}



