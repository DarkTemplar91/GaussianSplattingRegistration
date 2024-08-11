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


namespace hem
{
	typedef std::vector<vec3>  PointSet;
	typedef std::vector<vec3>  ColorSet;
	typedef std::vector<smat3> CovarianceSet;

}	/// end namespace cp

