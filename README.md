# GaussianSplattingRegistration

A software used for global and local registration of Gaussian point clouds produced via 3D Gaussian Splatting.

### You can:
* Load sparse, gaussian and Open3D format point clouds for registration.
* Set their transformation matrix by hand.
* Use global or local registration for their alignment.
* Merge two Gaussian point clouds together.

There are three distinct types of point clouds supported. In the GUI application teh following terms are used:
* Sparse point cloud: The input point cloud used for the gaussian training. (Usually made from the points3D.txt)
* Input point cloud: The input that should be used for the registration. It must be the point cloud created by the Gaussian splatting
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
