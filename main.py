from backend import CountdownBackend
from app import CountdownApp
from PyQt5.QtWidgets import QApplication
import sys
from threading import Thread

def main():
    app = QApplication(sys.argv)
    ex = CountdownApp()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
