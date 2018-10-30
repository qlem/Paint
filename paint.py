from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QAction, QFileDialog, QWidget, QLabel, \
    QPushButton, QColorDialog, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QSlider
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
        self.brush_size = 6
        self.brush_color = QColor(0, 0, 0)
        self.brush_line_type = Qt.SolidLine
        self.brush_cap_type = Qt.RoundCap
        self.brush_join_type = Qt.RoundJoin

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            pen = QPen(self.brush_color, self.brush_size, self.brush_line_type,
                       self.brush_cap_type, self.brush_join_type)
            painter.setPen(pen)
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    def resizeEvent(self, event):
        print("w: " + str(self.width()))
        print("h: " + str(self.height()))
        self.image = self.image.scaled(self.width(), self.height())


class BrushColorWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        self.painter = painter

        button = QPushButton("picker", self)
        button.clicked.connect(self.set_brush_color)
        self.color_indicator = QLabel()
        self.color_indicator.setStyleSheet(self.get_color_indicator())

        brush_colour_layout = QGridLayout()
        brush_colour_layout.addWidget(QLabel("color:"), 0, 0, 1, 1)
        brush_colour_layout.addWidget(self.color_indicator, 0, 1, 1, 1)
        brush_colour_layout.addWidget(button, 1, 0, 1, 2)
        self.setLayout(brush_colour_layout)

    def get_color_indicator(self):
        red = self.painter.brush_color.getRgb()[0]
        green = self.painter.brush_color.getRgb()[1]
        blue = self.painter.brush_color.getRgb()[2]
        return "background: rgb(" + str(red) + "," + str(green) + "," + str(blue) + ")"

    def set_brush_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.painter.brush_color = color
            self.color_indicator.setStyleSheet(self.get_color_indicator())


class BrushThicknessWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        self.painter = painter

        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setTickInterval(1)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(25)
        self.thickness_slider.setTickInterval(5)
        self.thickness_slider.setTickPosition(QSlider.TicksBelow)
        self.thickness_slider.setValue(6)
        self.thickness_slider.valueChanged.connect(self.set_brush_thickness)
        thickness_label = QLabel("size:")
        self.thickness_size_label = QLabel(str(self.thickness_slider.value()) + "px")

        brush_thickness_layout = QGridLayout()
        brush_thickness_layout.addWidget(self.thickness_slider, 0, 0, 1, 2)
        brush_thickness_layout.addWidget(thickness_label, 1, 0, 1, 1)
        brush_thickness_layout.addWidget(self.thickness_size_label, 1, 1, 1, 1)
        self.setLayout(brush_thickness_layout)

    def set_brush_thickness(self):
        self.painter.brush_size = self.thickness_slider.value()
        self.thickness_size_label.setText(str(self.thickness_slider.value()) + "px")


class BrushLineTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        self.painter = painter

        line_type_1 = QRadioButton("solid")
        line_type_1.setChecked(True)
        line_type_2 = QRadioButton("dash")
        line_type_3 = QRadioButton("dot")
        line_type_4 = QRadioButton("dash dot")
        line_type_5 = QRadioButton("dash dot dot")

        self.line_type_group = QButtonGroup()
        self.line_type_group.addButton(line_type_1)
        self.line_type_group.addButton(line_type_2)
        self.line_type_group.addButton(line_type_3)
        self.line_type_group.addButton(line_type_4)
        self.line_type_group.addButton(line_type_5)
        i = 0
        for button in self.line_type_group.buttons():
            self.line_type_group.setId(button, i)
            i += 1
        self.line_type_group.buttonClicked.connect(self.set_brush_line_type)

        line_type_layout = QVBoxLayout()
        line_type_layout.addWidget(line_type_1)
        line_type_layout.addWidget(line_type_2)
        line_type_layout.addWidget(line_type_3)
        line_type_layout.addWidget(line_type_4)
        line_type_layout.addWidget(line_type_5)
        self.setLayout(line_type_layout)

    def set_brush_line_type(self):
        id_button = self.line_type_group.checkedId()
        if id_button == 0:
            self.painter.brush_line_type = Qt.SolidLine
        elif id_button == 1:
            self.painter.brush_line_type = Qt.DashLine
        elif id_button == 2:
            self.painter.brush_line_type = Qt.DotLine
        elif id_button == 3:
            self.painter.brush_line_type = Qt.DashDotLine
        elif id_button == 4:
            self.painter.brush_line_type = Qt.DashDotDotLine


class BrushCapTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        self.painter = painter

        cap_type_1 = QRadioButton("flat")
        cap_type_2 = QRadioButton("square")
        cap_type_3 = QRadioButton("round")
        cap_type_3.setChecked(True)

        self.cap_type_group = QButtonGroup()
        self.cap_type_group.addButton(cap_type_1)
        self.cap_type_group.addButton(cap_type_2)
        self.cap_type_group.addButton(cap_type_3)
        i = 0
        for button in self.cap_type_group.buttons():
            self.cap_type_group.setId(button, i)
            i += 1
        self.cap_type_group.buttonClicked.connect(self.set_brush_cap_type)

        cap_type_layout = QVBoxLayout()
        cap_type_layout.addWidget(cap_type_1)
        cap_type_layout.addWidget(cap_type_2)
        cap_type_layout.addWidget(cap_type_3)
        self.setLayout(cap_type_layout)

    def set_brush_cap_type(self):
        id_button = self.cap_type_group.checkedId()
        if id_button == 0:
            self.painter.brush_cap_type = Qt.FlatCap
        elif id_button == 1:
            self.painter.brush_cap_type = Qt.SquareCap
        elif id_button == 2:
            self.painter.brush_cap_type = Qt.RoundCap


class BrushJoinTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        self.painter = painter

        join_type_1 = QRadioButton("miter")
        join_type_2 = QRadioButton("bevel")
        join_type_3 = QRadioButton("round")
        join_type_3.setChecked(True)

        self.join_type_group = QButtonGroup()
        self.join_type_group.addButton(join_type_1)
        self.join_type_group.addButton(join_type_2)
        self.join_type_group.addButton(join_type_3)
        i = 0
        for button in self.join_type_group.buttons():
            self.join_type_group.setId(button, i)
            i += 1
        self.join_type_group.buttonClicked.connect(self.set_brush_join_type)

        cap_type_layout = QVBoxLayout()
        cap_type_layout.addWidget(join_type_1)
        cap_type_layout.addWidget(join_type_2)
        cap_type_layout.addWidget(join_type_3)
        self.setLayout(cap_type_layout)

    def set_brush_join_type(self):
        id_button = self.join_type_group.checkedId()
        if id_button == 0:
            self.painter.brush_join_type = Qt.MiterJoin
        elif id_button == 1:
            self.painter.brush_join_type = Qt.BevelJoin
        elif id_button == 2:
            self.painter.brush_join_type = Qt.RoundJoin


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        top = 400
        left = 400
        width = 1200
        height = 800

        self.setWindowTitle("Paint Application")
        self.setGeometry(left, top, width, height)

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

        # painter
        self.painter = Painter()
        self.setCentralWidget(self.painter)
        self.painter.show()

        # brush color
        self.brush_colour = QDockWidget("Brush colour")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_colour)
        self.brush_colour.setWidget(BrushColorWidget(self.painter))
        self.brush_colour.setMaximumHeight(self.brush_colour.minimumSizeHint().height())
        self.brush_colour.setFixedWidth(200)

        # brush thickness
        self.brush_thickness = QDockWidget("Brush thickness")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_thickness)
        self.brush_thickness.setWidget(BrushThicknessWidget(self.painter))
        self.brush_thickness.setMaximumHeight(self.brush_thickness.minimumSizeHint().height())
        self.brush_thickness.setFixedWidth(200)

        # brush line type
        self.brush_line_type = QDockWidget("Brush line type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_line_type)
        self.brush_line_type.setWidget(BrushLineTypeWidget(self.painter))
        self.brush_line_type.setMaximumHeight(self.brush_line_type.minimumSizeHint().height())
        self.brush_line_type.setFixedWidth(200)

        # brush cap type
        self.brush_cap_type = QDockWidget("Brush cap type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_cap_type)
        self.brush_cap_type.setWidget(BrushCapTypeWidget(self.painter))
        self.brush_cap_type.setMaximumHeight(self.brush_cap_type.minimumSizeHint().height())
        self.brush_cap_type.setFixedWidth(200)

        # brush join type
        self.brush_join_type = QDockWidget("Brush join type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_join_type)
        self.brush_join_type.setWidget(BrushJoinTypeWidget(self.painter))
        self.brush_join_type.setMaximumHeight(self.brush_join_type.minimumSizeHint().height())
        self.brush_join_type.setFixedWidth(200)

    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.painter.image.load(file_path)
        if res:
            self.painter.image = self.painter.image.scaled(self.painter.width(), self.painter.height())
            self.painter.update()
            print("Image successfully loaded")
        else:
            print("Cannot open image")

    def save(self):
        current_path = os.getcwd()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", current_path + "/untitled.png",
                                                   "Images (*.png *.jpg)")
        if file_path == "":
            return
        res = self.painter.image.save(file_path)
        if res:
            print("Image successfully saved")
        else:
            print("Cannot save image")

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
