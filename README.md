# GaussianSplattingRegistration


A software used for global and local registration of Gaussian point clouds produced via 3D Gaussian Splatting.

### You can:
* Load sparse, gaussian and Open3D format point clouds for registration.
* Set their transformation matrix by hand.
* Use global or local registration for their alignment.
* Merge two Gaussian point clouds together.
* Visualize them via the default viewport in point cloud form or use the rasterizer for displaying gaussian point clouds.

There are three distinct types of point clouds supported. In the GUI application the following terms are used:
* Sparse point cloud: The input point cloud used for the gaussian training. (Usually made from the points3D.txt)
* Input point cloud/Gaussian point cloud: The input that should be used for the registration. It must be the point cloud created by the Gaussian splatting
* Cached point cloud: The converted point clouds created either from the sparse or gaussian inputs. Technically, it could also be any Open3D supported point clouds as well.

### How to register point clouds:
1. Load your point clouds.
2. Set up your view, using the visualizer.
    - You can set debug colors for the point cloud
    - Set up the view by hand or by using the "Copy current view" option
3. At the registration group, you can select the registration type and their corresponding arguments.
4. Click start registration.
5. Repeat the steps if necessary
6. If needed, merge the point clouds.
    - If the point clouds loaded are not Gaussian point clouds, you can select their corresponding point clouds and merge them using the transformation acquired via the registration.


## Installation
Clone the repository
```
git clone --recursive https://github.com/DarkTemplar91/GaussianSplattingRegistration.git
cd GaussianSplattingRegistration
```

I recommend using conda for the creation of the virtual environment:

```
conda create -n GaussianSplattingRegistration python=3.10
conda activate GaussianSplattingRegistration
```

The next step is installing pytorch. Please refer to https://pytorch.org/get-started/locally/ for further information\
It was tested on CUDA 12.1 and pytorch 2.1, but it should work with other configuration as well.
```
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

Install all other requirements
```
pip install -r requirements.txt
```

The next step is optional.\
If you wish to use the rasterization feature, run the following command:
```
pip install .\src\submodules\diff-gaussian-rasterization\
```

## References
The repository makes great use of the following repositories and libraries.
* 3D Gaussian Splatting for Real-Time Radiance Field Rendering
	* Webpage: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
	* Repository: https://github.com/graphdeco-inria/gaussian-splatting
* Open3D:
	* Webpage: http://www.open3d.org/
	* Repository: https://github.com/isl-org/Open3D
