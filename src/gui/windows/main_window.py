import os

import numpy as np
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QMainWindow, QSplitter, QWidget, QGroupBox, QVBoxLayout, \
    QTabWidget, QSizePolicy, QErrorMessage, QMessageBox, QProgressDialog, QLabel

from src.gui.widgets.cache_tab_widget import CacheTab
from src.gui.widgets.global_registration_widget import GlobalRegistrationTab
from src.gui.widgets.input_tab_widget import InputTab
from src.gui.widgets.local_registration_widget import LocalRegistrationTab
from src.gui.widgets.merger_widget import MergerWidget
from src.gui.widgets.multi_scale_registration_widget import MultiScaleRegistrationTab
from src.gui.widgets.rasterizer_tab_widget import RasterizerTab
from src.gui.widgets.transformation_widget import Transformation3DPicker
from src.gui.widgets.visualizer_widget import VisualizerWidget
from src.gui.windows.image_viewer_window import RasterImageViewer
from src.gui.windows.open3d_window import Open3DWindow
from src.gui.workers.qt_fgr_registrator import FGRRegistrator
from src.gui.workers.qt_local_registrator import LocalRegistrator
from src.gui.workers.qt_multiscale_registrator import MultiScaleRegistrator
from src.gui.workers.qt_ransac_registrator import RANSACRegistrator
from src.gui.workers.qt_rasterizer import RasterizerWorker
from src.gui.workers.qt_workers import PointCloudSaver
from src.utils.file_loader import load_plyfile_pc
from src.utils.point_cloud_merger import save_merged_point_clouds


class RegistrationMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(RegistrationMainWindow, self).__init__(parent)
        self.setWindowTitle("Gaussian Splatting Registration")

        # Point cloud output of the 3D Gaussian Splatting
        self.pc_originalFirst = None
        self.pc_originalSecond = None

        # Tabs for the settings page
        self.cache_tab = None
        self.input_tab = None
        self.merger_widget = None
        self.visualizer_widget = None
        self.rasterizer_tab = None
        self.transformation_picker = None

        # Image viewer
        self.raster_window = None

        working_dir = os.getcwd()
        self.cache_dir = os.path.join(working_dir, "cache")
        self.input_dir = os.path.join(working_dir, "inputs")
        self.output_dir = os.path.join(working_dir, "output")

        # Loading bar for registration
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setModal(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setLabel(QLabel("Registering point clouds..."))
        self.progress_dialog.close()

        # Set window size to screen size
        self.showMaximized()

        # Create splitter and two planes
        splitter = QSplitter(self)
        self.pane_open3d = Open3DWindow()
        pane_data = QWidget()

        layout_pane = QVBoxLayout()
        pane_data.setLayout(layout_pane)

        group_input_data = QGroupBox()
        self.setup_input_group(group_input_data)

        group_registration = QGroupBox()
        self.setup_registration_group(group_registration)

        layout_pane.addWidget(group_input_data)
        layout_pane.addWidget(group_registration)

        splitter.addWidget(self.pane_open3d)
        splitter.addWidget(pane_data)

        splitter.setOrientation(1)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

    def setup_input_group(self, group_input_data):
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_input_data.setTitle("Inputs and settings")
        layout = QVBoxLayout()
        group_input_data.setLayout(layout)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        self.input_tab = InputTab(self.input_dir)
        self.cache_tab = CacheTab(self.cache_dir)
        self.transformation_picker = Transformation3DPicker()
        self.visualizer_widget = VisualizerWidget()
        self.rasterizer_tab = RasterizerTab()
        self.merger_widget = MergerWidget(self.output_dir, self.input_dir)

        self.transformation_picker.transformation_matrix_changed.connect(self.update_point_clouds)
        self.input_tab.result_signal.connect(self.handle_result)
        self.cache_tab.result_signal.connect(self.handle_result)
        self.visualizer_widget.signal_change_vis.connect(self.change_visualizer)
        self.visualizer_widget.signal_get_current_view.connect(self.get_current_view)
        self.merger_widget.signal_merge_point_clouds.connect(self.merge_point_clouds)
        self.rasterizer_tab.signal_rasterize.connect(self.rasterize_gaussians)

        tab_widget.addTab(self.input_tab, "I/O files")
        tab_widget.addTab(self.cache_tab, "Cache")
        tab_widget.addTab(self.transformation_picker, "Transformation")
        tab_widget.addTab(self.visualizer_widget, "Visualizer")
        tab_widget.addTab(self.rasterizer_tab, "Rasterizer")
        tab_widget.addTab(self.merger_widget, "Merging")

    def setup_registration_group(self, group_registration):
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        group_registration.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout()
        group_registration.setLayout(layout)

        registration_tab = QTabWidget()

        local_registration_widget = LocalRegistrationTab()
        local_registration_widget.signal_do_registration.connect(self.do_local_registration)

        global_registration_widget = GlobalRegistrationTab()
        global_registration_widget.signal_do_ransac.connect(self.do_ransac_registration)
        global_registration_widget.signal_do_fgr.connect(self.do_fgr_registration)

        multi_scale_registration_widget = MultiScaleRegistrationTab(self.input_dir)
        multi_scale_registration_widget.signal_do_registration.connect(self.do_multi_scale_registration)

        registration_tab.addTab(global_registration_widget, "Global Registration")
        registration_tab.addTab(local_registration_widget, "Local Registration")
        registration_tab.addTab(multi_scale_registration_widget, "Multi-scale")
        layout.addWidget(registration_tab)

    # Event Handlers
    def update_point_clouds(self, transformation_matrix):
        if self.visualizer_widget.get_use_debug_color():
            dc1, dc2 = self.visualizer_widget.get_debug_colors()
            self.pane_open3d.update_transform_with_colors(dc1, dc2, transformation_matrix)
        else:
            self.pane_open3d.update_transform(transformation_matrix)

        zoom, front, lookat, up = self.visualizer_widget.get_current_transformations()
        self.pane_open3d.update_visualizer(zoom, front, lookat, up)

    def handle_result(self, pc_first, pc_second, save_point_clouds, original1=None, original2=None):
        error_message = ('Importing one or both of the point clouds failed.\nPlease check that you entered the correct '
                         'path!')
        if self.check_if_none_and_throw_error(pc_first, pc_second, error_message):
            return

        self.pc_originalFirst = original1
        self.pc_originalSecond = original2

        if save_point_clouds:
            worker = PointCloudSaver(pc_first, pc_second)
            worker.run()

        self.pane_open3d.load_point_clouds(pc_first, pc_second)

    def change_visualizer(self, use_debug_color, dc1, dc2, zoom, front, lookat, up):
        if use_debug_color:
            self.pane_open3d.update_transform_with_colors(dc1, dc2, self.transformation_picker.transformation_matrix)

        self.pane_open3d.update_visualizer(zoom, front, lookat, up)

    def get_current_view(self):
        zoom, front, lookat, up = self.pane_open3d.get_current_view()
        self.visualizer_widget.assign_new_values(zoom, front, lookat, up)

    def merge_point_clouds(self, is_checked, pc_path1, pc_path2, merge_path):
        pc_first = self.pc_originalFirst
        pc_second = self.pc_originalSecond

        if is_checked:
            pc_first = load_plyfile_pc(pc_path1)
            pc_second = load_plyfile_pc(pc_path2)
            error_message = ("Importing one or both of the point clouds failed.\nPlease check that you entered the "
                             "correct path and the point clouds selected are Gaussian point clouds!")
            if self.check_if_none_and_throw_error(pc_first, pc_second, error_message):
                return

        error_message = ("There were no preloaded point clouds found! Load a Gaussian point cloud before merging, "
                         "or check the \"corresponding inputs\" option and select the point clouds you wish to merge.")
        if self.check_if_none_and_throw_error(pc_first, pc_second, error_message):
            return

        save_merged_point_clouds(pc_first, pc_second,
                                 merge_path, self.transformation_picker.transformation_matrix)

    def check_if_none_and_throw_error(self, pc_first, pc_second, message):
        if not pc_first or not pc_second:
            # TODO: Further error messages. Tracing?
            dialog = QErrorMessage(self)
            dialog.setWindowTitle("Error")
            dialog.showMessage(message)
            return True

        return False

    def do_local_registration(self, registration_type, max_correspondence,
                              relative_fitness, relative_rmse, max_iteration):
        # Create worker for local registration
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2
        init_trans = self.transformation_picker.transformation_matrix
        local_registrator = LocalRegistrator(pc1, pc2, init_trans, registration_type, max_correspondence,
                                             relative_fitness, relative_rmse, max_iteration)

        # Create thread
        thread = QThread(self)
        # Move worker to thread
        local_registrator.moveToThread(thread)
        # connect signals to slots
        thread.started.connect(local_registrator.do_registration)
        local_registrator.signal_registration_done.connect(self.handle_registration_result)
        local_registrator.signal_finished.connect(thread.quit)
        local_registrator.signal_finished.connect(local_registrator.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        # time.sleep(1)
        self.progress_dialog.exec()

    def do_ransac_registration(self, voxel_size, mutual_filter, max_correspondence, estimation_method,
                               ransac_n, checkers, max_iteration, confidence):

        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2

        ransac_registrator = RANSACRegistrator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                               voxel_size, mutual_filter, max_correspondence,
                                               estimation_method, ransac_n, checkers, max_iteration, confidence)

        # Create thread
        thread = QThread(self)
        # Move worker to thread
        ransac_registrator.moveToThread(thread)
        # connect signals to slots
        thread.started.connect(ransac_registrator.do_registration)
        ransac_registrator.signal_registration_done.connect(self.handle_registration_result)
        ransac_registrator.signal_finished.connect(thread.quit)
        ransac_registrator.signal_finished.connect(ransac_registrator.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        self.progress_dialog.exec()

    def do_fgr_registration(self, voxel_size, division_factor, use_absolute_scale, decrease_mu, maximum_correspondence,
                            max_iterations, tuple_scale, max_tuple_count, tuple_test):
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2

        fgr_registrator = FGRRegistrator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                         voxel_size, division_factor, use_absolute_scale, decrease_mu,
                                         maximum_correspondence,
                                         max_iterations, tuple_scale, max_tuple_count, tuple_test)

        # Create thread
        thread = QThread(self)
        # Move worker to thread
        fgr_registrator.moveToThread(thread)
        # connect signals to slots
        thread.started.connect(fgr_registrator.do_registration)
        fgr_registrator.signal_registration_done.connect(self.handle_registration_result)
        fgr_registrator.signal_finished.connect(thread.quit)
        fgr_registrator.signal_finished.connect(fgr_registrator.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        self.progress_dialog.exec()

    def handle_registration_result(self, registration_result):
        self.progress_dialog.close()
        message_dialog = QMessageBox()
        message_dialog.setWindowTitle("Successful registration")
        message_dialog.setText(f"The registration of the point clouds is finished.\n"
                               f"The transformation will be applied.\n\n"
                               f"Fitness: {registration_result.fitness}\n"
                               f"RMSE: {registration_result.inlier_rmse}\n")
        message_dialog.exec()

        self.transformation_picker.set_transformation(registration_result.transformation)

    def do_multi_scale_registration(self, use_corresponding, sparse_first, sparse_second, registration_type,
                                    relative_fitness, relative_rmse, voxel_values, iter_values):
        pc1 = self.pane_open3d.pc1
        pc2 = self.pane_open3d.pc2

        multi_scale_registrator = MultiScaleRegistrator(pc1, pc2, self.transformation_picker.transformation_matrix,
                                                        use_corresponding, sparse_first, sparse_second,
                                                        registration_type, relative_fitness,
                                                        relative_rmse, voxel_values, iter_values)

        # Create thread
        thread = QThread(self)
        # Move worker to thread
        multi_scale_registrator.moveToThread(thread)
        # connect signals to slots
        thread.started.connect(multi_scale_registrator.do_registration)
        multi_scale_registrator.signal_registration_done.connect(self.handle_registration_result)
        multi_scale_registrator.signal_finished.connect(thread.quit)
        multi_scale_registrator.signal_finished.connect(multi_scale_registrator.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        self.progress_dialog.exec()

    def rasterize_gaussians(self, width, height, scale, color):
        pc1 = self.pc_originalFirst
        pc2 = self.pc_originalSecond

        extrinsic = self.pane_open3d.get_camera_extrinsic().astype(np.float32)
        intrinsic = self.pane_open3d.get_camera_intrinsic().astype(np.float32)
        rasterizer = RasterizerWorker(pc1, pc2, self.transformation_picker.transformation_matrix,
                                      extrinsic, intrinsic, scale, color, height, width)

        # Create thread
        thread = QThread(self)
        # Move worker to thread
        rasterizer.moveToThread(thread)
        # connect signals to slots
        thread.started.connect(rasterizer.do_rasterization)
        rasterizer.signal_rasterization_done.connect(self.create_raster_window)
        rasterizer.signal_finished.connect(thread.quit)
        rasterizer.signal_finished.connect(rasterizer.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        # TODO: Change progress dialog text and title
        self.progress_dialog.exec()

    def create_raster_window(self, pix):
        self.progress_dialog.close()
        self.raster_window = RasterImageViewer()
        self.raster_window.set_image(pix)
        self.raster_window.setWindowTitle("Rasterized point clouds")
        self.raster_window.setWindowModality(Qt.WindowModal)
        self.raster_window.show()
