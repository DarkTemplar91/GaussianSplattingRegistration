import plyfile
import os.path

from point_cloud_converter import convert_input_pc_to_open3d_pc, convert_pc_to_open3d_pc


def load_sparse_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    # TODO: Check point cloud type, if wrong, early return

    return convert_input_pc_to_open3d_pc(point_cloud_plyfile)


# TODO: Add tracing
def load_gaussian_pc(pc_path):
    if not os.path.isfile(pc_path):
        return None

    point_cloud_plyfile = plyfile.PlyData.read(pc_path)

    return convert_pc_to_open3d_pc(point_cloud_plyfile)
