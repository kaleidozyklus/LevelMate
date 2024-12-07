# main.py

import sys
import re

import serial
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from mesh_point_grid import MeshPointGrid  # Importiere das ausgelagerte Widget
from printer_connection_settings import PrinterConnectionSettings  # Importiere das ausgelagerte Widget
from printer_control import PrinterControl
from printer_command_queue import PrinterCommandQueue

class LevelMate(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Level Mate - 3D Printer Leveling Helper")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("printer_icon.png"))

        self.printerCommandQueue = PrinterCommandQueue()

        self.z_head_lift_for_moving = 50.0

        self.gcode_in_process = False

        # UI Setup
        self.init_ui()

        # Starte den Timer mit einem Intervall von 1 Sekunde (1000 ms)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_update_temperatures)
        self.timer.start(5000)

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
        self.printer_control.autolevel_bed_signal.connect(self.on_autolevel_bed)
        self.printer_control.load_mesh_button_clicked_signal.connect(self.on_load_mesh)
        self.printer_control.store_mesh_button_clicked_signal.connect(self.on_store_mesh)

        self.printer_control.target_bed_temperature_changed_signal.connect(self.on_set_target_bed_temperature)

    @QtCore.pyqtSlot()
    def on_establish_connection(self):
        """Wird aufgerufen, wenn der Connect-Button geklickt wird."""
        port = self.printer_connection_settings.get_selected_port()
        baudrate = self.printer_connection_settings.get_selected_baudrate()

        if self.printerCommandQueue.connect(port, baudrate):
            self.printerCommandQueue.start()
            self.printer_connection_settings.set_connection_status(True)
            self.load_bed_levels()

    @QtCore.pyqtSlot()
    def on_shutdown_connection(self):
        self.printerCommandQueue.stop()
        self.printerCommandQueue.disconnect()
        self.printer_connection_settings.set_connection_status(False)

    @QtCore.pyqtSlot()
    def on_home_head(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.home_head()
        self.printerCommandQueue.add_command(QApplication.restoreOverrideCursor)

    @QtCore.pyqtSlot()
    def on_autolevel_bed(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.home_head()
        self.autolevel_bed()
        self.load_bed_levels()
        self.printerCommandQueue.add_command(QApplication.restoreOverrideCursor)

    @QtCore.pyqtSlot()
    def on_load_mesh(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.load_bed_levels()
        self.printerCommandQueue.add_command(QApplication.restoreOverrideCursor)

    @QtCore.pyqtSlot()
    def on_store_mesh(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.store_bed_levels()
        self.printerCommandQueue.add_command(QApplication.restoreOverrideCursor)

    @QtCore.pyqtSlot(int, int, float)
    def on_move_head_to_position(self, row, col, z):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.move_head_to_position(row, col, z)
        self.printerCommandQueue.add_command(QApplication.restoreOverrideCursor)

    ###

    def home_head(self):
        self.printerCommandQueue.send_gcode("G28")
        self.printerCommandQueue.send_gcode("M400")
        self.printerCommandQueue.send_gcode("M114")

    def autolevel_bed(self):
        self.printerCommandQueue.send_gcode("G29")
        self.printerCommandQueue.send_gcode("M400")
        self.printerCommandQueue.send_gcode("M114")

    def load_bed_levels(self):
        self.printerCommandQueue.send_gcode("M420 V", lambda response : self.set_bed_levels_from_response(response))

    def set_bed_levels_from_response(self, response):
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

    def store_bed_levels(self):
        if self.serial_connection:
            for i in range(5):
                for j in range(5):
                    value = self.mesh_point_grid.get_value(i, j)
                    self.printerCommandQueue.send_gcode(f"M421 I{j} J{i} Z{value}")

    def move_head_to_position(self, row, col, z):
        self.printerCommandQueue.send_gcode(f"G0 Z{self.z_head_lift_for_moving}")
        self.printerCommandQueue.send_gcode(f"G42 I{col} J{row}")
        self.printerCommandQueue.send_gcode(f"G0 Z{z}")
        self.printerCommandQueue.send_gcode(f"M400")
        self.printerCommandQueue.send_gcode(f"M114")

        self.mesh_point_grid.set_head_is_positioned_at(row, col)

    def on_mesh_bed_level_point_value_changed(self, row, col, value):
        self.printerCommandQueue.send_gcode(f"G0 Z{value}")

    @QtCore.pyqtSlot(float)
    def on_set_target_bed_temperature(self, target_bed_temperature):
        self.printerCommandQueue.send_gcode(f"M140 S{round(target_bed_temperature)}")

    @QtCore.pyqtSlot()
    def on_update_temperatures(self):
        self.printerCommandQueue.send_gcode("M105", lambda response : self.update_temperatures_from_response(response))

    def update_temperatures_from_response(self, response):
        if response:
            match = re.search(r"B:(\d+\.\d+)", response)
            if match:
                bed_temperature = float(match.group(1))
                self.printer_control.update_current_bed_temperature(bed_temperature)

    def set_bed_temperature(self, bed_temperature):
        self.printerCommandQueue.send_gcode(f"M140 S{bed_temperature}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LevelMate()
    window.show()
    sys.exit(app.exec_())
