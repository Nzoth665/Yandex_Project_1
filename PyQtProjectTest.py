import sys

from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.field = [[0 for _ in range(10)] for _ in range(22)]
        self.start_pos = (25, 25)
        self.end_pos = (575, 275)
        self.cage_size = 25

    def initUI(self):
        size = (600, 300)
        self.setGeometry(300, 300, *size)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)

    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton and self.start_pos[0] < a0.position().x() < self.end_pos[0] and \
                self.start_pos[1] < a0.position().y() < self.end_pos[1]:
            pos = (int(a0.position().x() - self.start_pos[0]) // self.cage_size,
                   int(a0.position().y() - self.start_pos[1]) // self.cage_size)
            if self.field[pos[0]][pos[1]]:
                self.field[pos[0]][pos[1]] = 0
            else:
                self.field[pos[0]][pos[1]] = 1
            self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(0, 0, 0))
        for i1, e1 in enumerate(self.field):
            for i2, e2 in enumerate(e1):
                if e2:
                    qp.drawRect(i1 * self.cage_size + self.start_pos[0], i2 * self.cage_size + self.start_pos[1],
                                self.cage_size, self.cage_size)
        qp.end()


class StartWindow(QMainWindow):
    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
