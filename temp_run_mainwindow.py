from splitter_app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys
app = QApplication([])
win = MainWindow(['Alice','Bob'], ['Food','Travel'])
print('OK constructed; has grip:', hasattr(win,'size_grip'))
