from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
import math
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer

class CircleAnimation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circle Animation")
        self.setGeometry(100, 100, 600, 600)

        self.radius = 200
        self.angle = 0
        self.speed = 2
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(30)

        # Add a button to start/stop the animation
        self.button = QPushButton("Stop", self)
        self.button.clicked.connect(self.toggle_animation)
        self.button.setGeometry(10, 10, 80, 30)

    def update_angle(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        painter.setPen(QColor(0, 0, 0))
        painter.drawEllipse(center_x - self.radius, center_y - self.radius, self.radius * 2, self.radius * 2)

        point_x = center_x + self.radius * math.cos(math.radians(self.angle))
        point_y = center_y + self.radius * math.sin(math.radians(self.angle))

        point_x = int(point_x)
        point_y = int(point_y)

        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(point_x - 5, point_y - 5, 10, 10)

    def toggle_animation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start")
        else:
            self.timer.start(30)
            self.button.setText("Stop")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleAnimation()
    window.show()
    sys.exit(app.exec_())
