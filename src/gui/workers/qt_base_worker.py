from PySide6.QtCore import Signal, QObject, QRunnable, QThread


class BaseWorker(QObject):
    signal_result = Signal(object)
    signal_finished = Signal()
    signal_error = Signal(list)
    signal_progress = Signal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        raise NotImplementedError


def move_worker_to_thread(worker: BaseWorker, result_handler, error_handler=None, progress_handler=None):
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.signal_result.connect(result_handler)
    worker.signal_finished.connect(thread.quit)
    worker.signal_finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    if error_handler is not None:
        worker.signal_error.connect(error_handler)

    if progress_handler is not None:
        worker.signal_progress.connect(progress_handler)

    return thread