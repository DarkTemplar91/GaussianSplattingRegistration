import torch
import numpy as np

from src.utils.graphics_utils import getWorld2View2, get_focal_from_intrinsics, get_dimension_from_intrinsics


class Camera:
    right_vector = torch.tensor([1, 0, 0], dtype=torch.float32)
    up_vector = torch.tensor([0, 1, 0], dtype=torch.float32)

    def __init__(self, R, T, fx, fy, image_name, width, height,
                 trans=np.array([0.0, 0.0, 0.0]), scale=1.0):
        super(Camera, self).__init__()
        self.image_name = image_name
        self.position = torch.tensor(T, dtype=torch.float32)
        self.rotation = torch.tensor(R, dtype=torch.float32)
        self.width = width
        self.height = height
        self.intrinsics = torch.tensor([
            [fx, 0, width / 2],
            [0, fy, height / 2],
            [0, 0, 1]
        ], dtype=torch.float32)[None, :, :]

        # Initial view matrix
        self.viewmat = torch.tensor(getWorld2View2(R, T, trans, scale))[None, :, :]

        # Camera position and orientation
        self.position = torch.tensor(T, dtype=torch.float32)
        self.rotation = torch.tensor(R, dtype=torch.float32)

    def move_horizontally(self, speed):
        self.position += speed * self.right_vector

    def move_vertically(self, speed):
        self.position += speed * self.up_vector

    def rotate(self, yaw_change, pitch_change):
        torch_yawn = torch.tensor(yaw_change)
        torch_pitch = torch.tensor(pitch_change)

        yaw_matrix = torch.tensor([
            [torch.cos(torch_yawn), 0, -torch.sin(torch_yawn)],
            [0, 1, 0],
            [torch.sin(torch_yawn), 0, torch.cos(torch_yawn)]
        ], dtype=torch.float32)

        pitch_matrix = torch.tensor([
            [1, 0, 0],
            [0, torch.cos(torch_pitch), -torch.sin(torch_pitch)],
            [0, torch.sin(torch_pitch), torch.cos(torch_pitch)]
        ], dtype=torch.float32)

        self.rotation = self.rotation @ yaw_matrix @ pitch_matrix

    def zoom(self, delta):
        self.position += -delta * torch.tensor([0, 0, 1], dtype=torch.float32)

    def update_view_matrix(self):
        self.viewmat = torch.tensor(getWorld2View2(self.rotation.numpy(), self.position.numpy()))[None, :, :]
