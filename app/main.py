import sys

from PyQt6.QtWidgets import QApplication

from window import Window
import warnings
warnings.filterwarnings("ignore")
app = QApplication(sys.argv)
window = Window() 
window.show()
sys.exit(app.exec())
