#include "mixture.hpp"

namespace hem
{
#pragma region Component

	Component::Component() : is_parent(false), nvar() {}
	Component::Component(const Gaussian& g, const vec3& nvar /* = vec3(0, 0, 0) */) : Gaussian(g), nvar(nvar), is_parent(false) {}

#pragma endregion

#pragma region Mixture

	Mixture::Mixture(MixtureLevel &initialMixture, float hemReductionFactor, float distanceDelta, float colorDelta)
		: hemReductionFactor(hemReductionFactor)
		, distanceDelta( distanceDelta )
		, colorDelta( colorDelta )
		, mixtureList()
		, featureSize(0)
	{
		initMixture(initialMixture);
	}

	void Mixture::CreateMixture(uint clusterLevel)
	{
		mixtureList.clear();
		mixtureList.push_back(initialMixture);

		for (uint l = 0; l < clusterLevel; ++l)
		{
			cout << "clustering level " << l << endl;
			createClusterLevel(mixtureList.back());
		}
	}

	float Mixture::hemLikelihood(const Gaussian& parent, const Gaussian& child)
	{
		vec3 mean_diff = parent.mean - child.mean;
		smat3 pCovInv = inverse(parent.cov);

		float smd = dot(mean_diff, pCovInv * mean_diff);
		smat3 ipcCov = pCovInv * child.cov;
		float ipcTrace = ipcCov.e00 + ipcCov.e11 + ipcCov.e22;

		// Gaussian exponent and the trace exponent
		float e = -0.5f * (smd + ipcTrace);
		// 1/((2pi)^(3/2))   *   sqrt(|Sigma1|)^-1 = sqrt(|Sigma1^-1|)   *   e^exponent   
		float f = 0.063493635934241f * sqrtf(det(pCovInv)) * expf(e);
		// raise to the power of the number of points in the child cluster
		return powf(f, child.weight);
	}

	float Mixture::hemLikelihoodOpacity(const Gaussian& child)
    {
	    return child.opacity * sqrtf(det(child.cov));
    }

