from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QAction, QFileDialog, QWidget, QLabel, \
    QPushButton, QColorDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QRadioButton, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QColor
import sys
import os
from PyQt5.QtCore import Qt, QPoint


class Painter(QWidget):
    def __init__(self):
        super().__init__()

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # default draw settings
        self.drawing = False
        self.brushSize = 3
        self.brushColor = QColor(0, 0, 0)

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            # print(self.lastPoint)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            print(event.pos())

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    def resizeEvent(self, event):
        print("w: " + str(self.width()))
        print("h: " + str(self.height()))
        self.image = self.image.scaled(self.width(), self.height())


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        top = 400
        left = 400
        width = 800
        height = 600

        self.setWindowTitle("Paint Application")
        self.setGeometry(left, top, width, height)

        # painter
        self.painter = Painter()
        self.setCentralWidget(self.painter)
        self.painter.show()

        # menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        # open
        open_action = QAction(QIcon("./icons/save.png"), "Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open)

        # save
        save_action = QAction(QIcon("./icons/save.png"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save)

        # clear
        clear_action = QAction(QIcon("./icons/clear.png"), "Clear", self)
        clear_action.setShortcut("Ctrl+C")
        file_menu.addAction(clear_action)
        clear_action.triggered.connect(self.clear)

        # exit
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+X")
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.exit)

        # colour brush widget
        self.brush_colour = QDockWidget("Colour brush", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_colour)
        colour_brush_widget = QWidget(self)
        self.brush_colour.setWidget(colour_brush_widget)

        button = QPushButton("picker", self)
        button.clicked.connect(self.get_color)
        self.color_indicator = QLabel()
        self.color_indicator.setStyleSheet(self.get_color_indicator())

        colour_brush_layout = QGridLayout()
        colour_brush_layout.addWidget(QLabel("color:"), 0, 0, 1, 1)
        colour_brush_layout.addWidget(self.color_indicator, 0, 1, 1, 1)
        colour_brush_layout.addWidget(button, 1, 0, 1, 2)
        colour_brush_widget.setLayout(colour_brush_layout)

        # brush thickness widget
        self.brush_thickness = QDockWidget("Brush Thickness", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_thickness)

        brush_thickness_widget = QWidget(self)
        self.brush_thickness.setWidget(brush_thickness_widget)

        thickness_size_1 = QRadioButton("size 1")
        thickness_size_2 = QRadioButton("size 2")
        thickness_size_3 = QRadioButton("size 3")
        thickness_size_4 = QRadioButton("size 4")

        brush_thickness_layout = QVBoxLayout()
        brush_thickness_layout.addWidget(thickness_size_1)
        brush_thickness_layout.addWidget(thickness_size_2)
        brush_thickness_layout.addWidget(thickness_size_3)
        brush_thickness_layout.addWidget(thickness_size_4)
        brush_thickness_widget.setLayout(brush_thickness_layout)

    def get_color_indicator(self):
        red = self.painter.brushColor.getRgb()[0]
        green = self.painter.brushColor.getRgb()[1]
        blue = self.painter.brushColor.getRgb()[2]
        return "background: rgb(" + str(red) + "," + str(green) + "," + str(blue) + ")"

    def get_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.painter.brushColor = color
            self.color_indicator.setStyleSheet(self.get_color_indicator())

    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.painter.image.load(file_path)
        if res:
            self.painter.image = self.painter.image.scaled(self.painter.width(), self.painter.height())
            self.painter.update()

    def save(self):
        current_path = os.getcwd()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", current_path + "/untitled.png",
                                                   "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.painter.image.save(file_path)
        print(res)

    def clear(self):
        self.painter.image.fill(Qt.white)
        self.update()

    def exit(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
