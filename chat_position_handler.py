import logging
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox
import pyautogui

class ChatPositionHandler(QObject):
    position_set = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.chat_input_position = None

    def set_chat_position(self):
        QMessageBox.information(None, "Set Chat Position", "Click on the chat input field in 3 seconds.")
        QTimer.singleShot(3000, self._capture_chat_position)

    def _capture_chat_position(self):
        self.chat_input_position = pyautogui.position()
        logging.info(f"Chat input position set to: x={self.chat_input_position.x}, y={self.chat_input_position.y}")
        QMessageBox.information(None, "Success", "Chat position has been set.")
        self.position_set.emit(self.chat_input_position.x, self.chat_input_position.y)

    def get_chat_position(self):
        return self.chat_input_position

    def set_chat_position_from_settings(self, x, y):
        self.chat_input_position = pyautogui.Point(x=x, y=y)

    def has_position(self):
        return self.chat_input_position is not None

    def click_chat_input(self):
        if self.chat_input_position:
            pyautogui.click(self.chat_input_position.x, self.chat_input_position.y)
        else:
            logging.warning("Attempted to click chat input, but position is not set.")

    def type_message(self, message):
        if self.chat_input_position and message:
            self.click_chat_input()
            pyautogui.typewrite(str(message))  # Convert to string for safety
            pyautogui.press('enter')
        else:
            logging.warning("Attempted to type message, but chat input position is not set or message is empty.")