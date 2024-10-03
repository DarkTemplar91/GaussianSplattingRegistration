import torch
import numpy as np

from src.utils.graphics_utils import getWorld2View2


class Camera:
    def __init__(self, R, T, fx, fy, image_name, width, height,
                 trans=np.array([0.0, 0.0, 0.0]), scale=1.0):
        super(Camera, self).__init__()
        self.image_name = image_name
        self.width = width
        self.height = height
        self.intrinsics = torch.tensor([
            [fx, 0, width / 2],
            [0, fy, height / 2],
            [0, 0, 1]
        ], dtype=torch.float32, device='cuda:0')
        self.viewmat = torch.tensor(getWorld2View2(R, T, trans, scale), device="cuda:0")[None, :, :]
