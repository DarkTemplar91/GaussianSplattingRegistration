#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import numpy as np
import torch
from plyfile import PlyElement, PlyData
from torch import nn

from src.utils.general_utils import build_scaling_rotation, strip_symmetric, \
    inverse_sigmoid, build_rotation, matrices_to_quaternions


class GaussianModel:

    def setup_functions(self):
        def build_covariance_from_scaling_rotation(scaling, scaling_modifier, rotation):
            L = build_scaling_rotation(scaling_modifier * scaling, rotation)
            actual_covariance = L @ L.transpose(1, 2)
            symm = strip_symmetric(actual_covariance)
            return symm

        self.scaling_activation = torch.exp
        self.scaling_inverse_activation = torch.log

        self.covariance_activation = build_covariance_from_scaling_rotation

        self.opacity_activation = torch.sigmoid
        self.inverse_opacity_activation = inverse_sigmoid

        self.rotation_activation = torch.nn.functional.normalize

    def __init__(self, sh_degree: int):
        self.sh_degree = sh_degree
        self._xyz = torch.empty(0)
        self._features_dc = torch.empty(0)
        self._features_rest = torch.empty(0)
        self._scaling = torch.empty(0)
        self._rotation = torch.empty(0)
        self._opacity = torch.empty(0)
        self._covariance = torch.empty(0)
        self.setup_functions()

    @property
    def get_scaling(self):
        return self.scaling_activation(self._scaling)

    @property
    def get_rotation(self):
        return self.rotation_activation(self._rotation)

    @property
    def get_xyz(self):
        return self._xyz

    @property
    def get_features(self):
        features_dc = self._features_dc
        features_rest = self._features_rest
        return torch.cat((features_dc, features_rest), dim=1)

    @property
    def get_colors(self):
        return self._features_dc.flatten(start_dim=1)

    @property
    def get_opacity_with_activation(self):
        return self.opacity_activation(self._opacity)

    @property
    def get_raw_opacity(self):
        return self._opacity

    @property
    def get_covariance3D(self):
        return self._covariance


    def get_scaled_covariance(self, scaling_modifier=1):
        return self.covariance_activation(self.get_scaling, scaling_modifier, self._rotation)


    def from_ply(self, plydata):
        xyz = np.stack((np.asarray(plydata.elements[0]["x"]),
                        np.asarray(plydata.elements[0]["y"]),
                        np.asarray(plydata.elements[0]["z"])), axis=1)
        opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis]

        features_dc = np.zeros((xyz.shape[0], 3, 1))
        features_dc[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
        features_dc[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
        features_dc[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])

        extra_f_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
        extra_f_names = sorted(extra_f_names, key=lambda x: int(x.split('_')[-1]))
        assert len(extra_f_names) == 3 * (self.sh_degree + 1) ** 2 - 3
        features_extra = np.zeros((xyz.shape[0], len(extra_f_names)))
        for idx, attr_name in enumerate(extra_f_names):
            features_extra[:, idx] = np.asarray(plydata.elements[0][attr_name])
        # Reshape (P,F*SH_coeffs) to (P, F, SH_coeffs except DC)
        features_extra = features_extra.reshape((features_extra.shape[0], 3, (self.sh_degree + 1) ** 2 - 1))

        scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale_")]
        scale_names = sorted(scale_names, key=lambda x: int(x.split('_')[-1]))
        scales = np.zeros((xyz.shape[0], len(scale_names)))
        for idx, attr_name in enumerate(scale_names):
            scales[:, idx] = np.asarray(plydata.elements[0][attr_name])

        rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
        rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
        rots = np.zeros((xyz.shape[0], len(rot_names)))
        for idx, attr_name in enumerate(rot_names):
            rots[:, idx] = np.asarray(plydata.elements[0][attr_name])

        self._xyz = nn.Parameter(torch.tensor(xyz, dtype=torch.float, device="cuda").requires_grad_(True))
        self._features_dc = nn.Parameter(
            torch.tensor(features_dc, dtype=torch.float, device="cuda").transpose(1, 2).contiguous().requires_grad_(
                True))
        self._features_rest = nn.Parameter(
            torch.tensor(features_extra, dtype=torch.float, device="cuda").transpose(1, 2).contiguous().requires_grad_(
                True))
        self._opacity = nn.Parameter(torch.tensor(opacities, dtype=torch.float, device="cuda").requires_grad_(True))
        self._scaling = nn.Parameter(torch.tensor(scales, dtype=torch.float, device="cuda").requires_grad_(True))
        self._rotation = nn.Parameter(torch.tensor(rots, dtype=torch.float, device="cuda").requires_grad_(True))

        L = build_scaling_rotation(self._scaling, self._rotation)
        actual_covariance = L @ L.transpose(1, 2)
        self._covariance = actual_covariance

    def construct_list_of_attributes(self):
        l = ['x', 'y', 'z', 'nx', 'ny', 'nz']
        # All channels except the 3 DC
        for i in range(self._features_dc.shape[1]*self._features_dc.shape[2]):
            l.append('f_dc_{}'.format(i))
        for i in range(self._features_rest.shape[1]*self._features_rest.shape[2]):
            l.append('f_rest_{}'.format(i))
        l.append('opacity')
        for i in range(self._scaling.shape[1]):
            l.append('scale_{}'.format(i))
        for i in range(self._rotation.shape[1]):
            l.append('rot_{}'.format(i))
        return l

    def save_ply(self, path):
        xyz = self._xyz.detach().cpu().numpy()
        normals = np.zeros_like(xyz)
        f_dc = self._features_dc.detach().transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
        f_rest = self._features_rest.detach().transpose(1, 2).flatten(start_dim=1).contiguous().cpu().numpy()
        opacities = self._opacity.detach().cpu().numpy()
        scale = self._scaling.detach().cpu().numpy()
        rotation = self._rotation.detach().cpu().numpy()

        dtype_full = [(attribute, 'f4') for attribute in self.construct_list_of_attributes()]

        elements = np.empty(xyz.shape[0], dtype=dtype_full)
        attributes = np.concatenate((xyz, normals, f_dc, f_rest, opacities, scale, rotation), axis=1)
        elements[:] = list(map(tuple, attributes))
        el = PlyElement.describe(elements, 'vertex')
        PlyData([el]).write(path)

    def clone_gaussian(self):
        new_model = GaussianModel(3)
        new_model._covariance = self._covariance.clone().detach().requires_grad_(True)
        new_model._xyz = self._xyz.clone().detach().requires_grad_(True)
        new_model._rotation = self._rotation.clone().detach().requires_grad_(True)
        new_model._scaling = self._scaling.clone().detach().requires_grad_(True)
        new_model._features_dc = self._features_dc.clone().detach().requires_grad_(True)
        new_model._features_rest = self._features_rest.clone().detach().requires_grad_(True)
        new_model._opacity = self._opacity.clone().detach().requires_grad_(True)
        return new_model

    def transform_gaussian(self, transformation_matrix):
        points = torch.cat((self._xyz.T, torch.zeros(1, self._xyz.shape[0],
                                                                     device=self._xyz.device)))
        self._xyz = torch.matmul(transformation_matrix, points).T[:, :3]

        self._xyz[:, 0] += transformation_matrix[0, 3]
        self._xyz[:, 1] += transformation_matrix[1, 3]
        self._xyz[:, 2] += transformation_matrix[2, 3]

        new_rotation = build_rotation(self._rotation)
        new_rotation = transformation_matrix[:3, :3] @ new_rotation
        self._rotation = matrices_to_quaternions(new_rotation)


    @staticmethod
    def get_merged_gaussian_point_clouds(gaussian1, gaussian2, transformation_matrix = None):
        merged_pc = GaussianModel(3)

        if transformation_matrix is not None:
            transformation_matrix_tensor = torch.from_numpy(transformation_matrix.astype(np.float32)).cuda()
            gaussian1.transform_gaussian(transformation_matrix_tensor)

        merged_pc._xyz = torch.cat((gaussian1.xyz, gaussian2.xyz))
        merged_pc._rotation = torch.cat((gaussian1._rotation, gaussian2._rotation))
        merged_pc._scaling = torch.cat((gaussian1._scaling, gaussian2._scaling))
        merged_pc._features_dc = torch.cat((gaussian1.features_dc, gaussian2.features_dc))
        merged_pc._features_rest = torch.cat((gaussian1._features_rest, gaussian2._features_rest))
        merged_pc._opacity = torch.cat((gaussian1.opacity, gaussian2.opacity))

        return merged_pc
