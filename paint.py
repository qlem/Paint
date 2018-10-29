from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QAction, QFileDialog, QWidget, QLabel, \
    QPushButton, QColorDialog, QVBoxLayout, QHBoxLayout, QRadioButton
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen
import sys
import os
from PyQt5.QtCore import Qt, QPoint


class Painter(QWidget):
    def __init__(self):
        super().__init__()

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # draw settings
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.black

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

    # event handlers
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            print(self.lastPoint)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            # Images available here http://doc.qt.io/qt-5/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        top = 400
        left = 400
        width = 800
        height = 600

        self.setWindowTitle("Paint Application")
        self.setGeometry(top, left, width, height)

        # central widget
        self.central_widget = Painter()
        self.setCentralWidget(self.central_widget)

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
        self.colour_brush = QDockWidget("Colour brush", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colour_brush)

        colour_brush_widget = QWidget(self)
        self.colour_brush.setWidget(colour_brush_widget)

        button = QPushButton("color", self)
        button.clicked.connect(self.get_color)

        colour_brush_layout = QHBoxLayout()
        colour_brush_layout.addWidget(QLabel("Color:"))
        colour_brush_layout.addWidget(button)
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

    def get_color(self):
        color = QColorDialog().getColor()

    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.central_widget.image.load(file_path)
        if res:
            self.central_widget.update()

    def save(self):
        current_path = os.getcwd()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", current_path + "/untitled.png",
                                                   "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.central_widget.image.save(file_path)
        print(res)

    def clear(self):
        self.central_widget.image.fill(Qt.white)
        self.update()

    def exit(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
