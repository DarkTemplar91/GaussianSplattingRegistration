import torch
import numpy as np

from src.utils.graphics_utils import getWorld2View2
import torch.nn.functional as F


class Camera:
    def __init__(self, R, T, fx, fy, image_name, width, height,
                 trans=np.array([0.0, 0.0, 0.0]), scale=1.0, target=torch.zeros(3, dtype=torch.float32)):
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

        self.speed = 0.01  # Movement speed
        self.rotation_speed = np.radians(1)  # Rotation speed (in radians)
        self.zoom_factor = 0.01

    def move(self, direction):
        if direction == "left":
            self.position += self.speed * torch.tensor([1, 0, 0], dtype=torch.float32)  # Left
        elif direction == "right":
            self.position -= self.speed * torch.tensor([1, 0, 0], dtype=torch.float32)  # Right
        elif direction == "up":
            self.position += self.speed * torch.tensor([0, 1, 0], dtype=torch.float32)  # Up
        elif direction == "down":
            self.position -= self.speed * torch.tensor([0, 1, 0], dtype=torch.float32)  # Down

        self.update_view_matrix()

    def rotate(self, yaw_change, pitch_change):
        torch_yawn = torch.tensor(yaw_change)
        torch_pitch = torch.tensor(pitch_change)
        """Rotate the camera based on yaw and pitch changes."""
        # Update rotation matrix with yaw change
        yaw_matrix = torch.tensor([
            [torch.cos(torch_yawn), 0, -torch.sin(torch_yawn)],
            [0, 1, 0],
            [torch.sin(torch_yawn), 0, torch.cos(torch_yawn)]
        ], dtype=torch.float32)

        # Update rotation matrix with pitch change
        pitch_matrix = torch.tensor([
            [1, 0, 0],
            [0, torch.cos(torch_pitch), -torch.sin(torch_pitch)],
            [0, torch.sin(torch_pitch), torch.cos(torch_pitch)]
        ], dtype=torch.float32)

        # Update the camera's rotation matrix
        self.rotation = self.rotation @ yaw_matrix @ pitch_matrix
        self.update_view_matrix()

    def zoom(self, delta):
        self.position += -delta * self.zoom_factor * torch.tensor([0, 0, 1], dtype=torch.float32)
        self.update_view_matrix()

    def update_view_matrix(self):
        # Update the view matrix based on the current position and rotation
        self.viewmat = torch.tensor(
            getWorld2View2(self.rotation.numpy(), self.position.numpy(), np.array([0.0, 0.0, 0.0]), 1.0))[None, :, :]