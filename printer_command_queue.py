import sys
import time
from queue import Queue

import serial
from PyQt5.QtCore import QThread, QObject, QMetaObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication

# Worker-Klasse für Hintergrundaufgaben
class PrinterCommandQueue(QObject):
    execute_function_in_main_thread = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.task_queue = Queue()
        self.running = False
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.serial_connection = None

        self.execute_function_in_main_thread.connect(self.on_execute_function_in_main_thread)

    def connect(self, port, baud_rate):
        """Verbindet sich mit dem seriellen Port."""
        if not self.serial_connection:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            return True
        else:
            raise Exception("Serial connection already established.")

    def disconnect(self):
        """Trennt die serielle Verbindung."""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        else:
            raise Exception("Serial connection is not established.")

    def send_gcode(self, gcode, functor = None):
        """Fügt eine Aufgabe und ihren Functor hinzu."""
        self.task_queue.put(("gcode", gcode, functor))

    def add_command(self, functor):
        """Fügt eine Aufgabe und ihren Functor hinzu."""
        self.task_queue.put(("command", None, functor))

    def start(self):
        """Startet den Worker-Thread."""
        if not self.thread.isRunning():
            self.running = True
            self.thread.start()

    def stop(self):
        """Stoppt den Worker-Thread."""
        self.running = False
        self.thread.quit()
        self.thread.wait()

    def run(self):
        """Verarbeitet Aufgaben aus der Queue."""
        while self.running:
            if not self.task_queue.empty():
                type, gcode, functor = self.task_queue.get()
                try:
                    if type == "gcode":
                        if self.serial_connection:
                            # Sende das G-Code Kommando an die serielle Schnittstelle
                            print(f"Sending {gcode.rstrip('\n')}")
                            self.serial_connection.write((gcode + '\n').encode())
                            ok_received = False
                            response = ""
                            while not ok_received or self.serial_connection.in_waiting > 0:
                                QApplication.processEvents()
                                # Lese die Antwort und dekodiere sie
                                response += self.serial_connection.readline().decode('utf-8', errors='ignore')
                                ok_received = "ok" in response
                            if callable(functor):
                                self.execute_function_in_main_thread.emit( lambda : functor(response))
                        else:
                            raise Exception("Serial connection is not established.")
                    else:
                        self.execute_function_in_main_thread.emit(functor)
                except serial.SerialException as e:
                    raise Exception(f"Serial exception occurred: {e}")
                finally:
                    self.task_queue.task_done()
            else:
                time.sleep(0.1)  # Leerlauf, wenn keine Aufgaben vorhanden

    def on_execute_function_in_main_thread(self, functor):
        """Führt den Functor sicher im Haupt-Thread aus."""
        if callable(functor):
            functor()