import time
from threading import Lock

from PySide6.QtCore import Slot, Signal, QObject, QThread

from src.gui.workers.qt_base_worker import BaseWorker


class ParallelWorker(QObject):
    finished = Signal(object, object)

    def __init__(self, worker1: BaseWorker, worker2: BaseWorker):
        super().__init__()
        self.lock = Lock()
        self.workers = [worker1, worker2]
        self.workers[0].worker_id = 0
        self.workers[1].worker_id = 1

        self.results = [None, None]
        self.tasks_completed = 0

        # Create threads for each worker
        self.threads = [QThread(), QThread()]

        # Assign workers to threads
        self.workers[0].moveToThread(self.threads[0])
        self.workers[1].moveToThread(self.threads[1])

        # Connect the workers' signals to the appropriate slots
        self.workers[0].signals.result.connect(self.handle_result_single)
        self.workers[1].signals.result.connect(self.handle_result_single)

        # Connect the thread start to the worker's run method
        self.threads[0].started.connect(self.workers[0].run)
        self.threads[1].started.connect(self.workers[1].run)

        # Ensure threads are properly cleaned up
        self.threads[0].finished.connect(self.threads[0].deleteLater)
        self.threads[1].finished.connect(self.threads[1].deleteLater)

    def run(self):
        self.time1 = time.time()

        # Start the threads (which in turn starts the workers)
        self.threads[0].start()
        self.threads[1].start()

    @Slot(int, int)
    def handle_result_single(self, worker_id, result):
        with self.lock:
            self.results[worker_id] = result
            all_results_ready = self.results[0] is not None and self.results[1] is not None

        if all_results_ready:
            self.time2 = time.time()
            print(self.time2 - self.time1)
            self.finished.emit(*self.results)

        # Stop the threads after processing the result
        self.threads[worker_id].quit()
        self.threads[worker_id].wait()
