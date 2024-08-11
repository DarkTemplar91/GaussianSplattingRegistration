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

#include <cstdlib>

namespace hem
{
	typedef unsigned int uint;
	
	//--------------------------------------------------------------------------------------
	
	inline float fabsf(float a) { return a < 0 ? -a : a; }
	inline float fminf(float a, float b) { return a < b ? a : b; }
	inline float fmaxf(float a, float b) { return a > b ? a : b; }
	inline float lerp(float a, float b, float t)  { return a + t*(b - a); }
	inline float clamp(float f, float a, float b) { return fmaxf(a, fminf(f, b)); }

	#undef max
	#undef min
	inline int abs(int a) { return a < 0 ? -a : a; }
	inline int max(int a, int b) { return a > b ? a : b; }
	inline int min(int a, int b) { return a < b ? a : b; }
	inline int clamp(int f, int a, int b) { return max(a, min(f, b)); }
	inline uint max(uint a, uint b) { return a > b ? a : b; }
	inline uint min(uint a, uint b) { return a < b ? a : b; }
	inline uint clamp(uint f, uint a, uint b) { return max(a, min(f, b)); }
	inline float max(float a, float b) { return a > b ? a : b; }

	//--------------------------------------------------------------------------------------


	/// returns a 32bit random unsigned integer
	inline uint rand()
	{
		uint r = 0;
		for (int i = 0; i < 8; ++i)
			r |= (std::rand() % 16) << (4 * i);
		return r;
	}

	/// returns a normalized random float in intervall [0,1)
	inline float rand01()
	{
		return float(hem::rand()) / uint(0xffffffff);
	}

	/// returns a normalized random float in intervall [0,1)
	inline float rand(float rangeMin, float rangeMax)
	{
		return rangeMin + rand01() * (rangeMax - rangeMin);
	}

}	/// end namespace cp
