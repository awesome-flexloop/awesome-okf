---
type: Example
title: "2020-07-03"
source: "https://www.jianshu.com/p/cf0d9b7eff2c"
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
---

# 示例 02：2020-07-03

> **信源**：[简书文集《Qt Python GUI 学习（《PyQt5快速开发与实战》笔记）》](https://www.jianshu.com/nb/46416111) · 作者 **水之心** · [原文链接](https://www.jianshu.com/p/cf0d9b7eff2c) · 发布于 2020-07-03
> **对应事实**：F-004 ~ F-006

```python
class ParamDict(dict):
    def __init__(self, custom_type, *args, **kw):
        super().__init__(*args, **kw)
        self.custom_type = custom_type

    def __set__(self, instance, value):
        #print('===> set', instance, value)
        if isinstance(value, self.custom_type):
            self[instance] = self.custom_type(value)
        else:
            self[instance] = self.custom_type(*value)

    def __get__(self, instance, owner):
        return self[instance]
```

```python
'''涂鸦工具
借鉴 https://github.com/baoboa/pyqt5/blob/master/examples/widgets/scribble.py
'''

from PyQt5.QtCore import QDir, QPoint, QRectF, QRect, QSize, Qt
from PyQt5.QtGui import QImage, QImageWriter, QPainter, QPen, QColor
from PyQt5.QtWidgets import QColorDialog, QFileDialog, QInputDialog, QMenu, QMessageBox
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QWidget
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

from utils.param import ParamDict

class ScribbleArea(QWidget):
    last_point = ParamDict(QPoint)
    pen_color = ParamDict(QColor)

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setAttribute(Qt.WA_StaticContents)
        self.modified = False # 追踪涂鸦的画布是否被改变
        self.scribbling = False # 追踪是否正处于涂鸦的状态
        self.pen_width = 1  # 画笔的宽度
        self.image = QImage() # 涂鸦的画板
        self.last_point = QPoint() # 鼠标左键当前位置
        self.pen_color = QColor('blue') #画笔颜色

    @property
    def pen(self):
        '''设置画笔的样式
        等价于 QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        '''
        pen = QPen() # 创建画笔
        pen.setColor(self.pen_color) # 设定画笔颜色
        pen.setWidth(self.pen_width) # 设定画笔的笔尖宽度
        pen.setStyle(Qt.SolidLine) # 设定画笔的线条样式
        pen.setCapStyle(Qt.RoundCap) # 设定画笔的笔帽样式
        pen.setJoinStyle(Qt.RoundJoin)  # 设定画笔的画出的线条的连接方式
        return pen

    def draw_line_to(self, end_point):
        painter = QPainter(self.image) # 涂鸦者
        painter.setPen(self.pen) # 设定画笔
        painter.drawLine(self.last_point, end_point) # 画出线段
        self.modified = True # 画板内容被改动
        # 补足点之间的间隙
        rad = self.pen_width / 2 + 2
        rect = QRect(self.last_point, end_point).normalized().adjusted(-rad, -rad, +rad, +rad)
        self.update(rect)
        self.last_point = end_point

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.draw_line_to(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.draw_line_to(event.pos())
            self.scribbling = False

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)

    def clear_image(self):
        self.image.fill(QColor(255, 255, 255, 20))
        self.modified = True
        self.update()

    def resize_image(self, image, newSize):
        if image.size() == newSize:
            return
        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(QColor(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage
    
    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resize_image(self.image, QSize(newWidth, newHeight))
            self.update()

    def open_image(self, fileName):
        if not self.image.load(fileName):
            return False
        else:
            self.modified = False
            self.update()
            return True

    def save_image(self, fileName, fileFormat):
        visibleImage = self.image
        self.resize_image(visibleImage, self.size())
        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)
        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(),
                                size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

class ScribbleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.saveAsActs = []
        self.scribbleArea = ScribbleArea()
        self.setCentralWidget(self.scribbleArea)
        self.create_actions()
        self.create_menus()
        self.setWindowTitle("Scribble")
        self.resize(500, 500)

    def maybe_save(self):
        if self.scribbleArea.modified:
            ret = QMessageBox.warning(self, "Scribble",
                                      "The scribble has been modified.\n"
                                      "Do you want to save your changes?",
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.save_file('png')
            elif ret == QMessageBox.Cancel:
                return False
        return True

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def open(self):
        if self.maybe_save():
            fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                                                      QDir.currentPath())
            if fileName:
                self.scribbleArea.open_image(fileName)

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.save_file(fileFormat)

    def pen_color(self):
        newColor = QColorDialog.getColor(self.scribbleArea.pen_color)
        if newColor.isValid():
            self.scribbleArea.pen_color = newColor

    def pen_width(self):
        newWidth, ok = QInputDialog.getInt(self, "Scribble",
                                           "Select pen width:", self.scribbleArea.pen_width, 1, 50, 1)
        if ok:
            self.scribbleArea.pen_width = newWidth

    def about(self):
        QMessageBox.about(self, "About Scribble",
                          "<p>The <b>Scribble</b> example shows how to use "
                          "QMainWindow as the base widget for an application, and how "
                          "to reimplement some of QWidget's event handlers to receive "
                          "the events generated for the application's widgets:</p>"
                          "<p> We reimplement the mouse event handlers to facilitate "
                          "drawing, the paint event handler to update the application "
                          "and the resize event handler to optimize the application's "
                          "appearance. In addition we reimplement the close event "
                          "handler to intercept the close events before terminating "
                          "the application.</p>"
                          "<p> The example also demonstrates how to use QPainter to "
                          "draw an image in real time, as well as to repaint "
                          "widgets.</p>")

    def create_actions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                               triggered=self.open)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QAction("&Print...", self,
                                triggered=self.scribbleArea.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               triggered=self.close)

        self.penColorAct = QAction("&Pen Color...", self,
                                   triggered=self.pen_color)

        self.penWidthAct = QAction("Pen &Width...", self,
                                   triggered=self.pen_width)

        self.clearScreenAct = QAction("&Clear Screen", self, shortcut="Ctrl+L",
                                      triggered=self.scribbleArea.clear_image)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                                  triggered=QApplication.instance().aboutQt)

    def create_menus(self):
        self.saveAsMenu = QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def save_file(self, fileFormat):
        initialPath = QDir.currentPath() + '/untitled.' + fileFormat

        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                                                  "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.save_image(fileName, fileFormat)

        return False

def run(window_type, *args, **kwargs):
    import sys
    app = QApplication(sys.argv)
    window = window_type(*args, **kwargs)
    window.show()
    app.exec_()

if __name__ == "__main__":
    run(ScribbleWindow)
```
