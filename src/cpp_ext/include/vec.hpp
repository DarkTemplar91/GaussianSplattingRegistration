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

#include "base.hpp"
#include <sstream>
#include <iostream>
#include <vector>

namespace hem
{
	#pragma region vec3i
	//--------------------------------------------------------------------------------------
	struct vec3i
	{
		vec3i() { x = y = z = 0; }
		vec3i(int X, int Y, int Z) { x = X; y = Y; z = Z; }
		template<class vec3T> vec3i(const vec3T& rhs) { x = (int)rhs.x; y = (int)rhs.y; z = (int)rhs.z; }

		void operator=(const vec3i& rhs) { x = rhs.x; y = rhs.y; z = rhs.z; }

		bool operator==(const vec3i& rhs) const { return x == rhs.x && y == rhs.y && z == rhs.z; }
		bool operator!=(const vec3i& rhs) const { return x != rhs.x || y != rhs.y || z != rhs.z; }

		int x, y, z;
	};

	inline vec3i operator+(const vec3i& a, const vec3i& b)
	{
		return vec3i(a.x + b.x, a.y + b.y, a.z + b.z);
	}
	inline vec3i operator-(const vec3i& a, const vec3i& b)
	{
		return vec3i(a.x - b.x, a.y - b.y, a.z - b.z);
	}
	inline vec3i operator*(const vec3i& a, int s)
	{
		return vec3i(a.x*s, a.y*s, a.z*s);
	}
	inline vec3i operator*(int s, const vec3i& a)
	{
		return a*s;
	}
	inline vec3i& operator+=(vec3i& a, const vec3i& b)
	{
		a = a + b;
		return a;
	}
	inline vec3i& operator-=(vec3i& a, const vec3i& b)
	{
		a = a - b;
		return a;
	}
	inline vec3i& operator*=(vec3i& a, int s)
	{
		a = a * s;
		return a;
	}
	inline std::ostream& operator<< (std::ostream& os, const vec3i& p)
	{
		os << "(" << p.x << ", " << p.y << ", " << p.z << ")";
		return os;
	}

	inline vec3i min(const vec3i& a, const vec3i& b) { return vec3i(min(a.x, b.x), min(a.y, b.y), min(a.z, b.y)); }
	inline vec3i max(const vec3i& a, const vec3i& b) { return vec3i(max(a.x, b.x), max(a.y, b.y), max(a.z, b.y)); }
	inline vec3i clamp(const vec3i& x, const vec3i& a, const vec3i& b) { return vec3i(clamp(x.x, a.x, b.x), clamp(x.y, a.y, b.y), clamp(x.z, a.z, b.z)); }
	inline vec3i abs(const vec3i& a) { return vec3i(abs(a.x), abs(a.y), abs(a.z)); }
	//--------------------------------------------------------------------------------------
	#pragma endregion

	#pragma region vec3
	//--------------------------------------------------------------------------------------
	struct vec3
	{
		vec3() { x = y = z = 0; }
		vec3(float X, float Y, float Z) { x = X; y = Y; z = Z; }
		vec3(const vec3i& rhs) { x = (float)rhs.x; y = (float)rhs.y; z = (float)rhs.z; }
		vec3(const std::vector<float> vector)
		{
		    if (vector.size() != 3) {
                throw std::runtime_error("Python list must have exactly 3 elements.");
            }
		    x=vector[0];
		    y=vector[1];
		    z=vector[2];
		}

		void operator=(const vec3& rhs) { x = rhs.x; y = rhs.y; z = rhs.z; }

		float x, y, z;
	};

