import os
import tempfile
import qrcode
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
import logging

class QRCodeApp(QtWidgets.QWidget):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger("QRCG_Fallback")

        # Locate the UI file
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(plugin_dir, "QRCG.ui")

        try:
            uic.loadUi(ui_path, self)
            self.logger.info("UI file loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load UI file: {ui_path}. Error: {e}")
            raise

        self.setup_ui()

    def setup_ui(self):
        # Connect UI elements
        self.lineEdit_qr_data = self.findChild(QtWidgets.QLineEdit, "lineEdit_qr_data")
        self.sel_qr_version = self.findChild(QtWidgets.QComboBox, "sel_qr_version")
        self.lineEdit_file_name = self.findChild(QtWidgets.QLineEdit, "lineEdit_file_name")
        self.lineEdit_box_size = self.findChild(QtWidgets.QLineEdit, "lineEdit_box_size")
        self.lineEdit_border_size = self.findChild(QtWidgets.QLineEdit, "lineEdit_border_size")
        self.button_generate = self.findChild(QtWidgets.QPushButton, "button_generate")
        self.button_save = self.findChild(QtWidgets.QPushButton, "button_save")
        self.label_qr_display = self.findChild(QtWidgets.QLabel, "label_qr_display")
        self.sel_qr_err = self.findChild(QtWidgets.QComboBox, "sel_qr_err")

        # Connect the buttons to the functions
        self.button_generate.clicked.connect(self.generate_qr_code)
        self.button_save.clicked.connect(self.save_qr_code)

        self.temp_file = None

        self.logger.info("UI setup complete.")

    def generate_qr_code(self):
        qr_data = self.lineEdit_qr_data.text().strip()
        qr_version = self.sel_qr_version.currentText()
        err_correction = self.sel_qr_err.currentText()

        if not qr_data:
            QtWidgets.QMessageBox.warning(self, "Input Error", "QR Data is required!")
            self.logger.warning("QR Data field is empty. Cannot generate QR Code.")
            return

        err_correction_map = {
            "Level L  (Approx 7%)": qrcode.constants.ERROR_CORRECT_L,
            "Level M (Approx 15%)": qrcode.constants.ERROR_CORRECT_M,
            "Level Q (Approx 25%)": qrcode.constants.ERROR_CORRECT_Q,
            "Level H (Approx 30%)": qrcode.constants.ERROR_CORRECT_H,
        }
        err_correction_level = err_correction_map.get(err_correction, qrcode.constants.ERROR_CORRECT_L)

        try:
            box_size = int(self.lineEdit_box_size.text())
            border_size = int(self.lineEdit_border_size.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Box size and border size must be integers!")
            self.logger.warning("Invalid input for box size or border size. Must be integers.")
            return

        try:
            qr = qrcode.QRCode(
                version=int(qr_version),
                error_correction=err_correction_level,
                box_size=box_size,
                border=border_size,
            )

            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(self.temp_file.name)
            self.display_qr_code(self.temp_file.name)
            self.logger.info("QR Code generated successfully.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to generate QR Code: {e}")
            self.logger.error(f"QR Code generation failed. Error: {e}")

    def display_qr_code(self, filename):
        try:
            pixmap = QPixmap(filename)
            self.label_qr_display.setPixmap(pixmap)
            self.logger.info("QR Code displayed successfully.")
        except Exception as e:
            self.logger.error(f"Failed to display QR Code. Error: {e}")

    def save_qr_code(self):
        if not self.temp_file:
            QtWidgets.QMessageBox.warning(self, "Error", "No QR Code to save. Please generate one first.")
            self.logger.warning("Save operation attempted without a generated QR Code.")
            return

        file_name = self.lineEdit_file_name.text().strip()
        if not file_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Please specify a file name.")
            self.logger.warning("No file name provided for saving the QR Code.")
            return

        output_path = os.path.abspath(file_name + ".png")

        try:
            os.rename(self.temp_file.name, output_path)
            self.temp_file = None
            QtWidgets.QMessageBox.information(self, "Success", f"QR Code saved at: {output_path}")
            self.logger.info(f"QR Code saved successfully at: {output_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save QR Code: {e}")
            self.logger.error(f"Failed to save QR Code. Error: {e}")

    def closeEvent(self, event):
        if self.temp_file:
            try:
                os.remove(self.temp_file.name)
                self.logger.info("Temporary QR Code file deleted successfully.")
            except Exception as e:
                self.logger.warning(f"Failed to delete temporary QR Code file. Error: {e}")
        event.accept()


def main(parent_widget=None, parent_logger=None):
    if parent_logger:
        plugin_logger = parent_logger.getChild("QRCG")
    else:
        plugin_logger = logging.getLogger("QRCG_Fallback")

    plugin_logger.info("QRCG Plugin initialized.")
    return QRCodeApp(parent_widget, plugin_logger)
