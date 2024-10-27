import open3d as o3d
import numpy as np
import torch


def fit_plane(point_cloud: o3d.geometry.PointCloud, iterations, threshold, min_sample_distance):
    points_tensor = torch.from_numpy(np.array(point_cloud.points, dtype=np.float32))

    best_plane = None
    max_inliers_count = 0
    best_inliers = None
    for _ in range(iterations):
        sampled_indices = sample_random_points(points_tensor, min_sample_distance)
        sampled_points = points_tensor[sampled_indices]

        p1, p2, p3 = sampled_points[0], sampled_points[1], sampled_points[2]
        normal = torch.cross(p2 - p1, p3 - p1, dim=0)
        normal /= normal.norm()
        d = -torch.dot(normal, p1)

        plane = np.hstack((normal.numpy(), d.numpy()))

        _, distances = project_point_onto_plane(points_tensor, plane)

        inliers_indices = (torch.abs(distances) < threshold).nonzero(as_tuple=True)[0]
        inliers_count = inliers_indices.size(0)

        if inliers_count > max_inliers_count:
            max_inliers_count = inliers_count
            best_plane = plane
            best_inliers = inliers_indices.numpy()

    return best_plane, points_tensor[best_inliers], best_inliers


def sample_random_points(points: torch.Tensor, min_distance: float) -> torch.Tensor:
    num_points = points.shape[0]

    def is_distant_enough(selected_points, candidate):
        distances = torch.norm(selected_points - candidate, dim=1)
        return torch.all(distances >= min_distance)

    selected_indices = []
    first_index = torch.randint(0, num_points, (1,)).item()
    selected_indices.append(first_index)

    while len(selected_indices) < 3:
        candidate_index = torch.randint(0, num_points, (1,)).item()
        candidate_point = points[candidate_index]
        selected_points = points[selected_indices]

        if is_distant_enough(selected_points, candidate_point):
            selected_indices.append(candidate_index)

    return torch.tensor(selected_indices)


def project_point_onto_plane(points, plane):
    a, b, c, d = plane
    normal = torch.tensor([a, b, c], dtype=torch.float32)
    normal = normal / normal.norm()

    distances = (torch.mm(points, normal.unsqueeze(1)).squeeze() + d) / normal.norm()

    projected_points = points - distances.unsqueeze(1) * normal
    return projected_points, distances


def get_o3d_plane(plane_coefficients, points_tensor, resolution=10):
    a, b, c, d = plane_coefficients

    min_point = points_tensor.min(dim=0).values
    max_point = points_tensor.max(dim=0).values
    x = torch.linspace(min_point[0], max_point[0], resolution)
    y = torch.linspace(min_point[1], max_point[1], resolution)
    x, y = torch.meshgrid(x, y, indexing="xy")

    # Calculate z using the plane equation z = -(a*x + b*y + d) / c
    z = -(a * x + b * y + d) / c

    plane_points = np.stack((x.flatten(), y.flatten(), z.flatten()), axis=-1)
    plane_mesh = o3d.geometry.TriangleMesh()

    plane_mesh.vertices = o3d.utility.Vector3dVector(plane_points)

    triangles = []
    for i in range(resolution - 1):
        for j in range(resolution - 1):
            triangles.append([i * resolution + j, (i + 1) * resolution + j, i * resolution + (j + 1)])
            triangles.append([(i + 1) * resolution + j, (i + 1) * resolution + (j + 1), i * resolution + (j + 1)])

    plane_mesh.triangles = o3d.utility.Vector3iVector(triangles)

    plane_mesh.paint_uniform_color([0.1, 0.8, 0.1])
    return plane_mesh