	inline vec3 operator-(const vec3& a)
	{
		return vec3(-a.x, -a.y, -a.z);
	}
	inline vec3 operator+(const vec3& a, const vec3& b)
	{
		return vec3(a.x + b.x, a.y + b.y, a.z + b.z);
	}
	inline vec3 operator-(const vec3& a, const vec3& b)
	{
		return vec3(a.x - b.x, a.y - b.y, a.z - b.z);
	}
	inline vec3 operator*(const vec3& a, float s)
	{
		return vec3(a.x*s, a.y*s, a.z*s);
	}
	inline vec3 operator*(float s, const vec3& a)
	{
		return a*s;
	}
	inline vec3 operator*(const vec3& a, const vec3& b)
	{
		return vec3(a.x*b.x, a.y*b.y, a.z*b.z);
	}
	inline vec3 operator/(const vec3& a, float s)
	{
		float is = 1.0f / s;
		return a * is;
	}
	inline vec3 operator/(const vec3& a, const vec3& b)
	{
		return vec3(a.x / b.x, a.y / b.y, a.z / b.z);
	}
	inline vec3& operator+=(vec3& a, const vec3& b)
	{
		a = a + b;
		return a;
	}
	inline vec3& operator-=(vec3& a, const vec3& b)
	{
		a = a - b;
		return a;
	}
	inline vec3& operator*=(vec3& a, float s)
	{
		a = a * s;
		return a;
	}
	inline vec3& operator/=(vec3& a, float s)
	{
		a = a / s;
		return a;
	}
	inline float dot(const vec3& a, const vec3& b)
	{
		return	a.x*b.x + a.y*b.y + a.z*b.z;
	}
	inline float squaredDist(const vec3& a, const vec3& b)
	{
		vec3 d = a - b;
		return dot(d, d);
	}
	inline float dist(const vec3& a, const vec3& b)
	{
		return sqrt(squaredDist(a, b));
	}
	inline std::ostream& operator<< (std::ostream& os, const vec3& p)
	{
		os << "(" << p.x << ", " << p.y << ", " << p.z << ")";
		return os;
	}
	inline float length(const vec3& v)
	{
		return sqrtf(dot(v, v));
	}
	inline vec3 normalize(const vec3& v)
	{
		return v / length(v);
	}
	inline vec3 cross(const vec3& a, const vec3& b)
	{
		return vec3(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x);
	}

	inline vec3 min(const vec3& a, const vec3& b) { return vec3(fminf(a.x, b.x), fminf(a.y, b.y), fminf(a.z, b.z)); }
	inline vec3 max(const vec3& a, const vec3& b) { return vec3(fmaxf(a.x, b.x), fmaxf(a.y, b.y), fmaxf(a.z, b.z)); }
	inline vec3 clamp(const vec3& x, const vec3& a, const vec3& b) { return vec3(clamp(x.x, a.x, b.x), clamp(x.y, a.y, b.y), clamp(x.z, a.z, b.z)); }
	inline vec3 fabsf(const vec3& a) { return vec3(fabsf(a.x), fabsf(a.y), fabsf(a.z)); }
	//--------------------------------------------------------------------------------------
	#pragma endregion

	#pragma region mat3
	//--------------------------------------------------------------------------------------
	// mat3 class - ROW MAJOR!
	class mat3
	{
		float a[3 * 3];

	public:
		// Default constructor
		mat3()
		{}

		// Initializing constructor
		mat3(float e00, float e01, float e02,
			float e10, float e11, float e12,
			float e20, float e21, float e22)
		{
			a[0] = e00;		a[1] = e01;		a[2] = e02;
			a[3] = e10;		a[4] = e11;		a[5] = e12;
			a[6] = e20;		a[7] = e21;		a[8] = e22;
		}

		// identity matrix
		static mat3 identity()
		{
			return mat3(1, 0, 0, 0, 1, 0, 0, 0, 1 );
		}

