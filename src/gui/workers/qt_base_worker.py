from PySide6.QtCore import Signal, QObject, QRunnable


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(list)
    result = Signal(int, object)
    progress = Signal(int)


class BaseWorker(QObject):
    worker_id: int

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @property
    def is_valid(self):
        return self.worker_id != -1

    def run(self):
        raise NotImplementedError
