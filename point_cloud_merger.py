import numpy as np
import plyfile


def merge_point_clouds(pc1, pc2, output_path, transformation_matrix=None):
    vertex_data1 = pc1["vertex"].data
    vertex_data2 = pc2["vertex"].data

    # calculate the new positions for the transformation if needed
    if transformation_matrix is not None:
        points = np.vstack([vertex_data2['x'], vertex_data2['y'], vertex_data2['z'], np.ones(len(vertex_data2['x']))]).T
        transformed_points = np.dot(transformation_matrix, points.T).T[:, :3]

        # Update the coordinates in the PLY data
        vertex_data2['x'] = transformed_points[:, 0]
        vertex_data2['y'] = transformed_points[:, 1]
        vertex_data2['z'] = transformed_points[:, 2]

    out_vertex_data = np.concatenate([vertex_data1, vertex_data2])
    out_vertex_element = plyfile.PlyElement.describe(out_vertex_data, "vertex", len_types={}, val_types={}, comments=[])
    out_ply_data = plyfile.PlyData(text=False,  # binary
                                   byte_order='<',  # < stands for little endian
                                   elements=[out_vertex_element])
    plyfile.PlyData.write(out_ply_data, output_path)
