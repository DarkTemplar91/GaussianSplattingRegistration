# GaussianSplattingRegistration


A software used for global and local registration of Gaussian point clouds produced via 3D Gaussian Splatting.
![image](https://github.com/user-attachments/assets/19116670-261b-41a7-9e43-3a54214f8728)


### You can:
* Load sparse, gaussian and Open3D format point clouds for registration.
* Set their transformation matrix by hand.
* Use global or local registration for their alignment.
* Multiscale (Coarse-to-Fine) registration using voxel based downscaling and Gaussian Mixtures.
* Downsaple the Gaussian Splats using a Hierarchical Expectation Maximization (Gaussian Mixtures).
* Merge two Gaussian point clouds together.
* Visualize them via the default viewport in point cloud form or use the rasterizer for displaying gaussian point clouds.
* Evaluate the registration results.

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
    - For further information, please refer to the [Open3D documentation](https://www.open3d.org/docs/0.16.0/).
4. Click start registration.
5. Repeat the steps if necessary
6. If needed, merge the point clouds.
    - If the point clouds loaded are not Gaussian point clouds, you can select their corresponding point clouds and merge them using the transformation acquired via the registration.

Initial | Global registration | Local registration
:-------------------------:|:-------------------------:|:-------------------------:
![initial](https://github.com/user-attachments/assets/83c2f299-2bce-465a-90d5-8964e95eba3e) |  ![registered_global](https://github.com/user-attachments/assets/317b54f6-fba6-43f8-bdf4-3110cfe3cff0) | ![registered_local](https://github.com/user-attachments/assets/d18c13d8-89ed-4a72-92dc-b856954952c6)
![initial_rast](https://github.com/user-attachments/assets/783c3443-81aa-4cf6-aff7-cfe7fd207d61) | ![global_rast](https://github.com/user-attachments/assets/b4ea96f0-2472-4a49-8d34-06f35fdfa9aa) | ![local_rast](https://github.com/user-attachments/assets/1d64ac03-9bad-49ef-9634-5dbb9cc5ef61)



  
### Coarse-to-Fine registration using Gaussian Mixtures
The loaded Gaussian Splats can be dowscaled using the HEM method. This hopefully better preserves the underlying structure of the scene, as opposed to basic downscaling/sampling.
The steps are the following:
1. Load your point clouds.
2. Run the Gaussian Mixture downsampler in the "Mixture" tab.
    - You can select the "cluster level", i.e., the number of Gaussian Mixtures that will be created.
    - Geometric and color distances to evaluate the similarity between splats.
    - HEM reduction factor, which is the multiplicative inverse of the probability of a point being included in the downsampled point cloud.
3. Wait until the mixtures are created. (It may take a long time, depending on the hardware and the point clouds loaded.)
4. Head to the "Multiscale" tab:
   - Set the "downscale type" to "HEM Gaussian Mixture"
   - Set the iteration and correspondence values.
   - Set any other arguments as needed.
5. Run the registration by clicking on the start button.
6. You can change the current mixture level loaded by using the slider.

![lego_gif](https://github.com/user-attachments/assets/348ce0e9-ff1d-4ef5-8fc5-7c7cee165d55)


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
It was tested on CUDA 12.1 and pytorch 2.1, but it should work with other configurations as well.
```
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

Install all other requirements
```
pip install -r requirements.txt
```

For the rasterization to work, we have to install the gaussian rasterisation package from the original paper.\
For this, you should run the following command:
```
pip install .\src\submodules\diff-gaussian-rasterization\
```
Then finally, we have to compile the C++ files. This will allow us to use the HEM downsampler:
```
python setup.py build_ext --inplace
```
This was tested with MSVC and as such, the compiler arguments are also given in the appropriate format. If you use a different compiler, you may need to replace the arguments.

## References
The repository makes great use of the following repositories and libraries.
* 3D Gaussian Splatting for Real-Time Radiance Field Rendering
	* Webpage: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
	* Repository: https://github.com/graphdeco-inria/gaussian-splatting
* Open3D:
	* Webpage: http://www.open3d.org/
	* Repository: https://github.com/isl-org/Open3D
 * HEM/Gaussian Mixtures:
	* HEM algorithm as outlined in the following paper: https://www.cg.tuwien.ac.at/research/publications/2014/preiner2014clop/
 	* Likelihood function: https://repo-sam.inria.fr/fungraph/hierarchical-3d-gaussians/

## Known issues
* The legacy Open3D pipeline does not support callbacks, so few of the loading widgets provide no information.
* There are some issues when calculating the Aligned Axis Bounding Box, so the "copy current view" button could yield some values that differ from the real ones.
* The GUI was only tested on 1080p displays. It does not scale well for other resolutions. (WIP)
* For larger scenes, the HEM downsampler becomes extremely slow.
* The HEM downsampler does not handle the ill-formed (non-positive-definite) covariance matrices properly.
* Converting point clouds to the Open3D format takes too much time.

## Planned features
* GUI rehaul (Migrate to PySide6, make application responsive etc.)
* Migrate to different rasterizer
* Full Gaussian Splatting viewer integration
* Train Gaussian Splats in the application
* Improve the merging of Gaussian Splats: Post-processing, cleanup, possibly addition training passes.

## App gallery
|   |   |
:-------------------------:|:-------------------------:
![registration_mixture](https://github.com/user-attachments/assets/044a7f58-c389-453f-aed7-5dd623d48e7c) | ![bonsai_render](https://github.com/user-attachments/assets/02d13013-bb04-44e1-b6dc-131b7fac1755)
![carla_sparse_clouds](https://github.com/user-attachments/assets/c34e951c-e70c-4d3f-a7d5-d35dd275ac4e) | ![application_screenshot](https://github.com/user-attachments/assets/49ef63c7-88ae-40a7-846d-6b8659e05df3)




