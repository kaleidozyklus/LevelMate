import sys
import serial
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QHBoxLayout

class PrinterConnectionSettings(QWidget):
    # Signale für Verbindung und Trennung
    establish_connection = QtCore.pyqtSignal()  # Port und Baudrate als Argumente
    shutdown_connection = QtCore.pyqtSignal()           # Kein Argument für Trennung

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_connected = False  # Status privat halten
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Dropdown für Baudrate
        self.baudrate_combo = QComboBox(self)
        baud_rates = [
            "9600", "14400", "19200", "38400", "57600",
            "115200", "250000", "500000", "1000000"
        ]
        self.baudrate_combo.addItems(baud_rates)
        self.baudrate_combo.setCurrentText("115200")
        layout.addWidget(self.baudrate_combo)

        # Dropdown für verfügbare Ports
        self.port_combo = QComboBox(self)
        self.port_combo.setCurrentText("")
        layout.addWidget(self.port_combo)

        # Buttons für Verbindung und Trennung
        self.establish_connection_button = QPushButton("Connect", self)
        self.establish_connection_button.clicked.connect(self.on_establish_connection)
        layout.addWidget(self.establish_connection_button)

        self.shutdown_connection_button = QPushButton("Disconnect", self)
        self.shutdown_connection_button.clicked.connect(self.on_shutdown_connection)
        layout.addWidget(self.shutdown_connection_button)

        # Initialisierung von Ports und UI
        self.update_available_ports()
        self.update_ui()

    def update_available_ports(self):
        """Gibt alle verfügbaren seriellen Ports zurück."""
        ports = []
        for i in range(256):
            port = f"COM{i}" if sys.platform == "win32" else f"/dev/ttyUSB{i}"
            try:
                ser = serial.Serial(port=port)
                ser.isOpen()
                ports.append(port)
            except IOError:
                continue

        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def update_ui(self):
        """Aktualisiert den Status der UI basierend auf dem Verbindungsstatus."""
        self.baudrate_combo.setEnabled(not self._is_connected)
        self.port_combo.setEnabled(not self._is_connected)
        self.establish_connection_button.setEnabled(not self._is_connected)
        self.shutdown_connection_button.setEnabled(self._is_connected)

    def on_establish_connection(self):
        """Wird aufgerufen, wenn der Connect-Button geklickt wird."""
        port = self.port_combo.currentText()
        baudrate = int(self.baudrate_combo.currentText())
        self.establish_connection.emit()

    def on_shutdown_connection(self):
        """Wird aufgerufen, wenn der Disconnect-Button geklickt wird."""
        if self._is_connected:
            self.shutdown_connection.emit()

    @QtCore.pyqtSlot(bool)
    def set_connection_status(self, status):
        """Extern aufrufbarer Slot, um den Verbindungsstatus zu setzen."""
        self._is_connected = status
        self.update_ui()

    def get_selected_port(self):
        """Gibt den aktuell ausgewählten Port zurück."""
        return self.port_combo.currentText()

    def get_selected_baudrate(self):
        """Gibt die aktuell ausgewählte Baudrate als Integer zurück."""
        return int(self.baudrate_combo.currentText())
