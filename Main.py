import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui import PipsChatAnalyserUI

def setup_logging():
    logging.basicConfig(
        filename='app.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def exception_hook(exctype, value, tb):
    logging.critical('Unhandled exception:', exc_info=(exctype, value, tb))
    error_msg = f"An unhandled exception occurred:\n{exctype.__name__}: {str(value)}\n\nTraceback:\n{''.join(traceback.format_tb(tb))}"
    print(error_msg)  # Print to console as well
    QMessageBox.critical(None, "Critical Error", error_msg)
    sys.__excepthook__(exctype, value, tb)

def main():
    setup_logging()
    sys.excepthook = exception_hook
    logging.info("Starting PIPS CHAT ANALYSER")
    
    try:
        app = QApplication(sys.argv)
    except Exception as e:
        logging.critical(f"Error creating QApplication: {str(e)}", exc_info=True)
        print(f"Error creating QApplication: {str(e)}")
        return

    try:
        main_window = PipsChatAnalyserUI()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Critical error in main application: {str(e)}", exc_info=True)
        print(f"Critical error in main application: {str(e)}")

if __name__ == "__main__":
    main()