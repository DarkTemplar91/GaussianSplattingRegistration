#include "pointindex.hpp"

namespace hem
{
#pragma region PointIndex::cellHasher

	PointIndex::cellHasher::cellHasher(){}
	
	size_t PointIndex::cellHasher::operator()(const vec3i& x) const
	{
		return std::hash<uint>()(x.x) ^ std::hash<uint>()(x.y) ^ std::hash<uint>()(x.z);
	}

	bool PointIndex::cellHasher::operator()(const vec3i& left, const vec3i& right)
	{
		if (left.x != right.x)	return left.x < right.x;
		if (left.y != right.y)	return left.y < right.y;
		return left.z < right.z;
	}
#pragma endregion

#pragma region PointIndex::gridCoordPred

	PointIndex::gridCoordPred::gridCoordPred(const std::vector<vec3>& points, const vec3& bbMin, float cellSize, const vec3i& gridSize)
		: mPoints(&points), mBBmin(bbMin), mCellSize(cellSize), mMaxGridCoord(gridSize - vec3i(1, 1, 1))
	{}

	bool PointIndex::gridCoordPred::operator()(const uint& a, const uint& b)
	{
		cellHasher hasher;
		vec3i aIndex = min(vec3i(((*mPoints)[a] - mBBmin) / mCellSize), mMaxGridCoord);
		vec3i bIndex = min(vec3i(((*mPoints)[b] - mBBmin) / mCellSize), mMaxGridCoord);
		return hasher(aIndex, bIndex);
	}

#pragma endregion

#pragma region PointIndex::distancePred

	PointIndex::distancePred::distancePred(const std::vector<vec3>* points, const vec3& queryPoint) : mPoints(points), mQueryPoint(queryPoint) {}

	bool PointIndex::distancePred::operator()(const uint& a, const uint& b)
	{
		return squaredDist(mQueryPoint, (*mPoints)[a]) < squaredDist(mQueryPoint, (*mPoints)[b]);
	}
#pragma endregion

#pragma region PointIndex

	PointIndex::PointIndex(const std::vector<vec3>& points, float maxSearchRadius)
	{
		create(points, maxSearchRadius);
	}

	void PointIndex::create(const std::vector<vec3>& points, float maxSearchRadius)
	{
		assert(!points.empty());	// can't create index on empty set

		mGrid.clear();
		mPoints = &points;

		// compute bounding box (with epsilon space border)
		mBBmin = vec3(FLT_MAX, FLT_MAX, FLT_MAX);
		mBBmax = vec3(-FLT_MAX, -FLT_MAX, -FLT_MAX);
		for (std::vector<vec3>::const_iterator p = points.begin(); p != points.end(); ++p)
		{
			const vec3 pt = *p;
			mBBmin = min(mBBmin, pt);
			mBBmax = max(mBBmax, pt);
		}

		// create dim cells of size maxSearchRadius, and adapt bbox
		mCellSize = maxSearchRadius;
		mBBsize = mBBmax - mBBmin;
		mGridSize = vec3i(mBBsize / mCellSize) + vec3i(1, 1, 1);
		mBBsize = vec3(mGridSize) * mCellSize;
		vec3 halfSize = mBBsize * 0.5;
		vec3 center = (mBBmax + mBBmin) * 0.5f;
		mBBmin = center - halfSize;
		mBBmax = center + halfSize;


		// create point index buffer sorted by their grid coordinates
		std::vector<uint> indices(points.size());
		for (uint i = 0; i < indices.size(); ++i) indices[i] = i;
		std::sort(indices.begin(), indices.end(), gridCoordPred(points, mBBmin, mCellSize, mGridSize));


		// populate grid
		std::vector<uint> currentList;
		vec3i currentGridCoord = getGridCoord(points[indices[0]]);
		for (std::vector<uint>::iterator it = indices.begin(); it != indices.end(); ++it)
		{
			// next point index and associate gridCoord
			uint i = *it;
			vec3i gridCoord = getGridCoord(points[i]);

			// if we have a new gridCoord, finish current cell at currentGridCoord first
			if (gridCoord != currentGridCoord)
			{
				mGrid[currentGridCoord] = currentList;
				currentList.clear();
				currentGridCoord = gridCoord;
			}
			currentList.push_back(i);
		}
		mGrid[currentGridCoord] = currentList;		// finish index list for last cell
	}

	void PointIndex::annSearch(const vec3& queryPoint, uint k, std::vector<uint>& outIndices)
	{
		outIndices.clear();
		radiusSearch(queryPoint, sqrtf(12 * mCellSize * mCellSize), outIndices);
		// sort by distance
		std::sort(outIndices.begin(), outIndices.end(), distancePred(mPoints, queryPoint));
		// remove any indices beyond k
		outIndices.erase(outIndices.begin() + min(k, outIndices.size()), outIndices.end());
	}

	void PointIndex::radiusSearch(const vec3& queryPoint, float radius, std::vector<uint>& outIndices)
	{
		outIndices.clear();
		vec3i c = getGridCoord(queryPoint);

		// visit each neighbor cell and process points in there
		for (uint i = 0; i < 27; ++i)
		{
			// find n in the hash grid
			vec3i n = c + neighborOffsets[i];
			if (mGrid.find(n) != mGrid.end())
			{
				const std::vector<uint>& indices = mGrid[n];

				// search point list of neighbor cell for in-range points
				for (std::vector<uint>::const_iterator it = indices.begin(); it != indices.end(); ++it)
				{
					uint i = *it;
					if (squaredDist(queryPoint, (*mPoints)[i]) < radius * radius)
						outIndices.push_back(i);
				}
			}
		}
	}

	void PointIndex::radiusSearch(const std::vector<vec3>& queryPoints, float radius, std::vector<std::vector<uint>> outIndices)
	{
		outIndices.resize(queryPoints.size());
		for (uint i = 0; i < queryPoints.size(); ++i)
			radiusSearch(queryPoints[i], radius, outIndices[i]);
	}

	void PointIndex::radiusSearch(const std::vector<vec3>& queryPoints, const std::vector<float>& radii, std::vector<std::vector<uint>> outIndices)
	{
		assert(queryPoints.size() == radii.size());

		outIndices.resize(queryPoints.size());
		for (uint i = 0; i < queryPoints.size(); ++i)
			radiusSearch(queryPoints[i], radii[i], outIndices[i]);
	}

#pragma endregion



}