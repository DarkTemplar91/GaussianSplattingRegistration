import math

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSplitter, QGroupBox, \
    QTabWidget, QErrorMessage, QMessageBox, QSizePolicy

from src.gui.tabs.evaluation_tab import EvaluationTab
from src.gui.tabs.gaussian_mixture_tab import GaussianMixtureTab
from src.gui.tabs.global_registration_tab import GlobalRegistrationTab
from src.gui.tabs.input_tab import InputTab
from src.gui.tabs.local_registration_tab import LocalRegistrationTab
from src.gui.tabs.merger_tab import MergeTab
from src.gui.tabs.multi_scale_registration_tab import MultiScaleRegistrationTab
from src.gui.tabs.rasterizer_tab import RasterizerTab
from src.gui.tabs.visualizer_tab import VisualizerTab
from src.gui.widgets.progress_dialog_factory import ProgressDialogFactory
from src.gui.widgets.transformation_widget import Transformation3DPicker
from src.gui.windows.image_viewer_window import RasterImageViewer
from src.gui.windows.open3d_window import Open3DWindow
from src.gui.workers.qt_base_worker import move_worker_to_thread
from src.gui.workers.qt_evaluator import RegistrationEvaluator
from src.gui.workers.qt_fgr_registrator import FGRRegistrator
from src.gui.workers.qt_gaussian_mixture import GaussianMixtureWorker
from src.gui.workers.qt_gaussian_saver import GaussianSaverNormal, GaussianSaverUseCorresponding
from src.gui.workers.qt_local_registrator import LocalRegistrator
from src.gui.workers.qt_multiscale_registrator import MultiScaleRegistratorVoxel, MultiScaleRegistratorMixture
from src.gui.workers.qt_pc_loaders import PointCloudSaver, PointCloudLoaderGaussian, PointCloudLoaderInput, \
    PointCloudLoaderO3D
from src.gui.workers.qt_ransac_registrator import RANSACRegistrator
from src.gui.workers.qt_rasterizer import RasterizerWorker