	void Mixture::createClusterLevel(vector<Component>& parentMixture)
	{
		size_t nComponents = parentMixture.size();

		// 1. iterate over components, prepare index point centers and compute the parent's individual and maximum query radius
		vector<vec3> centers(nComponents);
		vector<uint> parentIndices;
		vector<float> queryRadii;
		float maxQueryRadius = 0;
		for (uint i = 0; i < nComponents; ++i)
		{
			const Component& c = parentMixture.at(i);

			// prepare centers to be indexed
			centers[i] = c.mean;

			// select parents
			if (c.is_parent)
			{
				parentIndices.push_back(i);

				// ii. get the conservative query radius for this parent
				float queryRadius = distanceDelta * sqrtf(c.cov.eigenvalues().z);
				queryRadii.push_back(queryRadius);

				// ii. determine maximum query radius
				if (queryRadius > maxQueryRadius)
					maxQueryRadius = queryRadius;
			}
		}


		// 2. create point index of component centers for neighbor queries
		PointIndex index(centers, maxQueryRadius);


		// 3. select child set for each parent
		size_t nParents = parentIndices.size();
		vector<vector<uint>> childIndices(nParents);

		#pragma omp parallel for
		for (int s_ = 0; s_ < nParents; ++s_)
		{
			int s = parentIndices[s_];
			const Gaussian& parent = parentMixture.at(s);

			vector<uint> resultSet;
			index.radiusSearch(parent.mean, queryRadii[s_], resultSet);

			// select eligible children from the conservative resultSet
			for (int i_ = 0; i_ < resultSet.size(); ++i_)
			{
				int i = resultSet[i_];
				const Component& child = parentMixture.at(i);


				float colorDiff = ColorDelta(child, parent);
				if (colorDiff > colorDelta * colorDelta * 0.5f)
					continue;

				float kld = KLD(child, parent);

				if (kld > distanceDelta * distanceDelta * 0.5f)
					continue;

				// the only parent allowed to merge is the parent s itself
				if (child.is_parent && s != i)
					continue;

				childIndices[s_].push_back(i);
			}
		}


		// 4. compute the wL_is and the wL sums
		vector<vector<float>> wL_cache(nComponents);
		vector<float> sumLw(nComponents, 0);
		for (uint s_ = 0; s_ < nParents; ++s_)
		{
			uint s = parentIndices[s_];
			const Component& parent = parentMixture.at(s);

			// iterate over children 
			const vector<uint>& I = childIndices[s_];
			wL_cache[s_].resize(I.size(), 0.0f);
			for (uint i_ = 0; i_ < I.size(); ++i_)
			{
				uint i = I[i_];

				const float maxL = 1e8f;
				const float minL = FLT_MIN;
				//float wL_si = parent.weight * clamp(hemLikelihood(parent, parentMixture.at(i)), minL, maxL);
				float wL_si = parent.weight * clamp(hemLikelihoodOpacity(parentMixture.at(i)), minL, maxL);

				// save likelihood contribution
				wL_cache[s_][i_] = wL_si;
				sumLw[i] += wL_si;
			}
		}


		// 5. compute responsibilities and update
		std::vector<Component> newComponents = std::vector<Component>();
		for (uint s_ = 0; s_ < nParents; ++s_)
		{
			uint s = parentIndices[s_];
			const Component& parent = parentMixture.at(s);
			const vector<uint>& I = childIndices[s_];

			// initialize parent info
			float w_s = 0.0f;
			vec3 summean_i(0, 0, 0);
			vec3 sumcol_i(0, 0, 0);
			smat3 sumcov_i(0, 0, 0, 0, 0, 0);
			vec3 resultant(0, 0, 0);
			FeatureVector sum_featureVector = FeatureVector(featureSize);
			float sum_opacity = 0.0f;
			float nvar = 0.0f;

			// iterate over children and accumulate
			for (uint i_ = 0; i_ < I.size(); ++i_)
			{
				uint i = I[i_];

				if (sumLw[i] == 0.0f)	// can happen
					continue;

				const Component& child = parentMixture.at(i);

				// compute responsibility of parent s for child i
				float r_is = wL_cache[s_][i_] / sumLw[i];
				float w = r_is * child.weight;

				// normal cluster update
				float c_nvar = length(child.nvar);
				vec3 c_normal = child.nvar / c_nvar;

				// flip child normal to be next to the parent normal
				// note that p_normalVar is unnormalized, but thats ok, we're just doing dot-product
				if (dot(c_normal, parent.nvar) < 0.0f)
					c_normal = -c_normal;

				// accumulate
				w_s += w;
				summean_i += w * child.mean;
				sumcol_i += w * child.color;
				sumcov_i += w * (child.cov + smat3::outer(child.mean - parent.mean));	// accumulates generic cov relative to parent mean, numerically more stable than origin, due to smaller distances
				resultant += w * c_normal;
				nvar += w * c_nvar;
				sum_opacity += w * child.opacity;
				sum_featureVector += w * child.featureVector;
			}

			// normalize and condition new cov matrix
			float inv_w = 1.0f / w_s;		// w_s > 0 is certain
			vec3 mean_s = inv_w * summean_i;
			smat3 cov_s = inv_w * sumcov_i - smat3::outer(mean_s - parent.mean);
			//cov_s = conditionCov(cov_s);
			vec3 col_s = inv_w * sumcol_i;
			float opacity_s = inv_w * sum_opacity;
			FeatureVector featureVector_s = inv_w * sum_featureVector;

			// mixture of normals
			float variance1 = nvar * inv_w;			// normalized sum of the variances of the child clusters
			float R = length(resultant);			// resultant length
			float Rmean = R * inv_w;				// mean resultant length
			float variance2 = -2.0f * log(Rmean);	// variance of the child clusters' mean normal vectors with respect to the common mean (outer product thingy)
			vec3  newMeanNormal = resultant / R;	// normalized mean normal vector of new cluster


			// Add new component to output list
			Component newComponent;
			newComponent.mean = mean_s;
			newComponent.cov = cov_s;
			newComponent.weight = w_s;
			newComponent.color = col_s;
			newComponent.opacity = opacity_s;
			newComponent.featureVector = featureVector_s;
			newComponent.nvar = newMeanNormal * (variance1 + variance2);

			newComponents.push_back(newComponent);
		}


		// 6. add orphans, components not addressed by any parent (zero sumLw)
		for (uint i = 0; i < nComponents; ++i)
			if (sumLw[i] == 0.0f)
				newComponents.push_back(parentMixture.at(i));


		// 7. distribute new parent flags to the new component set
		const float parentProbability = 1.0f / hemReductionFactor;
		for (uint i = 0; i < newComponents.size(); ++i)
			newComponents[i].is_parent = rand01() < parentProbability;

		/*for (uint i = 0; i < newComponents.size(); ++i)
		{
			const vec3& mean = newComponents[i].mean;
			const smat3& cov = newComponents[i].cov;
			if (isnan(mean) || det(cov) <= 0 || isnan(det(cov)))
				cerr << "[clusterLevel] Error @ new component " << i << ": mean = " << mean << ", cov = " << cov << ", det = " << det(cov) << endl;
		}*/

		mixtureList.push_back(newComponents);
	}

