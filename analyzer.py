import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizeGrip
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QColor, QPen
import pytesseract
from PIL import ImageGrab, Image

logging.basicConfig(filename='chat_analyzer_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TransparentWindow(QWidget):
    text_captured = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.min_size = QSize(300, 150)  # Changed minimum height to 150
        self.initUI()
        self.oldPos = None
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        logging.info(f"Tesseract path set to: {pytesseract.pytesseract.tesseract_cmd}")

    def initUI(self):
        self.setWindowTitle('Chat Analyzer')
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(self.min_size)

        layout = QVBoxLayout()
        self.setLayout(layout)

        size_grip = QSizeGrip(self)
        layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.SolidLine))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() < self.min_size.width() or self.height() < self.min_size.height():
            self.setGeometry(self.x(), self.y(), max(self.width(), self.min_size.width()), max(self.height(), self.min_size.height()))
            logging.warning(f"Window resized to minimum size: {self.size()}")

    def capture_screen(self):
        try:
            logging.debug("Attempting to capture screen")
            x, y, w, h = self.geometry().getRect()
            logging.info(f"Capture size: {w}x{h}")  # Log capture size
            
            screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            screenshot = screenshot.resize((w * 2, h * 2), Image.LANCZOS)
            
            screenshot.save("debug_screenshot.png")
            logging.debug(f"Screenshot saved: debug_screenshot.png")

            # Improve OCR accuracy
            text = pytesseract.image_to_string(screenshot, config='--psm 6 --oem 3')
            logging.debug(f"Captured text length: {len(text)}")
            if not text:
                logging.warning("No text captured by Tesseract")
            else:
                logging.debug(f"Captured text: {text[:100]}...")  # Log first 100 characters
            return text
        except Exception as e:
            logging.error(f"Error capturing screen: {str(e)}")
            return ""