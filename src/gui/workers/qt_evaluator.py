import copy
import json
import os.path

import torch
from PIL import Image
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
import torchvision.transforms.functional as tf

from src.models.gaussian_model import GaussianModel
from src.utils.point_cloud_merger import merge_point_clouds
from src.utils.rasterization_util import rasterize_image


class RegistrationEvaluator(QObject):
    signal_finished = pyqtSignal()
    signal_evaluation_done = pyqtSignal(object)

    signal_update_progress = pyqtSignal(int)

    def __init__(self, pc1, pc2, transformation, cameras_list, images_path, log_path, color, registration_result):
        super().__init__()
        # Signal to cancel task
        self.signal_cancel = False

        self.pc1 = copy.deepcopy(pc1)
        self.pc2 = copy.deepcopy(pc2)

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

        self.current_progress = 0
        self.max_progress = 201

    def do_evaluation(self):
        merged_pc = merge_point_clouds(self.pc1, self.pc2, self.transformation)
        point_cloud = GaussianModel(3)
        point_cloud.from_ply(merged_pc)

        rendered_images = []
        gt_images = []
        error_list = []
        for idx, camera in enumerate(self.cameras_list):
            # Process events, look for cancel signal
            QtWidgets.QApplication.processEvents()
            if self.signal_cancel:
                # Force gpu memory garbage collection
                del gt_images
                del rendered_images
                torch.cuda.empty_cache()
                import gc
                gc.collect()
                
                return

            self.update_progress()

            img_name = camera.image_name
            image_path = os.path.join(self.images_path, img_name + ".png")
            try:
                pil_image = Image.open(image_path)
                gt_image = tf.to_tensor(pil_image).unsqueeze(0).cuda()
                gt_images.append(gt_image)
                del gt_image
            except (OSError, IOError) as e:
                error_list.append(str(e))
                continue
            image_tensor, _ = rasterize_image(point_cloud, camera, 1, self.color, self.device)
            image_tensor = image_tensor.unsqueeze(0)
            rendered_images.append(image_tensor)
            del image_tensor

        self.evaluate_images(rendered_images, gt_images)

        log = self.create_and_save_log_file(error_list)
        self.update_progress()

        # Force gpu memory garbage collection
        del gt_images
        del rendered_images
        torch.cuda.empty_cache()
        import gc
        gc.collect()

        self.signal_evaluation_done.emit(log)
        self.signal_finished.emit()

    def cancel_evaluation(self):
        self.signal_cancel = True

    def update_progress(self):
        self.current_progress += 1
        new_percent = int(self.current_progress / self.max_progress * 100)
        self.signal_update_progress.emit(new_percent)

    def evaluate_images(self, rendered_images, gt_images):
        from src.submodules.lpips_pytorch import lpips
        from src.utils.evaluation_utils import ssim, psnr, mse

        mses = []
        rmses = []
        ssims = []
        psnrs = []
        lpipss = []

        for idx in range(len(rendered_images)):

            QtWidgets.QApplication.processEvents()
            if self.signal_cancel:
                # Force gpu memory garbage collection
                del gt_images
                del rendered_images
                torch.cuda.empty_cache()
                import gc
                gc.collect()
                self.signal_finished.emit()
                return

            self.update_progress()
            current_mse = mse(rendered_images[idx], gt_images[idx])
            mses.append(current_mse)
            rmses.append(torch.sqrt(current_mse))
            ssims.append(ssim(rendered_images[idx], gt_images[idx]))
            psnrs.append(psnr(rendered_images[idx], gt_images[idx]))
            lpipss.append(lpips(rendered_images[idx], gt_images[idx]))

        self.mean_mses = torch.tensor(mses).mean().item()
        self.mean_rmses = torch.tensor(rmses).mean().item()
        self.mean_ssims = torch.tensor(ssims).mean().item()
        self.mean_psnrs = torch.tensor(psnrs).mean().item()
        self.mean_lpipss = torch.tensor(lpipss).mean().item()

    def create_and_save_log_file(self, error_list):
        evaluation = self.EvaluationObject(self.registration_result, self.mean_mses, self.mean_rmses,
                                           self.mean_ssims, self.mean_psnrs, self.mean_lpipss, error_list)
        with open(self.log_path, 'w') as f:
            json.dump(evaluation.__dict__, f, default=lambda x: x.tolist(), indent=2)

        return evaluation

    # Class for the JSON evaluation
    class EvaluationObject(object):

        registration_data: dict
        mse: float
        rmse: float
        ssim: float
        psnr: float
        lpips: float

        error_list: list

        def __init__(self, registration_data, mse, rmse, ssim, psnr, lpips, error_list):
            super().__init__()

            self.registration_data = dict()
            if registration_data is not None:
                self.registration_data = registration_data.__dict__
            self.mse = mse
            self.rmse = rmse
            self.ssim = ssim
            self.psnr = psnr
            self.lpips = lpips
            self.error_list = error_list

