from PyQt5.QtWidgets import QApplication, QFontDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QLineEdit, QColorDialog, QSpinBox, QGridLayout
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from backend import CountdownBackend
from threading import Thread
import numpy as np
import pyvirtualcam
import sys
import cv2
import winreg
from PIL import ImageFont, ImageDraw, Image

class CountdownApp(QWidget):
    def __init__(self):
        super().__init__()

        self.backend = CountdownBackend()
        self.initUI()
        self.cam_thread = None

    def initUI(self):
        self.font = QFont()
        self.bg_color = QColor(0, 0, 0)  # Default to black
        self.text_color = QColor(255, 255, 255)  # Default to white

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.time_entry = QLineEdit(self)
        self.grid.addWidget(self.time_entry, 0, 0, 1, 2)

        self.width_spinbox = QSpinBox(self)
        self.width_spinbox.setRange(1, 1920)
        self.width_spinbox.setValue(1920)
        self.grid.addWidget(self.width_spinbox, 1, 0)

        self.height_spinbox = QSpinBox(self)
        self.height_spinbox.setRange(1, 1080)
        self.height_spinbox.setValue(1080)
        self.grid.addWidget(self.height_spinbox, 1, 1)

        self.set_button = QPushButton('Set', self)
        self.set_button.clicked.connect(self.set_time)
        self.set_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.set_button, 2, 0)

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_countdown)
        self.start_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.start_button, 2, 1)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_countdown)
        self.stop_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.stop_button, 3, 0)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_countdown)
        self.reset_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.reset_button, 3, 1)

        self.start_cam_button = QPushButton('Start Camera', self)
        self.start_cam_button.clicked.connect(self.start_cam)
        self.start_cam_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.start_cam_button, 4, 0)

        self.stop_cam_button = QPushButton('Stop Camera', self)
        self.stop_cam_button.clicked.connect(self.stop_cam)
        self.stop_cam_button.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.stop_cam_button, 4, 1)

        self.fontButton = QPushButton('Choose font', self)
        self.fontButton.clicked.connect(self.showFontDialog)
        self.fontButton.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.fontButton, 5, 0)

        self.bgColorButton = QPushButton('Choose background color', self)
        self.bgColorButton.clicked.connect(self.showBgColorDialog)
        self.bgColorButton.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.bgColorButton, 5, 1)

        self.textColorButton = QPushButton('Choose text color', self)
        self.textColorButton.clicked.connect(self.showTextColorDialog)
        self.textColorButton.setStyleSheet("background-color: lightgreen")
        self.grid.addWidget(self.textColorButton, 6, 0)

        self.label = QLabel('00:00', self)
        self.label.setFont(self.font)
        self.label.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.label, 7, 0, 1, 2)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Countdown App')
        self.show()

    def showFontDialog(self):
        font, ok = QFontDialog.getFont()

        if ok:
            self.font = font
            self.label.setFont(self.font)

    def showBgColorDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.bg_color = color

    def showTextColorDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.text_color = color

    def set_time(self):
        if self.backend.validate_time(self.time_entry.text()):
            self.backend.time_str = self.time_entry.text()
        else:
            QMessageBox.critical(self, "Invalid Time", "Please enter time in mm:ss format")

    def start_countdown(self):
        if self.backend.validate_time(self.time_entry.text()):
            self.backend.start_countdown(self.time_entry.text())
        else:
            QMessageBox.critical(self, "Invalid Time", "Please enter time in mm:ss format")

    def stop_countdown(self):
        self.backend.stop_countdown()

    def reset_countdown(self):
        self.backend.reset_countdown()
        self.time_entry.setText(self.backend.time_str)

    def start_cam(self):
        if self.cam_thread is None:
            self.cam_thread = Thread(target=self.show_on_virtual_cam)
            self.cam_thread.start()

    def stop_cam(self):
        if self.cam_thread is not None:
            self.cam_thread = None

    @staticmethod
    def get_font_file(font_name):
        # Open the Windows fonts registry key
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')

        # Loop over the values in the key
        for i in range(winreg.QueryInfoKey(key)[1]):
            value = winreg.EnumValue(key, i)
            if value[0].startswith(font_name):
                return value[1]

        return None

    def show_on_virtual_cam(self):
        with pyvirtualcam.Camera(width=self.width_spinbox.value(), height=self.height_spinbox.value(), fps=20) as cam:
            while self.cam_thread is not None:
                img = np.zeros((cam.height, cam.width, 3), np.uint8)
                img[:] = self.bg_color.getRgb()[:3]  # Set the background color

                # Convert the image to PIL format.
                pil_img = Image.fromarray(img)

                # Create a draw object.
                draw = ImageDraw.Draw(pil_img)

                # Get the font file from the Windows Registry
                font_file = self.get_font_file(self.font.toString().split(",")[0])
                if font_file is not None:
                    # Load the font and calculate the text size.
                    font = ImageFont.truetype(font_file, self.font.pointSize() * 10)
                    text_width, text_height = draw.textsize(self.backend.time_str, font)

                    # Calculate the position for the text to be centered.
                    textX = (img.shape[1] - text_width) // 2
                    textY = (img.shape[0] - text_height) // 2

                    # Draw the text on the image.
                    draw.text((textX, textY), self.backend.time_str, font=font, fill=self.text_color.getRgb()[:3])

                # Convert the image back to OpenCV format.
                img = np.array(pil_img)

                # Convert the image from BGR to RGB.
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Convert the image to the correct format and send it to the virtual webcam.
                frame = np.flip(rgb_img, 2).astype(np.uint8)
                cam.send(frame)

                # Sleep until the next frame should be sent.
                cam.sleep_until_next_frame()