	void Mixture::initMixture(MixtureLevel &initialMixtureLevel)
	{
		const float parentProbability = 1.0f / hemReductionFactor;

		auto& points = initialMixtureLevel.pointSet;
		auto& colors = initialMixtureLevel.colorSet;
		auto& covariances = initialMixtureLevel.covarianceSet;
		auto& opacities = initialMixtureLevel.opacities;
		std::vector<FeatureVector>& features = initialMixtureLevel.features;
		featureSize = features[0].GetSize();

		initialMixture = std::vector<Component>();
		initialMixture.resize(points.size());
		for (uint i = 0; i < points.size(); ++i)
		{
			const vec3& mean = points[i];
			const vec3& color = colors[i];
			const smat3& covariance = covariances[i];
			const float opacity = opacities[i];
			const FeatureVector feature = features[i];
			Component& c = initialMixture.at(i);


			c.mean = mean;
			c.color = color;
			c.cov = covariance;
			//c.cov = conditionCov(c.cov); Try with and without
			c.opacity = opacity;
			c.featureVector = feature;
			c.weight = 1.0f;


			// Compute the initial normal and set initial normal variance of this point cluster
			// the normal variance is encoded in the length of the normal vector
			vec3 evectors[3];
			c.cov.eigenvectors(evectors);

			// for the initial normal variance, 0.0f should theoretically also work, but since we are encoding the var 
			// in the length of the normal (to save a channel), thats not possible in our implementation
			float initialVar = 0.001f;
			c.nvar = evectors[0] * initialVar;


			// randomly set parent flag
			c.is_parent = rand01() < parentProbability;
		}

	}

	std::vector<MixtureLevel> Mixture::GetResult()
	{
		std::vector<MixtureLevel> resultVector = std::vector<MixtureLevel>();

		for (int level = 0; level < mixtureList.size(); level++)
		{
			
			std::vector<Component> currectComponents = mixtureList.at(level);
			MixtureLevel mixtureLevelCurrent = MixtureLevel();
			auto size = currectComponents.size();
			mixtureLevelCurrent.pointSet.resize(size);
			mixtureLevelCurrent.colorSet.resize(size);
			mixtureLevelCurrent.covarianceSet.resize(size);
			mixtureLevelCurrent.opacities.resize(size);
			mixtureLevelCurrent.features.resize(size);

			std::transform(currectComponents.begin(), currectComponents.end(), mixtureLevelCurrent.pointSet.begin(),
				[](const Component& comp) { return comp.mean; });

			std::transform(currectComponents.begin(), currectComponents.end(), mixtureLevelCurrent.colorSet.begin(),
				[](const Component& comp) { return comp.color; });

			std::transform(currectComponents.begin(), currectComponents.end(), mixtureLevelCurrent.covarianceSet.begin(),
				[](const Component& comp) { return comp.cov; });

			std::transform(currectComponents.begin(), currectComponents.end(), mixtureLevelCurrent.opacities.begin(),
				[](const Component& comp) { return comp.opacity; });

			std::transform(currectComponents.begin(), currectComponents.end(), mixtureLevelCurrent.features.begin(),
				[](const Component& comp) { return comp.featureVector; });

			resultVector.push_back(mixtureLevelCurrent);
		}

		return resultVector;
	}

#pragma endregion

}

