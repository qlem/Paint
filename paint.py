from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QAction, QFileDialog, QWidget, QLabel, \
    QPushButton, QColorDialog, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QSlider
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QColor
import sys
import os
from PyQt5.QtCore import Qt, QPoint
from enum import Enum


# This class is an enum that represents the current draw mode: curve or line.
class DrawMode(Enum):
    CURVE = 0
    LINE = 1


# This class defines the widget that allows to paint in the central area of the window.
class Painter(QWidget):
    def __init__(self):
        super().__init__()

        # initialisation of the image that represents the "drawing sheet"
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        # default draw settings
        self.drawing = False
        self.draw_mode = DrawMode.CURVE
        self.brush_size = 6
        self.brush_color = QColor(0, 0, 0)
        self.brush_line_type = Qt.SolidLine
        self.brush_cap_type = Qt.RoundCap
        self.brush_join_type = Qt.RoundJoin

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

        # reference to the image backup
        self.backup = QImage()

    # function to draw a line between tow points
    def draw(self, from_point, to_point):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color, self.brush_size, self.brush_line_type,
                   self.brush_cap_type, self.brush_join_type)
        painter.setPen(pen)
        painter.drawLine(from_point, to_point)
        self.update()

    # mouse press event listener
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            if self.draw_mode == DrawMode.LINE:
                self.backup = self.image.copy()

    # mouse move event listener
    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton) & (self.draw_mode == DrawMode.CURVE) & self.drawing:
            self.draw(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
        if (event.buttons() == Qt.LeftButton) & (self.draw_mode == DrawMode.LINE) & self.drawing:
            self.image = self.backup.copy()
            self.draw(self.lastPoint, event.pos())

    # mouse release event listener
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    # paint event listener, draw the image in the paint area
    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(self.rect(), self.image, self.image.rect())

    # resize event listener
    def resizeEvent(self, event):
        print("w: " + str(self.width()))
        print("h: " + str(self.height()))
        self.image = self.image.scaled(self.width(), self.height())


# This class defines the widget for the selection of the draw mode.
class DrawModeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # radio buttons declaration
        mode_1 = QRadioButton("curve")
        mode_2 = QRadioButton("line")
        mode_1.setChecked(True)

        # adding buttons to group
        self.draw_mode_group = QButtonGroup()
        self.draw_mode_group.addButton(mode_1)
        self.draw_mode_group.addButton(mode_2)
        i = 0
        for button in self.draw_mode_group.buttons():
            self.draw_mode_group.setId(button, i)
            i += 1
        self.draw_mode_group.buttonClicked.connect(self.set_draw_mode)

        # adding buttons to layout
        draw_mode_layout = QVBoxLayout()
        draw_mode_layout.addWidget(mode_1)
        draw_mode_layout.addWidget(mode_2)
        self.setLayout(draw_mode_layout)

    # button selection event listener
    def set_draw_mode(self):
        id_button = self.draw_mode_group.checkedId()
        if id_button == 0:
            self.painter.draw_mode = DrawMode.CURVE
        elif id_button == 1:
            self.painter.draw_mode = DrawMode.LINE


# This class defines the widget for the selection of the brush color.
class BrushColorWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # declaration of the color picker button and labels
        button = QPushButton("picker", self)
        button.clicked.connect(self.set_brush_color)
        self.color_indicator = QLabel()
        self.color_indicator.setStyleSheet("background: black")

        # adding color picker button and labels to layout
        brush_colour_layout = QGridLayout()
        brush_colour_layout.addWidget(QLabel("color:"), 0, 0, 1, 1)
        brush_colour_layout.addWidget(self.color_indicator, 0, 1, 1, 1)
        brush_colour_layout.addWidget(button, 1, 0, 1, 2)
        self.setLayout(brush_colour_layout)

    # color picker selection event listener
    def set_brush_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            red = color.getRgb()[0]
            green = color.getRgb()[1]
            blue = color.getRgb()[2]
            style = "background: rgb(" + str(red) + "," + str(green) + "," + str(blue) + ")"
            self.color_indicator.setStyleSheet(style)
            self.painter.brush_color = color


# This class defines the widget for the selection of the brush thickness.
class BrushThicknessWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # declaration of the thickness size's slider and label
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

        # adding slider and label to layout
        brush_thickness_layout = QGridLayout()
        brush_thickness_layout.addWidget(self.thickness_slider, 0, 0, 1, 2)
        brush_thickness_layout.addWidget(thickness_label, 1, 0, 1, 1)
        brush_thickness_layout.addWidget(self.thickness_size_label, 1, 1, 1, 1)
        self.setLayout(brush_thickness_layout)

    # slider value change event listener
    def set_brush_thickness(self):
        self.painter.brush_size = self.thickness_slider.value()
        self.thickness_size_label.setText(str(self.thickness_slider.value()) + "px")


# This class defines the widget for the selection of the brush line type selection.
class BrushLineTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # radio buttons declaration
        line_type_1 = QRadioButton("solid")
        line_type_2 = QRadioButton("dash")
        line_type_3 = QRadioButton("dot")
        line_type_4 = QRadioButton("dash dot")
        line_type_5 = QRadioButton("dash dot dot")
        line_type_1.setChecked(True)

        # adding buttons to group
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

        # adding buttons to layout
        line_type_layout = QVBoxLayout()
        line_type_layout.addWidget(line_type_1)
        line_type_layout.addWidget(line_type_2)
        line_type_layout.addWidget(line_type_3)
        line_type_layout.addWidget(line_type_4)
        line_type_layout.addWidget(line_type_5)
        self.setLayout(line_type_layout)

    # button selection event listener
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


# This class defines the widget for the selection of the brush cap type.
class BrushCapTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # radio buttons declaration
        cap_type_1 = QRadioButton("flat")
        cap_type_2 = QRadioButton("square")
        cap_type_3 = QRadioButton("round")
        cap_type_3.setChecked(True)

        # adding buttons to group
        self.cap_type_group = QButtonGroup()
        self.cap_type_group.addButton(cap_type_1)
        self.cap_type_group.addButton(cap_type_2)
        self.cap_type_group.addButton(cap_type_3)
        i = 0
        for button in self.cap_type_group.buttons():
            self.cap_type_group.setId(button, i)
            i += 1
        self.cap_type_group.buttonClicked.connect(self.set_brush_cap_type)

        # adding buttons to layout
        cap_type_layout = QVBoxLayout()
        cap_type_layout.addWidget(cap_type_1)
        cap_type_layout.addWidget(cap_type_2)
        cap_type_layout.addWidget(cap_type_3)
        self.setLayout(cap_type_layout)

    # button selection event listener
    def set_brush_cap_type(self):
        id_button = self.cap_type_group.checkedId()
        if id_button == 0:
            self.painter.brush_cap_type = Qt.FlatCap
        elif id_button == 1:
            self.painter.brush_cap_type = Qt.SquareCap
        elif id_button == 2:
            self.painter.brush_cap_type = Qt.RoundCap


# This class defines the widget for the selection of the brush join type.
class BrushJoinTypeWidget(QWidget):
    def __init__(self, painter):
        super().__init__()

        # reference to the painter widget
        self.painter = painter

        # radio buttons declaration
        join_type_1 = QRadioButton("miter")
        join_type_2 = QRadioButton("bevel")
        join_type_3 = QRadioButton("round")
        join_type_3.setChecked(True)

        # adding buttons to group
        self.join_type_group = QButtonGroup()
        self.join_type_group.addButton(join_type_1)
        self.join_type_group.addButton(join_type_2)
        self.join_type_group.addButton(join_type_3)
        i = 0
        for button in self.join_type_group.buttons():
            self.join_type_group.setId(button, i)
            i += 1
        self.join_type_group.buttonClicked.connect(self.set_brush_join_type)

        # adding buttons to layout
        cap_type_layout = QVBoxLayout()
        cap_type_layout.addWidget(join_type_1)
        cap_type_layout.addWidget(join_type_2)
        cap_type_layout.addWidget(join_type_3)
        self.setLayout(cap_type_layout)

    # button selection event listener
    def set_brush_join_type(self):
        id_button = self.join_type_group.checkedId()
        if id_button == 0:
            self.painter.brush_join_type = Qt.MiterJoin
        elif id_button == 1:
            self.painter.brush_join_type = Qt.BevelJoin
        elif id_button == 2:
            self.painter.brush_join_type = Qt.RoundJoin


# This class creates the main window and display all widgets that compose the UI.
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        top = 400
        left = 400
        width = 1200
        height = 800

        self.setWindowTitle("Paint Application")
        self.setGeometry(left, top, width, height)

        # init menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        help_menu = menu.addMenu("Help")

        # open
        open_action = QAction(QIcon("./icons/open.png"), "Open", self)
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
        exit_action = QAction(QIcon("./icons/exit.png"), "Exit", self)
        exit_action.setShortcut("Ctrl+X")
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.exit)

        # init painter widget
        self.painter = Painter()
        self.setCentralWidget(self.painter)
        self.painter.show()

        # init draw mode widget
        self.draw_mode = QDockWidget("Draw mode")
        self.addDockWidget(Qt.RightDockWidgetArea, self.draw_mode)
        self.draw_mode.setWidget(DrawModeWidget(self.painter))
        self.draw_mode.setMaximumHeight(self.draw_mode.minimumSizeHint().height())
        self.draw_mode.setFixedWidth(200)

        # init brush color widget
        self.brush_colour = QDockWidget("Brush colour")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_colour)
        self.brush_colour.setWidget(BrushColorWidget(self.painter))
        self.brush_colour.setMaximumHeight(self.brush_colour.minimumSizeHint().height())
        self.brush_colour.setFixedWidth(200)

        # init brush thickness widget
        self.brush_thickness = QDockWidget("Brush thickness")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_thickness)
        self.brush_thickness.setWidget(BrushThicknessWidget(self.painter))
        self.brush_thickness.setMaximumHeight(self.brush_thickness.minimumSizeHint().height())
        self.brush_thickness.setFixedWidth(200)

        # init brush line type widget
        self.brush_line_type = QDockWidget("Brush line type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_line_type)
        self.brush_line_type.setWidget(BrushLineTypeWidget(self.painter))
        self.brush_line_type.setMaximumHeight(self.brush_line_type.minimumSizeHint().height())
        self.brush_line_type.setFixedWidth(200)

        # init brush cap type widget
        self.brush_cap_type = QDockWidget("Brush cap type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_cap_type)
        self.brush_cap_type.setWidget(BrushCapTypeWidget(self.painter))
        self.brush_cap_type.setMaximumHeight(self.brush_cap_type.minimumSizeHint().height())
        self.brush_cap_type.setFixedWidth(200)

        # init brush join type widget
        self.brush_join_type = QDockWidget("Brush join type")
        self.addDockWidget(Qt.RightDockWidgetArea, self.brush_join_type)
        self.brush_join_type.setWidget(BrushJoinTypeWidget(self.painter))
        self.brush_join_type.setMaximumHeight(self.brush_join_type.minimumSizeHint().height())
        self.brush_join_type.setFixedWidth(200)

    # function that allows to open an image
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

    # function that allows to save an image
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

    # function that allows to clear the paint area
    def clear(self):
        self.painter.image.fill(Qt.white)
        self.update()

    # function to exit
    def exit(self):
        self.close()


# This is the entry point of the program.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
