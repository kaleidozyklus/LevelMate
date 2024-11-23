# main.py

import sys
import time
from http.client import responses

import serial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

from printer_connection_settings import PrinterConnectionSettings  # Importiere das ausgelagerte Widget
from mesh_point_grid import MeshPointGrid  # Importiere das ausgelagerte Widget
from printer_control import PrinterControl


class PrinterLevelingHelperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Printer Leveling Helper")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("printer_icon.png"))

        self.serial_connection = None
        self.baud_rate = 115200

        self.z_head_lift_for_moving = 50.0

        self.gcode_in_process = False

        # UI Setup
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.printer_connection_settings = PrinterConnectionSettings(self)
        layout.addWidget(self.printer_connection_settings)

        self.printer_control = PrinterControl(self)
        layout.addWidget(self.printer_control)

        self.mesh_point_grid = MeshPointGrid(self)
        layout.addWidget(self.mesh_point_grid)

        self.printer_connection_settings.establish_connection.connect(self.on_establish_connection)
        self.printer_connection_settings.shutdown_connection.connect(self.on_shutdown_connection)

        self.mesh_point_grid.moveHeadToPosition.connect(self.on_move_head_to_position)
        self.mesh_point_grid.valueChanged.connect(self.on_mesh_bed_level_point_value_changed)

        self.printer_control.home_button_clicked_signal.connect(self.on_home_head)
        self.printer_control.load_mesh_button_clicked_signal.connect(self.on_load_mesh)

    @QtCore.pyqtSlot()
    def on_establish_connection(self):
        """Wird aufgerufen, wenn der Connect-Button geklickt wird."""
        port = self.printer_connection_settings.get_selected_port()
        baudrate = self.printer_connection_settings.get_selected_baudrate()

        self.serial_connection = serial.Serial(port=port, baudrate=baudrate)
        if self.serial_connection:
            self.printer_connection_settings.set_connection_status(True)
            self.load_bed_levels()

    @QtCore.pyqtSlot()
    def on_shutdown_connection(self):
        """Wird aufgerufen, wenn der Disconnect-Button geklickt wird."""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            self.printer_connection_settings.set_connection_status(False)

    def send_gcode_command(self, gcode_command):
        try:
            if self.serial_connection:
                self.gcode_in_process = True
                # Sende das G-Code Kommando an die serielle Schnittstelle
                self.serial_connection.write((gcode_command + '\n').encode())
                ok_received = False
                response = ""
                while not ok_received:
                    QApplication.processEvents()
                    # Lese die Antwort und dekodiere sie
                    response += self.serial_connection.readline().decode('utf-8', errors='ignore')
                    ok_received = response.endswith("ok\n") and self.serial_connection.in_waiting == 0
                self.gcode_in_process = False
                return response
            else:
                self.gcode_in_process = False
                raise Exception("Serial connection is not established.")
        except serial.SerialException as e:
            self.gcode_in_process = False
            raise Exception(f"Serial exception occurred: {e}")

    @QtCore.pyqtSlot()
    def on_home_head(self):
        self.setCursor(Qt.WaitCursor)
        self.home_head()
        self.setCursor(Qt.ArrowCursor)

    def home_head(self):
        if self.serial_connection:
            self.send_gcode_command("G28")
            self.send_gcode_command("M400")
            self.send_gcode_command("M114")


    @QtCore.pyqtSlot()
    def on_load_mesh(self):
        self.setCursor(Qt.WaitCursor)
        self.load_bed_levels()
        self.setCursor(Qt.ArrowCursor)

    def load_bed_levels(self):
        if self.serial_connection:
            # Lade die aktuellen Bettleveling-Werte
            response = self.send_gcode_command("M420 V")

            if response:
                # Parse die Antwort und extrahiere die Bettleveling-Werte
                bed_levels = []
                parsing_grid = False
                for line in response.split("\n"):
                    if line.startswith("Bilinear Leveling Grid:"):
                        parsing_grid = True
                        continue
                    if parsing_grid:
                        if line.strip() == "":
                            parsing_grid = False
                            continue
                        # Extrahiere die Bettleveling-Werte aus der Antwort
                        values = line.split()[1:]  # Ignoriere die erste Spalte (Index)
                        bed_levels.append([round(float(value), 2) for value in values])

                # Skippe die erste Zeile (Index)
                bed_levels = bed_levels[1:]

                for row, row_values in enumerate(bed_levels):
                    for col, value in enumerate(row_values):
                        self.mesh_point_grid.set_value(row, col, value)

            else:
                return None

    def on_move_head_to_position(self, row, col, z):
        if self.serial_connection:
            self.setCursor(Qt.WaitCursor)
            self.move_head_to_position(row, col, z)
            self.setCursor(Qt.ArrowCursor)

    def move_head_to_position(self, row, col, z):
        if self.serial_connection:
            self.send_gcode_command(f"G0 Z{self.z_head_lift_for_moving}")
            self.send_gcode_command(f"G42 I{col} J{row}")
            self.send_gcode_command(f"G0 Z{z}")

            self.send_gcode_command(f"M400")
            self.send_gcode_command(f"M114")

            self.mesh_point_grid.set_head_is_positioned_at(row, col)

    def on_mesh_bed_level_point_value_changed(self, row, col, value):
        if self.serial_connection:
            self.send_gcode_command(f"G0 Z{value}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PrinterLevelingHelperApp()
    window.show()
    sys.exit(app.exec_())
