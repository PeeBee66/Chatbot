import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizeGrip
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
import pytesseract
from PIL import ImageGrab, Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class TransparentWindow(QWidget):
    text_captured = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_capturing = False
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture_text)
        self.previous_lines = set()

    def initUI(self):
        self.setWindowTitle('Chat Analyzer')
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

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
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def start_capture(self):
        self.is_capturing = True
        self.capture_timer.start(5000)  # Capture every 5 seconds

    def stop_capture(self):
        self.is_capturing = False
        self.capture_timer.stop()

    def capture_text(self):
        if self.is_capturing:
            try:
                x, y, w, h = self.geometry().getRect()
                screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
                screenshot = screenshot.resize((w*2, h*2), Image.LANCZOS)
                text = pytesseract.image_to_string(screenshot)
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line not in self.previous_lines:
                        self.previous_lines.add(line)
                        self.text_captured.emit(line)
                
            except Exception as e:
                print(f"Error capturing text: {str(e)}")