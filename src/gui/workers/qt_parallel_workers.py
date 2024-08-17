from threading import Lock

from PySide6.QtCore import Slot, Signal, QThreadPool, QObject

from src.gui.workers.qt_base_worker import BaseWorker


class ParrallelWorker(QObject):
    finished = Signal(object, object)
    lock = Lock()

    def __init__(self, worker1: BaseWorker, worker2: BaseWorker):
        super().__init__()
        self.worker1 = worker1
        self.worker2 = worker2
        self.worker1.worker_id = 0
        self.worker2.worker_id = 1
        self.worker1.signals.result.connect(self.handle_result_single)
        self.worker2.signals.result.connect(self.handle_result_single)
        self.worker1.signals.finished.connect(self.check_completion)
        self.worker2.signals.finished.connect(self.check_completion)

        self.results = [None, None]
        self.tasks_completed = 0

    def run(self):
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(self.worker1)
        thread_pool.start(self.worker2)

    @Slot(int, int)
    def handle_result_single(self, worker_id, result):
        with self.lock:
            self.results[worker_id] = result

    @Slot()
    def check_completion(self):
        with self.lock:
            self.tasks_completed += 1
            if self.tasks_completed != 2:
                return
            self.finished.emit(*self.results)
