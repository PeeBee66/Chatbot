import logging
import pytesseract
from PIL import Image, ImageGrab, ImageOps, ImageEnhance
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizeGrip, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QPen
import traceback

class TransparentWindow(QWidget):
    text_captured = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.min_size = QSize(50, 50)
        self.border_width = 2
        self.corner_size = 10
        self.capture_inset = 5
        self.capture_reduction = 1
        self.buffer_zone = 20  # New: Buffer zone size in pixels
        self.recent_lines = []  # New: List to store recent lines
        self.max_recent_lines = 20  # New: Maximum number of recent lines to store
        self.initUI()
        self.oldPos = None
        
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        logging.info(f"Tesseract path set to: {pytesseract.pytesseract.tesseract_cmd}")
        
        try:
            logging.info(f"Tesseract version: {pytesseract.get_tesseract_version()}")
        except Exception as e:
            logging.error(f"Error getting Tesseract version: {str(e)}")

    def initUI(self):
        self.setWindowTitle('Chat Analyzer')
        self.setGeometry(100, 100, 400, 250)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(self.min_size)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.close_button = QPushButton("X", self)
        self.close_button.setStyleSheet("background-color: grey; color: white;")
        self.close_button.setFixedSize(15, 15)
        self.close_button.clicked.connect(self.close)
        
        size_grip = QSizeGrip(self)
        layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        
        painter.setPen(QPen(QColor(255, 255, 255), self.border_width, Qt.SolidLine))
        painter.drawRect(self.rect().adjusted(self.border_width//2, self.border_width//2, -self.border_width//2, -self.border_width//2))
        
        capture_area = self.get_visible_capture_area()
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
        painter.drawRect(capture_area)

        self.close_button.move(self.width() - self.close_button.width(), 0)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def get_visible_capture_area(self):
        return self.rect().adjusted(
            self.border_width + self.capture_inset,
            self.border_width + self.capture_inset,
            -self.corner_size - self.border_width - self.capture_inset,
            -self.corner_size - self.border_width - self.capture_inset
        )

    def get_actual_capture_area(self):
        visible_area = self.get_visible_capture_area()
        return visible_area.adjusted(
            self.capture_reduction,
            self.capture_reduction + self.buffer_zone,  # Added buffer zone
            -self.capture_reduction,
            -self.capture_reduction
        )

    def capture_screen(self):
        try:
            logging.debug("Entering capture_screen method")
            
            capture_area = self.get_actual_capture_area()
            top_left = self.mapToGlobal(capture_area.topLeft())
            x, y = top_left.x(), top_left.y()
            w, h = capture_area.width(), capture_area.height()
            logging.info(f"Capture coordinates: x={x}, y={y}, w={w}, h={h}")
            
            screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            screenshot.save("debug_screenshot.png")
            
            screenshot = screenshot.convert('L')
            screenshot = ImageOps.invert(screenshot)
            enhancer = ImageEnhance.Contrast(screenshot)
            screenshot = enhancer.enhance(2)
            
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(screenshot, config=custom_config)
            
            unique_text = self.process_new_text(text)
            
            logging.debug(f"OCR completed. Captured text length: {len(unique_text)}")
            if not unique_text:
                logging.warning("No new text captured")
            else:
                logging.debug(f"Captured text: {unique_text}")
                self.text_captured.emit(unique_text)
            
            return unique_text
        except Exception as e:
            logging.error(f"Unexpected error in capture_screen: {str(e)}")
            logging.error(traceback.format_exc())
            return ""

    def process_new_text(self, text):
        new_lines = text.split('\n')
        unique_new_lines = []
        
        for line in new_lines:
            line = line.strip()
            if line and line not in self.recent_lines:
                unique_new_lines.append(line)
        
        # Update recent lines
        self.recent_lines = (self.recent_lines + unique_new_lines)[-self.max_recent_lines:]
        
        return '\n'.join(unique_new_lines)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.close_button.move(self.width() - self.close_button.width(), 0)

    def closeEvent(self, event):
        logging.info("Closing TransparentWindow")
        super().closeEvent(event)