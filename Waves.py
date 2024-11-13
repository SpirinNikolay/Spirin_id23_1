import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
import json

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Класс для описания волны
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

    def to_dict(self):
        return {
            "amplitude": self.amplitude,
            "period": self.period,
            "speed": self.speed,
            "offset": self.offset
        }

class Buoy:
    def __init__(self, wave):
        self.wave = wave
        self.x_position = np.random.randint(0, WINDOW_WIDTH)
        self.y_position = self.wave.get_y(self.x_position)

    def update(self):
        self.y_position = self.wave.get_y(self.x_position)

class WaveSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wave Simulation")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.waves = [
            Wave(amplitude=80, period=150, speed=10, offset=WINDOW_HEIGHT / 4),
            Wave(amplitude=60, period=120, speed=10, offset=WINDOW_HEIGHT / 2),
            Wave(amplitude=40, period=90, speed=20, offset=3 * WINDOW_HEIGHT / 4),
            Wave(amplitude=20, period=60, speed=25, offset=WINDOW_HEIGHT)
        ]

        self.buoys = [Buoy(wave) for wave in self.waves]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(1000 // FPS)

        # Преобразование волн в словари для сохранения в JSON
        data = {"waves": [wave.to_dict() for wave in self.waves]}

        with open('waves.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def update_simulation(self):
        for wave in self.waves:
            wave.update()
        for buoy in self.buoys:
            buoy.update()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = [QColor(0, 0, 255), QColor(0, 255, 0), QColor(255, 0, 0), QColor(255, 255, 0)]

        for i, wave in enumerate(self.waves):
            painter.setPen(colors[i % len(colors)])
            last_y = int(wave.get_y(0))
            for x in range(1, WINDOW_WIDTH):
                y = int(wave.get_y(x))
                painter.drawLine(x - 1, last_y, x, y)
                last_y = y

        for buoy in self.buoys:
            painter.setBrush(QColor(255, 165, 0))
            painter.drawEllipse(buoy.x_position - 5, int(buoy.y_position) - 5, 10, 10)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaveSimulation()
    window.show()
    sys.exit(app.exec_())
