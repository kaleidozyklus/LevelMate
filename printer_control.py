import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QGroupBox, QLabel, QDoubleSpinBox, QSpacerItem, QSizePolicy

class PrinterControl(QWidget):
    # Definieren von benutzerdefinierten Signalen
    home_button_clicked_signal = pyqtSignal()
    autolevel_bed_signal = pyqtSignal()
    load_mesh_button_clicked_signal = pyqtSignal()
    store_mesh_button_clicked_signal = pyqtSignal()
    target_bed_temperature_changed_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Form")
        self.setGeometry(100, 100, 733, 81)

        # Horizontal Layout for the ToolButtons
        horizontal_layout_2 = QHBoxLayout()

        # Horizontal Layout for the ToolButtons
        horizontal_layout_3 = QHBoxLayout()

        # Home button
        self.home_head_toolButton = QToolButton(self)
        self.home_head_toolButton.setText("Home")
        self.home_head_toolButton.clicked.connect(self.on_home_button_clicked)  # Signal connected to slot
        horizontal_layout_3.addWidget(self.home_head_toolButton)

        # Home button
        self.autolevel_bed_toolButton = QToolButton(self)
        self.autolevel_bed_toolButton.setText("Autolevel")
        self.autolevel_bed_toolButton.clicked.connect(self.on_autolevel_bed_button_clicked)  # Signal connected to slot
        horizontal_layout_3.addWidget(self.autolevel_bed_toolButton)

        # Load Mesh button
        self.toolButton_2 = QToolButton(self)
        self.toolButton_2.setText("Load Mesh")
        self.toolButton_2.clicked.connect(self.on_load_mesh_button_clicked)  # Signal connected to slot
        horizontal_layout_3.addWidget(self.toolButton_2)

        # Store Mesh button
        self.toolButton_3 = QToolButton(self)
        self.toolButton_3.setText("Store Mesh")
        self.toolButton_3.clicked.connect(self.on_store_mesh_button_clicked)  # Signal connected to slot
        horizontal_layout_3.addWidget(self.toolButton_3)

        horizontal_layout_2.addLayout(horizontal_layout_3)

        # Spacer between buttons and the GroupBox
        horizontal_spacer = QSpacerItem(155, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        horizontal_layout_2.addItem(horizontal_spacer)

        # Vertical Layout for the GroupBox
        vertical_layout_2 = QVBoxLayout()

        # GroupBox with temperature controls
        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle("")  # Empty title as in XML
        horizontal_layout = QHBoxLayout()

        # Bed Temperature Label
        self.label = QLabel("Bed Temperature", self)
        horizontal_layout.addWidget(self.label)

        # Target Bed Temperature SpinBox
        self.target_bed_temperature_doubleSpinBox = QDoubleSpinBox(self)
        self.target_bed_temperature_doubleSpinBox.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.target_bed_temperature_doubleSpinBox.setButtonSymbols(QDoubleSpinBox.PlusMinus)
        self.target_bed_temperature_doubleSpinBox.setSuffix("°C")
        self.target_bed_temperature_doubleSpinBox.setDecimals(1)
        self.target_bed_temperature_doubleSpinBox.setMaximum(100.0)
        self.target_bed_temperature_doubleSpinBox.valueChanged.connect(self.on_target_bed_temperature_changed)  # Signal connected to slot
        horizontal_layout.addWidget(self.target_bed_temperature_doubleSpinBox)

        # Current Bed Temperature SpinBox (Read-Only)
        self.current_bed_temperature_doubleSpinBox = QDoubleSpinBox(self)
        self.current_bed_temperature_doubleSpinBox.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.current_bed_temperature_doubleSpinBox.setReadOnly(True)
        self.current_bed_temperature_doubleSpinBox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.current_bed_temperature_doubleSpinBox.setSuffix("°C")
        self.current_bed_temperature_doubleSpinBox.setDecimals(1)
        horizontal_layout.addWidget(self.current_bed_temperature_doubleSpinBox)

        self.groupBox.setLayout(horizontal_layout)
        vertical_layout_2.addWidget(self.groupBox)

        # Add a spacer for vertical spacing
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vertical_layout_2.addItem(vertical_spacer)

        # Add the vertical layout to the main horizontal layout
        horizontal_layout_2.addLayout(vertical_layout_2)

        # Set the layout for the main window
        self.setLayout(horizontal_layout_2)

    def on_home_button_clicked(self):
        """Handle Home button click."""
        self.home_button_clicked_signal.emit()  # Emit the signal

    def on_autolevel_bed_button_clicked(self):
        self.autolevel_bed_signal.emit()  # Emit the signal

    def on_load_mesh_button_clicked(self):
        """Handle Load Mesh button click."""
        self.load_mesh_button_clicked_signal.emit()  # Emit the signal

    def on_store_mesh_button_clicked(self):
        """Handle Store Mesh button click."""
        self.store_mesh_button_clicked_signal.emit()  # Emit the signal

    def on_target_bed_temperature_changed(self, value):
        """Handle target bed temperature change."""
        self.target_bed_temperature_changed_signal.emit(value)  # Emit the signal with the new value

    def update_current_bed_temperature(self, value):
        self.current_bed_temperature_doubleSpinBox.setValue(value)

