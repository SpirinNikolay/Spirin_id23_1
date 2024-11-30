import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QPushButton, QSpinBox, QFormLayout, QDialog
)
from PyQt5.QtGui import QPainter, QColor, QMouseEvent
from PyQt5.QtCore import QTimer, Qt

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
MENU_HEIGHT = 100


class Wave:
    def __init__(self, amplitude, period, speed, offset):
        self.amplitude = amplitude
        self.period = period
        self.speed = speed
        self.position = 0
        self.offset = offset

    def update(self):
        self.position += self.speed / FPS

    def get_y(self, x):
        return self.amplitude * np.sin((2 * np.pi / self.period) * (x - self.position)) + self.offset


class Buoy:
    def __init__(self, wave, mass=1, size=20):
        self.wave = wave
        self.x_position = np.random.randint(0, WINDOW_WIDTH)
        self.y_position = self.wave.get_y(self.x_position)
        self.mass = mass
        self.size = size
        self.radius = self.size
        self.velocity_y = 0
        self.velocity_x = 2
        self.buoyancy_strength = 0.1

    def update(self):

        wave_y = self.wave.get_y(self.x_position)

        buoyancy_force = (wave_y - self.y_position) * self.buoyancy_strength

        damping = -self.velocity_y * 0.02

        self.velocity_y += (buoyancy_force + damping) / self.mass

        max_speed = 5 / (self.mass ** 0.5)

        self.velocity_y = np.clip(self.velocity_y, -max_speed, max_speed)

        self.y_position += self.velocity_y

        self.x_position += self.velocity_x

        if self.x_position > WINDOW_WIDTH:
            self.x_position = 0

    def contains(self, x, y):
        return (x - self.x_position) ** 2 + (y - self.y_position) ** 2 <= self.radius ** 2


class WaveSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wave Simulation")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.waves = [
            Wave(amplitude=36, period=200, speed=30, offset=MENU_HEIGHT + WINDOW_HEIGHT / 6),
            Wave(amplitude=46, period=210, speed=40, offset=MENU_HEIGHT + WINDOW_HEIGHT / 3),
            Wave(amplitude=56, period=200, speed=50, offset=MENU_HEIGHT + WINDOW_HEIGHT / 2),
        ]
        self.buoys = [Buoy(wave) for wave in self.waves]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(1000 // FPS)

        self.initUI()

    def update_simulation(self):
        for wave in self.waves:
            wave.update()
        for buoy in self.buoys:
            buoy.update()
        self.update()

    def initUI(self):
        layout = QVBoxLayout()
        self.amplitude_slider = self.create_slider(1, 200, 80, "Amplitude")
        self.period_slider = self.create_slider(50, 300, 150, "Period")
        self.speed_slider = self.create_slider(1, 100, 10, "Speed")

        self.add_wave_button = QPushButton("Add Wave")
        self.add_wave_button.clicked.connect(self.add_wave)

        self.remove_wave_button = QPushButton("Remove Wave")
        self.remove_wave_button.clicked.connect(self.remove_wave)

        layout.addWidget(self.amplitude_slider)
        layout.addWidget(self.period_slider)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.add_wave_button)
        layout.addWidget(self.remove_wave_button)

        self.amplitude_label = QLabel(f"Amplitude: {self.amplitude_slider.value()}")
        self.period_label = QLabel(f"Period: {self.period_slider.value()}")
        self.speed_label = QLabel(f"Speed: {self.speed_slider.value()}")

        layout.addWidget(self.amplitude_label)
        layout.addWidget(self.period_label)
        layout.addWidget(self.speed_label)

        self.amplitude_slider.valueChanged.connect(self.update_wave_parameters)
        self.period_slider.valueChanged.connect(self.update_wave_parameters)
        self.speed_slider.valueChanged.connect(self.update_wave_parameters)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_slider(self, min_value, max_value, initial_value, label):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        return slider

    def update_wave_parameters(self):
        for wave in self.waves:
            wave.amplitude = self.amplitude_slider.value()
            wave.period = self.period_slider.value()
            wave.speed = self.speed_slider.value()

        self.amplitude_label.setText(f"Amplitude: {self.amplitude_slider.value()}")
        self.period_label.setText(f"Period: {self.period_slider.value()}")
        self.speed_label.setText(f"Speed: {self.speed_slider.value()}")

    def add_wave(self):
        offset = MENU_HEIGHT + (len(self.waves) + 1) * (WINDOW_HEIGHT / 6)
        new_wave = Wave(amplitude=50, period=100, speed=15, offset=offset)
        self.waves.append(new_wave)
        self.buoys.append(Buoy(new_wave))
        self.update()

    def remove_wave(self):
        if self.waves:
            self.waves.pop()
            self.buoys.pop()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = [QColor(0, 0, 255), QColor(0, 255, 0), QColor(255, 0, 0)]

        for i, wave in enumerate(self.waves):
            painter.setPen(colors[i % len(colors)])
            last_y = int(wave.get_y(0))
            for x in range(1, WINDOW_WIDTH):
                y = int(wave.get_y(x))
                painter.drawLine(x - 1, last_y, x, y)
                last_y = y

        for buoy in self.buoys:
            painter.setBrush(QColor(255, 165, 0))
            painter.drawEllipse(
                buoy.x_position - buoy.radius,
                int(buoy.y_position) - buoy.radius,
                2 * buoy.radius,
                2 * buoy.radius,
            )
            painter.setPen(Qt.black)
            painter.drawText(
                buoy.x_position - buoy.radius,
                int(buoy.y_position) - buoy.radius - 5,
                f"Mass: {buoy.mass}",
            )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            for buoy in self.buoys:
                if buoy.contains(event.x(), event.y()):
                    self.edit_buoy_properties(buoy)
                    break

    def edit_buoy_properties(self, buoy):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Buoy Properties")
        form_layout = QFormLayout()

        mass_spinbox = QSpinBox()
        mass_spinbox.setValue(buoy.mass)
        form_layout.addRow("Mass:", mass_spinbox)

        size_spinbox = QSpinBox()
        size_spinbox.setValue(buoy.size)
        form_layout.addRow("Size:", size_spinbox)

        def save_changes():
            buoy.mass = mass_spinbox.value()
            buoy.size = size_spinbox.value()
            buoy.radius = buoy.size
            dialog.accept()

        save_button = QPushButton("Save")
        save_button.clicked.connect(save_changes)
        form_layout.addRow(save_button)
        dialog.setLayout(form_layout)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaveSimulation()
    window.show()
    sys.exit(app.exec_())
