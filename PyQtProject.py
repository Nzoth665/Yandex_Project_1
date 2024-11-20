import sys
import sqlite3
import numpy as np

from PyQt6 import uic
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtCore import Qt, QTimer


class MainWindow(QMainWindow):
    def __init__(self, a1, cs, rule):
        super().__init__()
        uic.loadUi("main_window.ui", self)
        self.startWindow = a1
        self.cs = cs
        self.rule = rule
        self.generation = 0
        self.setWindowTitle(f"Прошло {self.generation} поколений.")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time)
        self.q = 1000 // self.speed.value()

        self.initUI()
        self.buttons_init()

    def initUI(self):
        global ok
        self.xs, ok_press = QInputDialog.getInt(self, "Ширина поля", f"Введите ширину поля (max - {2000 // self.cs})", 1000 // self.cs, 1, 2000 // self.cs, 1)
        if not ok_press:
            ok = 0
            self.xs, self.ys = 0, 0
        else:
            self.ys, ok_press = QInputDialog.getInt(self, "Высота поля", f"Введите высоту поля (max - {850 // self.cs})", 500 // self.cs, 1, 850 // self.cs, 1)
            if not ok_press:
                ok = 0
                self.ys = 0

        self.field = np.array([[0 for _ in range(self.ys)] for _ in range(self.xs)], dtype=np.byte)

        self.frame.resize(self.xs * self.cs, self.ys * self.cs)
        self.groupBox.move(1, self.ys * self.cs)
        self.groupBox.resize(self.xs * self.cs, self.ys * self.cs)
        ws = (self.groupBox.pos().x() + self.groupBox.size().width() + 5,
              self.groupBox.pos().y() + self.groupBox.size().height() + 20)
        self.resize(ws[0], ws[1])
        self.setMinimumSize(ws[0], ws[1])
        self.setMaximumSize(ws[0], ws[1])

        born = self.born.buttons()
        survival = self.survival.buttons()
        for i in range(1, 10):
            self.born.setId(born[i - 1], i)
            self.survival.setId(survival[i - 1], i)
        for i, e in enumerate(self.rule):
            if e == "1" and i < 9:
                born[i].setCheckState(Qt.CheckState.Checked)
            elif e == "1" and i >= 9:
                survival[i - 9].setCheckState(Qt.CheckState.Checked)

    def buttons_init(self):
        self.mix_button.clicked.connect(self.mix)
        self.clean_button.clicked.connect(self.clean)
        self.step_button.clicked.connect(self.step)
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.born.buttonClicked.connect(self.checkBoxBorn)
        self.survival.buttonClicked.connect(self.checkBoxSurvival)
        self.lrb.clicked.connect(self.lrbf)
        self.srb.clicked.connect(self.srbf)
        self.lfb.clicked.connect(self.lfbf)
        self.sfb.clicked.connect(self.sfbf)

    def ruleUpdate(self):
        born = self.born.buttons()
        survival = self.survival.buttons()
        for i in born:
            i.setCheckState(Qt.CheckState.Unchecked)
        for i in survival:
            i.setCheckState(Qt.CheckState.Unchecked)
        for i, e in enumerate(self.rule):
            if e == "1" and i < 9:
                born[i].setCheckState(Qt.CheckState.Checked)
            elif e == "1" and i >= 9:
                survival[i - 9].setCheckState(Qt.CheckState.Checked)

    def checkBoxBorn(self, x):
        self.rule = self.rule[:self.born.id(x) - 1] + str(1 - int(self.rule[self.born.id(x) - 1])) + self.rule[
                                                                                                     self.born.id(x):]

    def checkBoxSurvival(self, x):
        self.rule = (self.rule[:self.survival.id(x) - 1] + str(1 - int(self.rule[self.survival.id(x) - 1]))
                     + self.rule[self.survival.id(x):])

    def mix(self):
        self.field = np.random.randint(0, 2, (self.xs, self.ys))
        self.generation = 0
        self.setWindowTitle(f"Прошло {self.generation} поколений.")
        self.update()

    def clean(self):
        self.field *= 0
        self.generation = 0
        self.setWindowTitle(f"Прошло {self.generation} поколений.")
        self.stop()
        self.update()

    def onecell(self, a):
        neighbors = sum([
            np.roll(np.roll(a, -1, 1), 1, 0),
            np.roll(np.roll(a, 1, 1), -1, 0),
            np.roll(np.roll(a, 1, 1), 1, 0),
            np.roll(np.roll(a, -1, 1), -1, 0),
            np.roll(a, 1, 1),
            np.roll(a, -1, 1),
            np.roll(a, 1, 0),
            np.roll(a, -1, 0)
        ])
        s = False
        b = False
        for i, e in enumerate(self.rule):
            if e == "1" and i <= 9:
                b = b | (neighbors == i)
            elif e == "1" and i > 8:
                s = s | (neighbors == (i - 9))
        return ((1 - a) & b) | (a & s)

    def step(self):
        self.field = self.onecell(self.field)
        self.generation += 1
        self.setWindowTitle(f"Прошло {self.generation} поколений.")
        self.update()

    def start(self):
        self.timer.start(self.q)

    def stop(self):
        self.timer.stop()

    def lrbf(self):
        cur = sqlite3.connect("project.db").cursor()
        new_rule, ok_pressed = QInputDialog.getItem(
    self, "Правило", "Выбирете новое правило",
    tuple(map(lambda x: x[0], cur.execute(f"SELECT title FROM save_rules ORDER BY id").fetchall())), 0, False)
        if ok_pressed:
            self.rule = cur.execute(f'SELECT rule FROM save_rules WHERE title = "{new_rule}"').fetchall()[0][0]
            self.ruleUpdate()
            self.update()
        cur.close()

    def srbf(self):
        self.safes = Safes_rules()
        self.safes.show()

    def lfbf(self):
        pass

    def sfbf(self):
        pass

    def time(self):
        if self.q != 1000 // self.speed.value():
            q = 1000 // self.speed.value()
            self.timer.start(q)
        self.step()

    def closeEvent(self, a0):
        self.startWindow.show()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            if a0.pos().x() < self.frame.size().width() and a0.pos().y() < self.frame.size().height():
                pos = (a0.pos().x() // self.cs, a0.pos().y() // self.cs)
                self.field[pos[0]][pos[1]] = int(not self.field[pos[0]][pos[1]])
                self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(0, 0, 0))
        for i1, e1 in enumerate(self.field):
            for i2, e2 in enumerate(e1):
                if e2:
                    qp.drawRect(i1 * self.cs, i2 * self.cs, self.cs, self.cs)
        qp.end()


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("start_window.ui", self)
        with open('settings', "r") as f:
            self.sets = f.read().split("\n")
            self.cs = int(self.sets[0])
            cur = sqlite3.connect("project.db").cursor()
            self.rule = cur.execute(f"SELECT rule FROM save_rules WHERE id = {self.sets[1]}").fetchall()[0][0]
            cur.close()
            # self.rule = rule
        self.cfb.clicked.connect(self.create_field)
        self.ccs.clicked.connect(self.change_cell_size)
        self.field = 0

    def create_field(self):
        global ok
        ok = 1
        self.field = MainWindow(self, self.cs, self.rule)
        if ok:
            self.field.show()
            self.hide()

    def change_cell_size(self):
        cs, ok_pressed = QInputDialog.getInt(self, "Новый размер клетки", "Введите новый размер клетки",
                                             self.cs, 1, 100, 1)
        if ok_pressed:
            self.cs = cs
            open('settings', "w").write(str(cs) + "\n" + '\n'.join(self.sets[1:]))

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()


class Safes_rules(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("safes.ui", self)
        self.initUI()
        self.buttons_init()

    def initUI(self):
        self.con = sqlite3.connect("project.db")
        self.cur = self.con.cursor()
        self.tableWidget.setColumnCount(2)
        self.update_table()

    def update_table(self):
        r = self.cur.execute(f"SELECT id, title FROM save_rules ORDER BY id").fetchall()
        self.tableWidget.setRowCount(len(r))
        for i in range(len(r)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(r[i][0])))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(r[i][1])))
        self.tableWidget.resizeColumnsToContents()


    def buttons_init(self):
        self.sbtn.clicked.connect(self.safe)
        self.dbtn.clicked.connect(self.delete)

    def safe(self):
        name, ok_press = QInputDialog.getText(self, "Название правила", "Выбирете название правилу которое у вас стоит на данный момент")
        if ok_press:
            self.cur.execute(f"INSERT INTO save_rules(title, rule) VALUES('{name}', '000000000000000000')")
            self.con.commit()
            self.update_table()

    def delete(self):
        id, ok_press = QInputDialog.getText(self, "Удаление правила", "Напишите id правила которое вы хотите удалить")
        if ok_press and id > 5:
            self.cur.execute(f"DELETE FROM save_rules WHERE id = {id}")
            self.con.commit()
            self.update_table()

    def closeEvent(self, event):
        pass

ok = 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = StartWindow()
    w.show()
    sys.exit(app.exec())
