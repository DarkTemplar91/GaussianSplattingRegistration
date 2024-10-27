from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter

from gui.windows.visualization.fx.temporal_filter import TemporalFilter


class TemporalAntiAliasing:
    def __init__(self, base_alpha=0.1, high_alpha=0.5, decay=0.95, max_frames=5):
        self.base_alpha = base_alpha
        self.high_alpha = high_alpha
        self.decay = decay
        self.max_frames = max_frames
        self.accumulated_frame = None
        self.frame_count = 0
        self.temporal_filter = TemporalFilter()

    def apply_taa(self, new_frame: QPixmap):
        filtered_frame = self.temporal_filter.apply_temporal_filter(new_frame)

        if self.frame_count % 30 == 0:
            self.accumulated_frame = None
            self.frame_count = 0

        if self.accumulated_frame is None:
            self.accumulated_frame = filtered_frame.copy()
            return self.accumulated_frame

        faded_frame = QPixmap(self.accumulated_frame.size())
        faded_frame.fill(Qt.QPtransparent)
        painter = QPainter(faded_frame)
        painter.setOpacity(self.decay)  # Apply decay to accumulated frame
        painter.drawPixmap(0, 0, self.accumulated_frame)
        painter.end()

        # Use a higher alpha for new frames (to reduce ghosting)
        alpha = self.high_alpha if self.frame_count % 2 == 0 else self.base_alpha

        painter = QPainter(faded_frame)
        painter.setOpacity(alpha)
        painter.drawPixmap(0, 0, filtered_frame)
        painter.end()

        self.accumulated_frame = faded_frame
        self.frame_count += 1

        return self.accumulated_frame