		// Copy constructor
		mat3(const mat3& m)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] = m.a[k];
		}

		// Copy constructor with a given array (must have a length >= 4*4)
		mat3(const float* m)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] = m[k];
		}

		// Constructor with an initial value for all elements
		explicit mat3(float w)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] = w;
		}

		float& operator[](int k)
		{
			//ASSERT( (k>=0) && (k<3*3) );
			return a[k];
		}

		const float& operator[](int k) const
		{
			//ASSERT( (k>=0) && (k<3*3) );
			return a[k];
		}

		// Matrix access
		float& operator() (int r, int c)
		{
			//ASSERT( (r>=0) && (c>=0) && (r<4) && (c<4) );
			return a[r * 3 + c];
		}

		const float& operator() (int r, int c) const
		{
			//ASSERT( (r>=0) && (c>=0) && (r<3) && (c<3) );
			return a[r * 3 + c];
		}

		// Dereferencing operator
		operator float* ()
		{
			return a;
		}

		// Constant dereferencing operator
		operator const float* () const
		{
			return a;
		}

		// Assignment operator
		mat3& operator=(const mat3& m)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] = m.a[k];
			return (*this);
		}

		mat3& operator+=(const mat3& m)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] += m.a[k];
			return *this;
		}

		mat3& operator-=(const mat3& m)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] -= m.a[k];
			return *this;
		}

		mat3& operator*=(float w)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] *= w;
			return *this;
		}

		mat3& operator/=(float w)
		{
			for (int k = 0; k < 3 * 3; ++k) a[k] /= w;
			return *this;
		}

		// Matrix Multiplication
		mat3 & operator*=(const mat3& m)
		{
			mat3 result;
			for (int i = 0; i < 3; ++i)
			for (int j = 0; j < 3; ++j)
			{
				float sum(0);
				for (int k = 0; k < 3; k++)
					sum += a[i * 3 + k] * m.a[k * 3 + j];
				result[i * 3 + j] = sum;
			}
			*this = result;
			return *this;
		}


		mat3 operator+(const mat3& m) const
		{
			mat3 res;
			for (int k = 0; k < 3 * 3; ++k) res[k] = a[k] + m.a[k];
			return res;
		}

		mat3 operator-(const mat3& m) const
		{
			mat3 res;
			for (int k = 0; k < 3 * 3; ++k) res[k] = a[k] - m.a[k];
			return res;
		}

		mat3 operator*(float w) const
		{
			mat3 res;
			for (int k = 0; k < 3 * 3; ++k) res[k] = a[k] * w;
			return res;
		}

		mat3 operator/(float w) const
		{
			float invw = 1.0f / w;
			return (*this) * invw;
		}

		// matrix vector product
		vec3 operator*(const vec3& v) const
		{
			return vec3(
				a[0] * v.x + a[1] * v.y + a[2] * v.z,
				a[3] * v.x + a[4] * v.y + a[5] * v.z,
				a[6] * v.x + a[7] * v.y + a[8] * v.z
				);
		}

		// Product of two matrices
		mat3 operator*(const mat3& m) const
		{
			mat3 res;
			for (int i = 0; i < 3; ++i)
			for (int j = 0; j < 3; ++j)
			{
				float sum(0);
				for (int k = 0; k < 3; k++)
					sum += a[i * 3 + k] * m.a[k * 3 + j];
				res[i * 3 + j] = sum;
			}
			return res;
		}

		// Unary -
		mat3 operator-() const
		{
			mat3 res;
			for (int k = 0; k < 3 * 3; ++k) res[k] = -a[k];
			return res;
		}

		// Clear the matrix to zero
		void clear()
		{
			for (int k = 0; k < 3 * 3; ++k)
				a[k] = 0.0f;
		}

		// Transpose matrix
		void transpose()
		{
			float help;
			for (int i = 0; i < 3; ++i)
			for (int j = 0; j < 3; ++j)
			if (i > j)
			{
				help = a[i * 3 + j];
				a[i * 3 + j] = a[j * 3 + i];
				a[j * 3 + i] = help;
			}
		}

		// get i-th row vector
		vec3 row(uint i) const
		{
			return vec3((*this)(i, 0), (*this)(i, 1), (*this)(i, 2));
		}

		// get i-th column vector
		vec3 col(uint i) const
		{
			return vec3((*this)(0, i), (*this)(1, i), (*this)(2, i));
		}

		// outer product a . b^T
		static mat3 outer(const vec3& a, const vec3& b)
		{
			return mat3(a.x*b.x, a.x*b.y, a.x*b.z, a.y*b.x, a.y*b.y, a.y*b.z, a.z*b.x, a.z*b.y, a.z*b.z);
		}
	};

	inline mat3 transpose(mat3 const & m)
	{
		mat3 result = m;
		result.transpose();
		return result;
	}

	inline float det(const mat3& m)
	{
		return	m(0, 0)*m(1, 1)*m(2, 2) + m(0, 1)*m(1, 2)*m(2, 0) + m(0, 2)*m(1, 0)*m(2, 1) -
			m(0, 2)*m(1, 1)*m(2, 0) - m(0, 1)*m(1, 0)*m(2, 2) - m(0, 0)*m(1, 2)*m(2, 1);
	}

	inline mat3 inverse(const mat3& m)
	{
		float d = det(m);
		mat3 r = mat3(
			m(1, 1)*m(2, 2) - m(1, 2)*m(2, 1), m(0, 2)*m(2, 1) - m(0, 1)*m(2, 2), m(0, 1)*m(1, 2) - m(0, 2)*m(1, 1),
			m(1, 2)*m(2, 0) - m(1, 0)*m(2, 2), m(0, 0)*m(2, 2) - m(0, 2)*m(2, 0), m(0, 2)*m(1, 0) - m(0, 0)*m(1, 2),
			m(1, 0)*m(2, 1) - m(1, 1)*m(2, 0), m(0, 1)*m(2, 0) - m(0, 0)*m(2, 1), m(0, 0)*m(1, 1) - m(0, 1)*m(1, 0)
			);
		return r / d;
	}
	//--------------------------------------------------------------------------------------
	#pragma endregion

	#pragma region smat3
	//--------------------------------------------------------------------------------------
	// symmetric 3x3 matrix given by its upper triangle matrix entries
	struct smat3
	{
		float e00, e01, e02, e11, e12, e22;

		smat3() {}

		smat3(float _e00, float _e01, float _e02, float _e11, float _e12, float _e22) :
			e00(_e00), e01(_e01), e02(_e02), e11(_e11), e12(_e12), e22(_e22)
		{}

		// creates a symmetric 3x3 matrix from the upper right triangle matrix entries of the given 3x3 matrix
		smat3(const mat3& mat) :
			e00(mat(0, 0)), e01(mat(0, 1)), e02(mat(0, 2)), e11(mat(1, 1)), e12(mat(1, 2)), e22(mat(2, 2))
		{}

		smat3(const std::vector<float> vector)
		{
		    if (vector.size() != 6) {
                throw std::runtime_error("Python list must have exactly 6 elements.");
            }
		    e00=vector[0];
		    e01=vector[1];
		    e02=vector[2];
		    e11=vector[3];
		    e12=vector[4];
		    e22=vector[5];
		}

		const smat3& operator=(const mat3& mat)
		{
			*this = smat3(mat);
			return *this;
		}

		mat3 toMat3() const
		{
			return mat3(e00, e01, e02, e01, e11, e12, e02, e12, e22);
		}

		smat3 operator+ (const smat3& c) const
		{
			return smat3(e00 + c.e00, e01 + c.e01, e02 + c.e02, e11 + c.e11, e12 + c.e12, e22 + c.e22);
		}

		smat3 operator- (const smat3& c) const
		{
			return smat3(e00 - c.e00, e01 - c.e01, e02 - c.e02, e11 - c.e11, e12 - c.e12, e22 - c.e22);
		}

		smat3 operator* (float s) const
		{
			return smat3(e00*s, e01*s, e02*s, e11*s, e12*s, e22*s);
		}

		smat3 operator/ (float s) const
		{
			float inv_s = 1.0f / s;
			return smat3(e00*inv_s, e01*inv_s, e02*inv_s, e11*inv_s, e12*inv_s, e22*inv_s);
		}

		smat3& operator+= (const smat3& c)
		{
			e00 += c.e00;	e01 += c.e01;	e02 += c.e02;
			e11 += c.e11;	e12 += c.e12;	e22 += c.e22;
			return *this;
		}

		smat3& operator-= (const smat3& c)
		{
			e00 -= c.e00;	e01 -= c.e01;	e02 -= c.e02;
			e11 -= c.e11;	e12 -= c.e12;	e22 -= c.e22;
			return *this;
		}
		smat3& operator*= (float s)
		{
			for (float* e = &e00; e <= &e22; ++e)
				*e *= s;
			return *this;
		}
		smat3& operator/= (float s)
		{
			float inv_s = 1.0f / s;
			return *this *= inv_s;
		}
		vec3 operator* (const vec3& v) const
		{
			return vec3(e00*v.x + e01*v.y + e02*v.z, e01*v.x + e11*v.y + e12*v.z, e02*v.x + e12*v.y + e22*v.z);
		}
		mat3 operator* (const smat3& c) const
		{
			return mat3(
				c.e00*e00 + c.e01*e01 + c.e02*e02, c.e01*e00 + c.e11*e01 + c.e12*e02, c.e02*e00 + c.e12*e01 + c.e22*e02,
				c.e00*e01 + c.e01*e11 + c.e02*e12, c.e01*e01 + c.e11*e11 + c.e12*e12, c.e02*e01 + c.e12*e11 + c.e22*e12,
				c.e00*e02 + c.e01*e12 + c.e02*e22, c.e01*e02 + c.e11*e12 + c.e12*e22, c.e02*e02 + c.e12*e12 + c.e22*e22
				);
		}
		mat3 operator* (const mat3& a) const
		{
			return mat3(a[0] * e00 + a[3] * e01 + a[6] * e02, a[1] * e00 + a[4] * e01 + a[7] * e02, a[2] * e00 + a[5] * e01 + a[8] * e02,
				a[0] * e01 + a[3] * e11 + a[6] * e12, a[1] * e01 + a[4] * e11 + a[7] * e12, a[2] * e01 + a[5] * e11 + a[8] * e12,
				a[0] * e02 + a[3] * e12 + a[6] * e22, a[1] * e02 + a[4] * e12 + a[7] * e22, a[2] * e02 + a[5] * e12 + a[8] * e22);
		}

		// Unary -
		smat3 operator-() const
		{
			return smat3(-e00, -e01, -e02, -e11, -e12, -e22);
		}

		std::string toString() const
		{
			std::stringstream s;
			s << "(" << e00 << ", " << e01 << ", " << e02 << ", " << e11 << ", " << e12 << ", " << e22 << ")";
			return s.str();
		}

		static smat3 identity()
		{
			return smat3(1, 0, 0, 1, 0, 1);
		};

		static smat3 zero()
		{
			return smat3(0, 0, 0, 0, 0, 0);
		}

		static smat3 outer(const vec3& v)
		{
			return smat3 (v.x*v.x, v.x*v.y, v.x*v.z, v.y*v.y, v.y*v.z, v.z*v.z);
		}

		static smat3 diag(const vec3& v)
		{
			return smat3 (v.x, 0, 0, v.y, 0, v.z);
		}

		#pragma region eigenvalue decomposition methods
	private:
		int computeRank(mat3& M, float epsilon = 0) const
		{
			// Compute the maximum magnitude matrix entry.
			float abs, save, max = -1;
			int row, col, maxRow = -1, maxCol = -1;
			for (row = 0; row < 3; row++)
			{
				for (col = row; col < 3; col++)
				{
					abs = fabsf(M(row, col));
					if (abs > max)
					{
						max = abs;
						maxRow = row;
						maxCol = col;
					}
				}
			}
			if (max < epsilon)
			{
				// The rank is 0. The eigenvalue has multiplicity 3.
				return 0;
			}

			// The rank is at least 1. Swap the row containing the maximum-magnitude entry with row 0.
			if (maxRow != 0)
			{
				for (col = 0; col < 3; col++)
				{
					save = M(0, col);
					M(0, col) = M(maxRow, col);
					M(maxRow, col) = save;
				}
			}

			/// Row-reduce the matrix.

			//Scale the row containing the maximum to generate a 1-valued pivot.
			float invMax = 1.0f / M(0, maxCol);
			M(0, 0) *= invMax;
			M(0, 1) *= invMax;
			M(0, 2) *= invMax;

			// Eliminate the maxCol column entries in rows 1 and 2.
			if (maxCol == 0)
			{
				M(1, 1) -= M(1, 0)*M(0, 1);
				M(1, 2) -= M(1, 0)*M(0, 2);
				M(2, 1) -= M(2, 0)*M(0, 1);
				M(2, 2) -= M(2, 0)*M(0, 2);
				M(1, 0) = 0;
				M(2, 0) = 0;
			}
			else if (maxCol == 1)
			{
				M(1, 0) -= M(1, 1)*M(0, 0);
				M(1, 2) -= M(1, 1)*M(0, 2);
				M(2, 0) -= M(2, 1)*M(0, 0);
				M(2, 2) -= M(2, 1)*M(0, 2);
				M(1, 1) = 0;
				M(2, 1) = 0;
			}
			else
			{
				M(1, 0) -= M(1, 2)*M(0, 0);
				M(1, 1) -= M(1, 2)*M(0, 1);
				M(2, 0) -= M(2, 2)*M(0, 0);
				M(2, 1) -= M(2, 2)*M(0, 1);
				M(1, 2) = 0;
				M(2, 2) = 0;
			}

			// Compute the maximum-magnitude entry of the last two rows of the row-reduced matrix.
			max = -1;
			maxRow = -1;
			maxCol = -1;
			for (row = 1; row < 3; row++)
			{
				for (col = 0; col < 3; col++)
				{
					abs = fabsf(M(row, col));
					if (abs > max)
					{
						max = abs;
						maxRow = row;
						maxCol = col;
					}
				}
			}
			if (max < epsilon)
			{
				// The rank is 1. The eigenvalue has multiplicity 2.
				return 1;
			}

			// If row 2 has the maximum-magnitude entry, swap it with row 1.
			if (maxRow == 2)
			{
				for (col = 0; col < 3; col++)
				{
					save = M(1, col);
					M(1, col) = M(2, col);
					M(2, col) = save;
				}
			}
			// Scale row 1 to generate a 1-valued pivot.
			invMax = 1 / M(1, maxCol);
			M(1, 0) *= invMax;
			M(1, 1) *= invMax;
			M(1, 2) *= invMax;

			// The rank is 2. The eigenvalue has multiplicity 1.
			return 2;
		}

		void getComplement2(vec3 u, vec3& v, vec3& w) const
		{
			u = normalize(u);
			if (fabsf(u.x) >= fabsf(u.y))
			{
				float invLength = 1.0f / sqrt(u.x*u.x + u.z*u.z);
				v.x = -u.z*invLength;
				v.y = 0.0f;
				v.z = u.x*invLength;
				w.x = u.y*v.z;
				w.y = u.z*v.x - u.x*v.z;
				w.z = -u.y*v.x;
			}
			else
			{
				float invLength = 1.0f / sqrt(u.y*u.y + u.z*u.z);
				v.x = 0.0f;
				v.y = u.z*invLength;
				v.z = -u.y*invLength;
				w.x = u.y*v.z - u.z*v.y;
				w.y = -u.x*v.z;
				w.z = u.x*v.y;
			}
		}

	public:
		// returns the eigenvalues in the elements x,y,z of a vec3 in ascending order
		vec3 eigenvalues() const
		{
			const double inv3 = 0.33333333333333333333333333333333;
			const double root3 = 1.7320508075688772935274463415059;

			double c0 = e00*e11*e22 + 2 * e01*e02*e12 - e00*e12*e12 - e11*e02*e02 - e22*e01*e01;
			double c1 = e00*e11 - e01*e01 + e00*e22 - e02*e02 + e11*e22 - e12*e12;
			double c2 = e00 + e11 + e22;
			double c2Div3 = c2*inv3;
			double aDiv3 = c1*inv3 - c2Div3*c2Div3;
			if (aDiv3 > 0.0) aDiv3 = 0.0;
			double mbDiv2 = 0.5*c0 + c2Div3*c2Div3*c2Div3 - 0.5*c2Div3*c1;
			double q = mbDiv2*mbDiv2 + aDiv3*aDiv3*aDiv3;		// Note: This line produces an inexact result.
			if (q > 0.0) q = 0.0;
			double magnitude = sqrt(-aDiv3);
			double angle = atan2(sqrt(-q), mbDiv2)*inv3;
			if (angle != angle) angle = 0.0;					// check for NAN. Can happen if q == 0 && mbDiv2 == 0. Although atan2(0,0) does return 0!
			double sn, cs;
			sn = sin(angle);
			cs = cos(angle);

			double evalues[3];
			evalues[0] = c2Div3 + 2 * magnitude*cs;
			evalues[1] = c2Div3 - magnitude*(cs + root3*sn);
			evalues[2] = c2Div3 - magnitude*(cs - root3*sn);

			// Sort eigenvalues in ascending order
			double h;
			if (evalues[2] < evalues[1]) { h = evalues[1];  evalues[1] = evalues[2];  evalues[2] = h; }
			if (evalues[1] < evalues[0]) { h = evalues[0];  evalues[0] = evalues[1];  evalues[1] = h; }
			if (evalues[2] < evalues[1]) { h = evalues[1];  evalues[1] = evalues[2];  evalues[2] = h; }
			return vec3(float(evalues[0]), float(evalues[1]), float(evalues[2]));
		}

		// returns the eigenvalues in the elements x,y,z of out_evalues in ascending order, and their associated eigenvectors in out_evectors
		void eigensystem(vec3& out_evalues, vec3 out_evectors[3]) const
		{
			// condition matrix by normalizing by element of largest magnitude
			float emax = 0;
			for (const float *eptr = &e00; eptr != &e22 + 1; ++eptr)
				if (fabsf(*eptr) > emax)
					emax = fabsf(*eptr);
			smat3 cn = (*this) / emax;

			vec3 evalues;				// pivoted eigen values
			float eps = 2 * FLT_MIN;	// Note: if epsilon is zero, small numeric instabilities can pretty fast result in a false rank-estimation, which can result in bad eigenvectors
			{
				evalues = cn.eigenvalues();

				// Compute eigenvectors
				mat3 M(cn.e00 - evalues.x, cn.e01, cn.e02, cn.e01, cn.e11 - evalues.x, cn.e12, cn.e02, cn.e12, cn.e22 - evalues.x);

				int rank0 = computeRank(M, eps);
				if (rank0 == 0)
				{
					// evalue[0] = evalue[1] = evalue[2]
					out_evectors[0] = vec3(1, 0, 0);
					out_evectors[1] = vec3(0, 1, 0);
					out_evectors[2] = vec3(0, 0, 1);
				}
				else if (rank0 == 1 || evalues.x == evalues.y)			// EXPERIMENTAL: The term right of the OR
				{
					// evalue[0] = evalue[1] < evalue[2]
					getComplement2(normalize(M.row(0)), out_evectors[0], out_evectors[1]);
					out_evectors[2] = cross(out_evectors[0], out_evectors[1]);
				}
				else	// rank0 == 2
				{
					out_evectors[0] = normalize(cross(normalize(M.row(0)), normalize(M.row(1))));
					M = mat3(cn.e00 - evalues.y, cn.e01, cn.e02, cn.e01, cn.e11 - evalues.y, cn.e12, cn.e02, cn.e12, cn.e22 - evalues.y);

					int rank1 = computeRank(M, eps);
					if (rank1 == 1)
					{
						// evalue[0] < evalue[1] = evalue[2]
						getComplement2(out_evectors[0], out_evectors[1], out_evectors[2]);
					}
					else
					{
						// evalue[0] < evalue[1] < evalue[2]
						out_evectors[1] = normalize(cross(M.row(0), M.row(1)));
						out_evectors[2] = cross(out_evectors[0], out_evectors[1]);
					}
				}
			}
			// scale back to obtain proper eigenvalues
			out_evalues = evalues * emax;
		}

		void eigensystem(vec3& out_evalues, mat3& out_evectors) const
		{
			vec3 evecs[3];
			eigensystem(out_evalues, evecs);
			out_evectors = mat3(
				evecs[0].x, evecs[1].x, evecs[2].x,
				evecs[0].y, evecs[1].y, evecs[2].y,
				evecs[0].z, evecs[1].z, evecs[2].z
				);
		}

		void eigenvectors(vec3 out_evectors[3]) const
		{
			vec3 evalues;
			eigensystem(evalues, out_evectors);
		}

		mat3 eigenvectors() const
		{
			vec3 evecs[3];
			eigenvectors(evecs);
			return mat3(
				evecs[0].x, evecs[1].x, evecs[2].x,
				evecs[0].y, evecs[1].y, evecs[2].y,
				evecs[0].z, evecs[1].z, evecs[2].z
			);
		}

		#pragma endregion
	};

	#pragma region smat3	non-member operators

	inline smat3 operator* (float s, const smat3& cov)
	{
		return cov * s;
	}

	inline float det(const smat3& c)
	{
		return -c.e02*c.e02*c.e11 + 2 * c.e01*c.e02*c.e12 - c.e00*c.e12*c.e12 - c.e01*c.e01*c.e22 + c.e00*c.e11*c.e22;
	}

	inline smat3 inverse(const smat3& c)
	{
		smat3 r(c.e11*c.e22 - c.e12*c.e12, c.e02*c.e12 - c.e01*c.e22, c.e01*c.e12 - c.e02*c.e11, c.e00*c.e22 - c.e02*c.e02, c.e02*c.e01 - c.e00*c.e12, c.e00*c.e11 - c.e01*c.e01);
		return r / det(c);
	}

	inline float trace(const smat3& c)
	{
		return c.e00 + c.e11 + c.e22;
	}
	
	inline std::ostream& operator<< (std::ostream& os, const smat3& cov)
	{
		return (os << cov.toString());
	}

	inline mat3 operator* (const mat3& m, const smat3& sm)
	{
		mat3 res;
		for (uint r = 0; r < 3; ++r)
		{
			res(r, 0) = m(r, 0)*sm.e00 + m(r, 1)*sm.e01 + m(r, 2)*sm.e02;
			res(r, 1) = m(r, 0)*sm.e01 + m(r, 1)*sm.e11 + m(r, 2)*sm.e12;
			res(r, 2) = m(r, 0)*sm.e02 + m(r, 1)*sm.e12 + m(r, 2)*sm.e22;
		}
		return res;
	}

	inline mat3 operator+ (const smat3& sm, const mat3& m)
	{
		return sm.toMat3() + m;
	}

	inline mat3 operator+ (const mat3& m, const smat3& sm)
	{
		return m + sm.toMat3();
	}

	inline mat3 operator- (const smat3& sm, const mat3& m)
	{
		return sm.toMat3() - m;
	}

	inline mat3 operator- (const mat3& m, const smat3& sm)
	{
		return m - sm.toMat3();
	}

	#pragma endregion

	//--------------------------------------------------------------------------------------
	#pragma endregion

	#pragma region general functions
	//--------------------------------------------------------------------------------------
	inline bool isnan(float v) { return v != v; }
	inline bool isnan(const vec3& v) { return v.x != v.x || v.y != v.y || v.z != v.z; }
	
	//--------------------------------------------------------------------------------------
	#pragma endregion

}	// end namespace cp
