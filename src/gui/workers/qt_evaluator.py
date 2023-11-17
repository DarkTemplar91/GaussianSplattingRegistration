import copy
import json
import math
import os.path
from time import sleep

import torch
from PIL import Image
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.uic.properties import QtGui
from dataclasses import dataclass, asdict
from tqdm import tqdm

from src.submodules.lpips_pytorch import lpips
from src.utils.evaluation_utils import ssim, psnr, mse
from src.utils.point_cloud_merger import merge_point_clouds
from src.utils.rasterization_util import rasterize_image

from torchvision.transforms import functional as T


class RegistrationEvaluator(QObject):
    signal_finished = pyqtSignal()
    signal_evaluation_done = pyqtSignal()

    signal_update_progress = pyqtSignal(int)

    def __init__(self, pc1, pc2, transformation, cameras_list, images_path, log_path, color, registration_result):
        super().__init__()
        # Signal to cancel task
        self.signal_cancel = False

        self.pc1 = copy.copy(pc1)
        self.pc2 = copy.copy(pc2)

        self.transformation = transformation

        self.cameras_list = cameras_list
        self.images_path = images_path
        self.log_path = log_path

        self.color = color
        self.device = "cuda:0"

        self.registration_result = registration_result
        self.mean_rmses = None
        self.mean_ssims = None
        self.mean_psnrs = None
        self.mean_lpipss = None
        self.mean_mses = None

    def do_evaluation(self):
        point_cloud = merge_point_clouds(self.pc1, self.pc2, self.transformation)

        rendered_images = []
        gt_images = []
        for idx, camera in enumerate(self.cameras_list):
            # Process events, look for cancel signal
            QtGui.QApplication.processEvents()
            if self.signal_cancel:
                self.signal_finished.emit()
                return

            img_name = camera.image_name
            image_path = os.path.join(self.images_path, img_name)
            gt_image = Image.open(image_path)

            image_tensor, _ = rasterize_image(point_cloud, camera, self.color, self.device)
            rendered_image = T.to_pil_image(image_tensor)

            gt_images.append(gt_image)
            rendered_images.append(rendered_image)

            # TODO: Set proper value
            # Update progress bar
            percent = int((idx / 100) * 100)
            self.signal_update_progress.emit(percent)
            sleep(1)

        self.evaluate_images(rendered_images, gt_images)

        self.create_log_file()

        self.signal_finished.emit()

    def cancel_evaluation(self):
        self.signal_cancel = True

    def evaluate_images(self, rendered_images, gt_images):
        mses = []
        rmses = []
        ssims = []
        psnrs = []
        lpipss = []

        for idx in tqdm(range(len(rendered_images)), desc="Metric evaluation progress"):
            current_mse = mse(rendered_images[idx], gt_images[idx])
            mses.append(current_mse)
            rmses.append(math.sqrt(current_mse))
            ssims.append(ssim(rendered_images[idx], gt_images[idx]))
            psnrs.append(psnr(rendered_images[idx], gt_images[idx]))
            lpipss.append(lpips(rendered_images[idx], gt_images[idx]))

        self.mean_mses = torch.tensor(mses).mean()
        self.mean_rmses = torch.tensor(rmses).mean()
        self.mean_ssims = torch.tensor(ssims).mean()
        self.mean_psnrs = torch.tensor(psnrs).mean()
        self.mean_lpipss = torch.tensor(lpipss).mean()

    def create_log_file(self):
        evaluation = self.EvaluationObject(self.registration_result, self.mean_mses, self.mean_rmses,
                                           self.mean_ssims, self.mean_psnrs, self.mean_lpipss)

        with open(self.log_path, 'w') as f:
            json.dump(asdict(evaluation), f)

    # Class for the JSON evaluation
    @dataclass
    class EvaluationObject:

        registration_data: dataclass
        mse: float
        rmse: float
        ssim: float
        psnr: float
        lpips: float
