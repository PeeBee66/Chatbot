import sys
from PyQt5.QtWidgets import QApplication
from ui import PipsChatAnalyserUI

def main():
    app = QApplication(sys.argv)
    main_window = PipsChatAnalyserUI()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()