from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit

class CaptureControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.capture_button = QPushButton("Capture", self)
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

class ChatLogDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        layout.addWidget(QLabel("Chat log and information"))
        layout.addWidget(self.chat_log)
        self.setLayout(layout)

    def setup_logger(self, logger):
        class QTextEditLogger(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget

            def emit(self, record):
                msg = self.format(record)
                self.widget.append(msg)

        text_handler = QTextEditLogger(self.chat_log)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(text_handler)

class SettingsDisplay(QWidget):
    def __init__(self, prompt_text, my_username, other_usernames, parent=None):
        super().__init__(parent)
        self.initUI(prompt_text, my_username, other_usernames)

    def initUI(self, prompt_text, my_username, other_usernames):
        layout = QVBoxLayout()
        
        # Background Prompt
        layout.addWidget(QLabel("Background Prompt"))
        self.background_prompt = QTextEdit(self)
        self.background_prompt.setPlainText(prompt_text)
        self.background_prompt.setFixedHeight(4 * self.background_prompt.fontMetrics().lineSpacing())
        layout.addWidget(self.background_prompt)

        # Save and Settings buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        button_layout.addWidget(self.save_button)
        
        self.settings_button = QPushButton("Settings", self)
        button_layout.addWidget(self.settings_button)
        layout.addLayout(button_layout)
        
        # Username inputs
        username_layout = QHBoxLayout()
        self.my_username_input = QLineEdit(self)
        self.my_username_input.setText(my_username)
        self.my_username_input.setPlaceholderText("My username")
        username_layout.addWidget(QLabel("My Username:"))
        username_layout.addWidget(self.my_username_input)
        
        self.other_usernames_input = QLineEdit(self)
        self.other_usernames_input.setText(", ".join(other_usernames))
        self.other_usernames_input.setPlaceholderText("Other usernames (comma-separated)")
        username_layout.addWidget(QLabel("Other Usernames:"))
        username_layout.addWidget(self.other_usernames_input)
        layout.addLayout(username_layout)

        self.setLayout(layout)

    def update_settings(self, prompt_text, my_username, other_usernames):
        self.background_prompt.setPlainText(prompt_text)
        self.my_username_input.setText(my_username)
        self.other_usernames_input.setText(", ".join(other_usernames))

    def get_prompt(self):
        return self.background_prompt.toPlainText()

    def get_my_username(self):
        return self.my_username_input.text()

    def get_other_usernames(self):
        return [username.strip() for username in self.other_usernames_input.text().split(',') if username.strip()]

class LastCapturedDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.last_captured_line = QLineEdit(self)
        self.last_captured_line.setReadOnly(True)
        layout.addWidget(QLabel("Last Captured Line:"))
        layout.addWidget(self.last_captured_line)
        self.setLayout(layout)

    def update_last_captured(self, text):
        self.last_captured_line.setText(text)