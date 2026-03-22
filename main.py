import sys
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from db.database import initialize_db
from ui.main_window import MainWindow

def handle_exception(exc_type, exc_value, exc_traceback):
    with open("error.log", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

if __name__ == '__main__':
    initialize_db()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('assets/matometor.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())