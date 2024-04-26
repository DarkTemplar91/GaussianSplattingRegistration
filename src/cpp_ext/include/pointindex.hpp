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

#include "vec.hpp"
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cassert>


namespace hem
{
	// index offsets for neighbor cells in a grid
	static const vec3i neighborOffsets[27] = {
		vec3i(-1, -1, -1), vec3i(0, -1, -1), vec3i(1, -1, -1),
		vec3i(-1, 0, -1), vec3i(0, 0, -1), vec3i(1, 0, -1),
		vec3i(-1, 1, -1), vec3i(0, 1, -1), vec3i(1, 1, -1),
		vec3i(-1, -1, 0), vec3i(0, -1, 0), vec3i(1, -1, 0),
		vec3i(-1, 0, 0), vec3i(0, 0, 0), vec3i(1, 0, 0),
		vec3i(-1, 1, 0), vec3i(0, 1, 0), vec3i(1, 1, 0),
		vec3i(-1, -1, 1), vec3i(0, -1, 1), vec3i(1, -1, 1),
		vec3i(-1, 0, 1), vec3i(0, 0, 1), vec3i(1, 0, 1),
		vec3i(-1, 1, 1), vec3i(0, 1, 1), vec3i(1, 1, 1)
	};



	// primitive 3D hash grid
	class PointIndex
	{
	private:
		// hash function for a vec3i
		struct cellHasher
		{
			static const size_t bucket_size = 10;	// mean bucket size that the container should try not to exceed
			static const size_t min_buckets = 1204;	// minimum number of buckets, power of 2, >0

			cellHasher();

			size_t operator()(const vec3i& x) const;
			bool operator()(const vec3i& left, const vec3i& right);
		};

		typedef std::unordered_map<vec3i, std::vector<uint>, cellHasher> HashGrid;


		HashGrid mGrid;
		const std::vector<vec3>* mPoints;
		vec3 mBBmin;
		vec3 mBBmax;
		vec3 mBBsize;		// world space dimensions
		vec3i mGridSize;	// grid dimensions
		float mCellSize;


	private:
		struct gridCoordPred
		{
			vec3 mBBmin;
			float mCellSize;
			vec3i mMaxGridCoord;
			const std::vector<vec3>* mPoints;

			gridCoordPred(const std::vector<vec3>& points, const vec3& bbMin, float cellSize, const vec3i& gridSize);

			/// compares ordering of indices based on the grid coordinate of their associating points
			bool operator()(const uint& a, const uint& b);
		};

		struct distancePred
		{
			vec3 mQueryPoint;
			const std::vector<vec3>* mPoints;

			distancePred(const std::vector<vec3>* points, const vec3& queryPoint);

			bool operator()(const uint& a, const uint& b);
		};

	public:

		PointIndex(const std::vector<vec3>& points, float maxSearchRadius);
		void create(const std::vector<vec3>& points, float maxSearchRadius);


		// retrieve grid coordinates of point p
		inline vec3i getGridCoord(const vec3& p)
		{
			return min(vec3i((p - mBBmin) / mCellSize), mGridSize - vec3i(1, 1, 1));
		}

		// retrieve the side length of a grid cell. This equals the maximum reliable search radius
		inline float cellSize()
		{
			return mCellSize;
		}


		// approximate k nearest neighbor search within a maximum radius of mCellSize.
		// if a neighbor's distance is not within the 3x3x3 neighboring cells, it is not returned.
		// all previous content in outIndices will be cleared.
		void annSearch(const vec3& queryPoint, uint k, std::vector<uint>& outIndices);

		// queries all indices within a radius ball around queryPoint and write them to the vector outIndices
		// all previous content in outIndices will be cleared.
		void radiusSearch(const vec3& queryPoint, float radius, std::vector<uint>& outIndices);

		// radius search for a list of queryPoints with common radius.
		// all previous content in outIndices will be cleared.
		void radiusSearch(const std::vector<vec3>& queryPoints, float radius, std::vector<std::vector<uint>> outIndices);


		// radius search for a list of queryPoints with individual radii.
		// all previous content in outIndices will be cleared.
		void radiusSearch(const std::vector<vec3>& queryPoints, const std::vector<float>& radii, std::vector<std::vector<uint>> outIndices);

	};	/// class PointIndex


}	/// end namespace cp