class RegistrationMainWindow(QMainWindow):

    # Constructor
    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.setWindowTitle("Gaussian Splatting Registration")
        # Set window size to screen size
        self.showMaximized()

        # Point cloud output of the 3D Gaussian Splatting
        self.pc_gaussian_list_first = []
        self.pc_gaussian_list_second = []

        # Open3D point clouds to display
        self.pc_open3d_list_first = []
        self.pc_open3d_list_second = []

        self.current_index = 0

        # Dataclass that stores the results and parameters of the last local registration
        self.local_registration_data = None

        # Tabs for the settings page
        self.input_tab = None
        self.merger_widget = None
        self.visualizer_widget = None
        self.rasterizer_tab = None
        self.transformation_picker = None
        self.hem_widget = None

        # Image viewer
        self.raster_window = None

        # Create splitter and two planes
        splitter = QSplitter(self)
        self.pane_open3d = Open3DWindow(self)
        pane_data = QWidget()

        layout_pane = QVBoxLayout()
        pane_data.setLayout(layout_pane)

        group_input_data = QGroupBox()
        self.setup_input_group(group_input_data)

        group_registration = QGroupBox()
        self.setup_registration_group(group_registration)

        layout_pane.addWidget(group_input_data)
        layout_pane.addWidget(group_registration)
        layout_pane.setStretch(0, 1)
        layout_pane.setStretch(1, 1)

        splitter.addWidget(self.pane_open3d)
        splitter.addWidget(pane_data)

        splitter.setOrientation(Qt.Orientation.Horizontal)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

    # GUI setup functions
    def setup_input_group(self, group_input_data):
        group_input_data.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        group_input_data.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        group_input_data.setTitle("Inputs and settings")
        layout = QVBoxLayout()
        group_input_data.setLayout(layout)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        self.input_tab = InputTab()
        self.transformation_picker = Transformation3DPicker()
        self.visualizer_widget = VisualizerTab()
        self.rasterizer_tab = RasterizerTab()
        self.merger_widget = MergeTab()

        self.input_tab.signal_load_gaussian.connect(self.handle_gaussian_load)
        self.input_tab.signal_load_sparse.connect(self.handle_sparse_load)
        self.input_tab.signal_load_cached.connect(self.handle_cached_load)
        self.transformation_picker.transformation_matrix_changed.connect(self.update_point_clouds)
        self.visualizer_widget.signal_change_vis.connect(self.change_visualizer)
        self.visualizer_widget.signal_get_current_view.connect(self.get_current_view)
        self.visualizer_widget.signal_pop_visualizer.connect(self.pane_open3d.on_embed_button_pressed)
        self.merger_widget.signal_merge_point_clouds.connect(self.merge_point_clouds)
        self.rasterizer_tab.signal_rasterize.connect(self.rasterize_gaussians)

        tab_widget.addTab(self.input_tab, "I/O")
        tab_widget.addTab(self.transformation_picker, "Transformation")
        tab_widget.addTab(self.visualizer_widget, "Visualizer")
        tab_widget.addTab(self.rasterizer_tab, "Rasterizer")
        tab_widget.addTab(self.merger_widget, "Merging")

    def setup_registration_group(self, group_registration):
        group_registration.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        group_registration.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        group_registration.setLayout(layout)
        group_registration.setTitle("Registration and evaluation")

        registration_tab = QTabWidget()

        local_registration_widget = LocalRegistrationTab()
        local_registration_widget.signal_do_registration.connect(self.do_local_registration)

        global_registration_widget = GlobalRegistrationTab()
        global_registration_widget.signal_do_ransac.connect(self.do_ransac_registration)
        global_registration_widget.signal_do_fgr.connect(self.do_fgr_registration)

        multi_scale_registration_widget = MultiScaleRegistrationTab()
        multi_scale_registration_widget.signal_do_registration.connect(
            self.do_multiscale_registration)

        self.hem_widget = GaussianMixtureTab()
        self.hem_widget.signal_create_mixture.connect(self.create_mixture)
        self.hem_widget.signal_slider_changed.connect(self.active_pc_changed)

        evaluator_widget = EvaluationTab()
        evaluator_widget.signal_camera_change.connect(self.pane_open3d.apply_camera_transformation)
        evaluator_widget.signal_evaluate_registration.connect(self.evaluate_registration)

        registration_tab.addTab(global_registration_widget, "Global")
        registration_tab.addTab(local_registration_widget, "Local")
        registration_tab.addTab(multi_scale_registration_widget, "Multiscale")
        registration_tab.addTab(self.hem_widget, "Mixture")
        registration_tab.addTab(evaluator_widget, "Evaluation")
        layout.addWidget(registration_tab)

    # Event Handlers
    def update_point_clouds(self, transformation_matrix):
        dc1 = dc2 = None
        if self.visualizer_widget.get_use_debug_color():
            dc1, dc2 = self.visualizer_widget.get_debug_colors()

        self.pane_open3d.update_transform(transformation_matrix, dc1, dc2)

    def handle_sparse_load(self, sparse_path_first, sparse_path_second):
        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Loading point clouds...")
        worker = PointCloudLoaderInput(sparse_path_first, sparse_path_second)
        thread = move_worker_to_thread(worker, self.handle_result_sparse, progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def handle_gaussian_load(self, gaussian_path_first, gaussian_path_second, save_o3d_pc):
        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Loading point clouds...")
        worker = PointCloudLoaderGaussian(gaussian_path_first, gaussian_path_second)
        thread = move_worker_to_thread(worker, lambda result: self.handle_result_gaussian(result, save_o3d_pc),
                                       progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def handle_cached_load(self, cached_path_first, cached_path_second):
        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Loading point clouds...")
        worker = PointCloudLoaderO3D(cached_path_first, cached_path_second)
        thread = move_worker_to_thread(worker, self.handle_result_cached, progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def handle_result_sparse(self, sparse_result):
        self.transformation_picker.reset_transformation()
        self.handle_point_cloud_loading(sparse_result.point_cloud_first, sparse_result.point_cloud_second)

    def handle_result_gaussian(self, gaussian_result, save_o3d_point_clouds):
        self.transformation_picker.reset_transformation()
        self.handle_point_cloud_loading(gaussian_result.o3d_point_cloud_first, gaussian_result.o3d_point_cloud_second,
                                        gaussian_result.gaussian_point_cloud_first,
                                        gaussian_result.gaussian_point_cloud_second)

        if save_o3d_point_clouds:
            progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Saving open3D point clouds...")
            worker = PointCloudSaver(gaussian_result.o3d_point_cloud_first, gaussian_result.o3d_point_cloud_first)
            thread = move_worker_to_thread(worker, lambda *args: None, progress_handler=progress_dialog.setValue)
            thread.start()
            progress_dialog.exec()

    def handle_result_cached(self, cached_result):
        self.transformation_picker.reset_transformation()
        self.handle_point_cloud_loading(cached_result.point_cloud_first, cached_result.point_cloud_first)

    def handle_point_cloud_loading(self, pc_first, pc_second, original1=None, original2=None):
        error_message = ('Importing one or both of the point clouds failed.\nPlease check that you entered the correct '
                         'path and the point clouds are of the appropriate type!')
        if self.check_if_none_and_throw_error(pc_first, pc_second, error_message):
            return

        self.current_index = 0

        self.hem_widget.set_slider_range(0)
        self.hem_widget.set_slider_enabled(False)

        self.pc_gaussian_list_first.clear()
        self.pc_gaussian_list_second.clear()
        self.pc_open3d_list_first.clear()
        self.pc_open3d_list_second.clear()

        self.pc_gaussian_list_first.append(original1)
        self.pc_gaussian_list_second.append(original2)
        self.pc_open3d_list_first.append(pc_first)
        self.pc_open3d_list_second.append(pc_second)

        self.pane_open3d.vis.reset_view_point(True)
        self.pane_open3d.load_point_clouds(pc_first, pc_second)

    def change_visualizer(self, zoom, front, lookat, up, dc1, dc2):
        self.pane_open3d.update_transform(self.transformation_picker.transformation_matrix, dc1, dc2)
        self.pane_open3d.update_visualizer(zoom, front, lookat, up)

    def get_current_view(self):
        zoom, front, lookat, up = self.pane_open3d.get_current_view()
        self.visualizer_widget.set_visualizer_attributes(zoom, front, lookat, up)

    def merge_point_clouds(self, use_corresponding_pc, pc_path1, pc_path2, merge_path):
        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Saving merged point cloud...")
        transformation = self.transformation_picker.transformation_matrix
        if use_corresponding_pc:
            worker = GaussianSaverUseCorresponding(pc_path1, pc_path2, transformation, merge_path)
        elif len(self.pc_gaussian_list_second) != 0 and len(self.pc_gaussian_list_first) != 0:
            pc_first = self.pc_gaussian_list_first[self.current_index]
            pc_second = self.pc_gaussian_list_second[self.current_index]
            worker = GaussianSaverNormal(pc_first, pc_second, transformation, merge_path)
        else:
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage("There were no preloaded point clouds found! Load a Gaussian point cloud before merging,"
                               "or check the \"corresponding inputs\" option and select the point clouds you wish to "
                               "merge.")
            return

        thread = move_worker_to_thread(worker, lambda *args: None, error_handler=self.create_error_list_dialog,
                                       progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    # Registration
    def do_local_registration(self, registration_type, max_correspondence,
                              relative_fitness, relative_rmse, max_iteration, rejection_type, k_value):
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2
        init_trans = self.transformation_picker.transformation_matrix

        # Create worker for local registration
        worker = LocalRegistrator(pc1, pc2, init_trans, registration_type, max_correspondence,
                                  relative_fitness, relative_rmse, max_iteration, rejection_type,
                                  k_value)

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Registering point clouds...")
        thread = move_worker_to_thread(worker, self.handle_registration_result_local,
                                       progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def do_ransac_registration(self, voxel_size, mutual_filter, max_correspondence, estimation_method,
                               ransac_n, checkers, max_iteration, confidence):
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2

        worker = RANSACRegistrator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                   voxel_size, mutual_filter, max_correspondence,
                                   estimation_method, ransac_n, checkers, max_iteration, confidence)

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Registering point clouds...")
        thread = move_worker_to_thread(worker, self.handle_registration_result_global,
                                       progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def do_fgr_registration(self, voxel_size, division_factor, use_absolute_scale, decrease_mu, maximum_correspondence,
                            max_iterations, tuple_scale, max_tuple_count, tuple_test):
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2

        worker = FGRRegistrator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                voxel_size, division_factor, use_absolute_scale, decrease_mu,
                                maximum_correspondence,
                                max_iterations, tuple_scale, max_tuple_count, tuple_test)

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Registering point clouds...")
        thread = move_worker_to_thread(worker, self.handle_registration_result_global,
                                       progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def do_multiscale_registration(self, use_corresponding, sparse_first, sparse_second, registration_type,
                                   relative_fitness, relative_rmse, voxel_values, iter_values, rejection_type,
                                   k_value, use_mixture):

        if use_mixture:
            pc1_list = self.pc_open3d_list_first
            pc2_list = self.pc_open3d_list_second
            worker = MultiScaleRegistratorMixture(pc1_list, pc2_list, self.transformation_picker.transformation_matrix,
                                                  use_corresponding, sparse_first, sparse_second,
                                                  registration_type, relative_fitness,
                                                  relative_rmse, voxel_values, iter_values,
                                                  rejection_type, k_value)
        else:
            pc1 = self.pane_open3d.pc1
            pc2 = self.pane_open3d.pc2
            worker = MultiScaleRegistratorVoxel(pc1, pc2, self.transformation_picker.transformation_matrix,
                                                use_corresponding, sparse_first, sparse_second,
                                                registration_type, relative_fitness,
                                                relative_rmse, voxel_values, iter_values,
                                                rejection_type, k_value)

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Registering point clouds...")
        thread = move_worker_to_thread(worker, self.handle_registration_result_local, self.create_error_list_dialog,
                                       progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def handle_registration_result_local(self, resultData: LocalRegistrator.ResultData):
        self.local_registration_data = resultData.registration_data
        results = resultData.result
        self.handle_registration_result_base(results.transformation, results.fitness, results.inlier_rmse)

    def handle_registration_result_global(self, results):
        transformation_actual = np.dot(results.transformation, self.transformation_picker.transformation_matrix)
        self.handle_registration_result_base(transformation_actual, results.fitness, results.inlier_rmse)

    def handle_registration_result_base(self, transformation, fitness, inlier_rmse):
        self.transformation_picker.set_transformation(transformation)

        message_dialog = QMessageBox()
        message_dialog.setWindowTitle("Successful registration")
        message_dialog.setText(f"The registration of the point clouds is finished.\n"
                               f"The transformation will be applied.\n\n"
                               f"Fitness: {fitness}\n"
                               f"RMSE: {inlier_rmse}\n")
        message_dialog.exec()

    def rasterize_gaussians(self, width, height, scale, color, intrinsics_supplied):
        pc1 = self.pc_gaussian_list_first[self.current_index] if self.pc_gaussian_list_first else None
        pc2 = self.pc_gaussian_list_second[self.current_index] if self.pc_gaussian_list_second else None

        error_message = 'Load two Gaussian point clouds for rasterization!'
        if not pc1 or not pc2:
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage(error_message)
            return

        if self.pane_open3d.is_ortho():
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage("The current projection type is orthographical, which is invalid for rasterization.\n"
                               "Increase the FOV to continue!")
            return

        extrinsic = self.pane_open3d.get_camera_extrinsic().astype(np.float32)
        intrinsic = intrinsics_supplied
        if intrinsic is None:
            intrinsic = self.pane_open3d.get_camera_intrinsic().astype(np.float32)

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Creating rasterized image...")
        worker = RasterizerWorker(pc1, pc2, self.transformation_picker.transformation_matrix,
                                  extrinsic, intrinsic, scale, color, height, width)

        thread = move_worker_to_thread(worker, self.create_raster_window, progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def create_raster_window(self, pix):
        self.raster_window = RasterImageViewer()
        self.raster_window.set_image(pix)
        self.raster_window.setWindowTitle("Rasterized point clouds")
        self.raster_window.setWindowModality(Qt.WindowModality.WindowModal)
        self.raster_window.show()

    def evaluate_registration(self, camera_list, image_path, log_path, color, use_gpu):
        pc1 = self.pc_gaussian_list_first[self.current_index]
        pc2 = self.pc_gaussian_list_second[self.current_index]

        if not pc1 or not pc2:
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage("There are no gaussian point clouds loaded for registration evaluation!"
                               "\nPlease load two point clouds for registration and evaluation")
            return

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Evaluating registration...")
        worker = RegistrationEvaluator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                       camera_list, image_path, log_path, color, self.local_registration_data,
                                       use_gpu)
        progress_dialog.canceled.connect(worker.cancel_evaluation)
        thread = move_worker_to_thread(worker, self.handle_evaluation_result, progress_handler=progress_dialog.setValue)
        thread.start()
        progress_dialog.exec()

    def create_mixture(self, hem_reduction, distance_delta, color_delta, cluster_level):
        pc1 = pc2 = None

        if len(self.pc_gaussian_list_first) != 0:
            pc1 = self.pc_gaussian_list_first[0]
        if len(self.pc_gaussian_list_second) != 0:
            pc2 = self.pc_gaussian_list_second[0]

        if not pc1 or not pc2:
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage("There are no gaussian point clouds loaded! "
                               "Please load two point clouds to create Gaussian mixtures.")
            return

        progress_dialog = ProgressDialogFactory.get_progress_dialog("Loading", "Creating Gaussian mixtures...")
        worker = GaussianMixtureWorker(pc1, pc2, hem_reduction, distance_delta, color_delta, cluster_level)
        thread = move_worker_to_thread(worker, self.handle_mixture_results, progress_handler=progress_dialog.setValue)
        progress_dialog.canceled.connect(worker.cancel)

        thread.start()
        progress_dialog.exec()

    def handle_mixture_results(self, result_data: GaussianMixtureWorker.ResultData):

        if len(self.pc_gaussian_list_first) > 1:
            base_pc_first = self.pc_gaussian_list_first[0]
            base_pc_second = self.pc_gaussian_list_second[0]
            base_open3d_first = self.pc_open3d_list_first[0]
            base_open3d_second = self.pc_open3d_list_second[0]

            self.pc_gaussian_list_first.clear()
            self.pc_gaussian_list_second.clear()
            self.pc_open3d_list_first.clear()
            self.pc_open3d_list_second.clear()
            self.pc_open3d_list_first.append(base_open3d_first)
            self.pc_open3d_list_second.append(base_open3d_second)
            self.pc_gaussian_list_first.append(base_pc_first)
            self.pc_gaussian_list_second.append(base_pc_second)

        self.pc_open3d_list_first.extend(result_data.list_open3d_first)
        self.pc_open3d_list_second.extend(result_data.list_open3d_second)
        self.pc_gaussian_list_first.extend(result_data.list_gaussian_first)
        self.pc_gaussian_list_second.extend(result_data.list_gaussian_second)

        self.hem_widget.set_slider_range(len(self.pc_gaussian_list_first) - 1)
        self.hem_widget.set_slider_enabled(True)
        self.hem_widget.set_slider_to(0)

    def active_pc_changed(self, index):
        if self.current_index == index:
            return

        self.current_index = index

        dc1 = dc2 = None
        if self.visualizer_widget.get_use_debug_color():
            dc1, dc2 = self.visualizer_widget.get_debug_colors()

        self.pane_open3d.load_point_clouds(self.pc_open3d_list_first[index], self.pc_open3d_list_second[index], True,
                                           self.transformation_picker.transformation_matrix, dc1, dc2)

    def check_if_none_and_throw_error(self, pc_first, pc_second, message):
        if not pc_first or not pc_second:
            # TODO: Further error messages. Tracing?
            dialog = QErrorMessage(self)
            dialog.setModal(True)
            dialog.setWindowTitle("Error")
            dialog.showMessage(message)
            return True

        return False

    def closeEvent(self, event):
        self.pane_open3d.close()
        super(QMainWindow, self).closeEvent(event)

    @staticmethod
    def create_error_list_dialog(error_list):
        message_dialog = QMessageBox()
        message_dialog.setModal(True)
        message_dialog.setWindowTitle("Error occurred")
        message_dialog.setText("The following error(s) occurred.\n Click \"Show details\" for more information!")
        message_dialog.setDetailedText("\n".join(error_list))
        message_dialog.exec()

    @staticmethod
    def handle_evaluation_result(log_object):
        message_dialog = QMessageBox()
        message_dialog.setModal(True)
        message_dialog.setWindowTitle("Evaluation finished")
        message = "The evaluation finished with"
        if not math.isnan(log_object.psnr):
            message += " success.\n"
            message += f"\nMSE:  {log_object.mse}"
            message += f"\nRMSE: {log_object.rmse}"
            message += f"\nSSIM: {log_object.ssim}"
            message += f"\nPSNR: {log_object.psnr}"
            message += f"\nLPIP: {log_object.lpips}"
        else:
            message += " error."

        if log_object.error_list:
            message += "\nClick \"Show details\" for any potential issues."
            message_dialog.setDetailedText("\n".join(log_object.error_list))

        message_dialog.setText(message)
        message_dialog.exec()
