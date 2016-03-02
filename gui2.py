
#!/usr/bin/env python


# imports Sip library, contains interface moduels for C++
import sip

# converts QString to Py v2 unicode rather than Py type, was needed for prototyping
sip.setapi('QString', 2)

# imports python maths module, lots of useful tools
import math

# from PyQt4 library imports QtCore and QtGui, these are the only two used
from PyQt4 import QtCore, QtGui
from os import path
from yaml import load

import diagramscene_rc







# Path Class handles connecting path between nodes
class Path(QtGui.QGraphicsLineItem):

    # initiation function, takes 5 arguments in total the 2 none standard ones hold the ID for the two nodes being connected
    # rest of code properties and ui config
    def __init__(self, sitem, eitem, parent = None, scene = None):
        super(Path, self).__init__(parent, scene)

        self.pathend = QtGui.QPolygonF()

        self.thisstart = sitem
        self.thisend = eitem
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.thiscolor = QtCore.Qt.black
        self.setPen(QtGui.QPen(self.thiscolor, 2, QtCore.Qt.SolidLine,
                               QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    # set functions for colour, start position and end position
    def setColor(self, color):
        self.thiscolor = color

    def startItem(self):
        return self.thisstart

    def endItem(self):
        return self.thisend

    # setting snap properties
    def boundingRect(self):
        extra = (self.pen().width() + 10) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)


    def shape(self):
        path = super(Path, self).shape()
        path.addPolygon(self.pathend)
        return path

    # updates position ui properties if nodes move ect
    def updatePosition(self):
        line = QtCore.QLineF(self.mapFromItem(self.thisstart, 0, 0), self.mapFromItem(self.thisend, 0, 0))
        self.setLine(line)

    # draw the line
    def paint(self, painter, option, widget=None):
        if (self.thisstart.collidesWithItem(self.thisend)):
            return

        # myStartItem and myEndItem hold object ID for respective nodes, this block mainly just deals with the UI and
        # actually drawing and updating the path between nodes
        myStartItem = self.thisstart
        myEndItem = self.thisend
        myColor = self.thiscolor
        myPen = self.pen()
        myPen.setColor(self.thiscolor)
        arrowSize = 10.0
        painter.setPen(myPen)
        painter.setBrush(self.thiscolor)

        centerLine = QtCore.QLineF(myStartItem.pos(), myEndItem.pos())
        endPolygon = myEndItem.polygon()
        p1 = endPolygon.first() + myEndItem.pos()

        intersectPoint = QtCore.QPointF()
        for i in endPolygon:
            p2 = i + myEndItem.pos()
            polyLine = QtCore.QLineF(p1, p2)
            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QtCore.QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QtCore.QLineF(intersectPoint, myStartItem.pos()))
        line = self.line()

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.pathend.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.pathend.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.pathend)
        if self.isSelected():
            painter.setPen(QtGui.QPen(myColor, 1, QtCore.Qt.DashLine))
            myLine = QtCore.QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)




# DiagramItem mainly deals with the setting up and drawing of the node objects, for now flow chart symbols are used
# as they were easy to draw
class DiagramItem(QtGui.QGraphicsPolygonItem):
    Step, Conditional, StartEnd, Io = range(4)

    # standard initiation function that takes two extras, diagramType allows the node config to be setup and context menu
    # is for a future feature where a user can right click on a node and see a list of functions.
    def __init__(self, diagramType, contextMenu, parent=None, scene=None):
        super(DiagramItem, self).__init__(parent, scene)

        self.arrows = []

        self.diagramType = diagramType
        self.contextMenu = contextMenu

        path = QtGui.QPainterPath()
        if self.diagramType == self.StartEnd:
            path.moveTo(200, 50)
            path.arcTo(150, 0, 50, 50, 0, 90)
            path.arcTo(50, 0, 50, 50, 90, 90)
            path.arcTo(50, 50, 50, 50, 180, 90)
            path.arcTo(150, 50, 50, 50, 270, 90)
            path.lineTo(200, 25)
            self.myPolygon = path.toFillPolygon()
        elif self.diagramType == self.Conditional:
            self.myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(-25, 0), QtCore.QPointF(0, 25),
                    QtCore.QPointF(25, 0), QtCore.QPointF(0, -25),
                    QtCore.QPointF(-25, 0)])
        elif self.diagramType == self.Step:
            self.myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(-25, -25), QtCore.QPointF(25, -25),
                    QtCore.QPointF(25, 25), QtCore.QPointF(-25, 25),
                    QtCore.QPointF(-25, -25)])
        else:
            self.myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(-30, -20), QtCore.QPointF(-15, 20),
                    QtCore.QPointF(30, 20), QtCore.QPointF(15, -20),
                    QtCore.QPointF(-30, -20)])


        self.setPolygon(self.myPolygon)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        


    # some delete logic to remove edges
    def removeArrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass

    def removeArrows(self):
        for arrow in self.arrows[:]:
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)

    # logic to add edges
    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def image(self):
        pixmap = QtGui.QPixmap(250, 250)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        return pixmap

    # context menu not in yet
    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction(self.cutAct)
        menu.addAction(self.copyAct)
        menu.addAction(self.pasteAct)

        self.scene().clearSelection()
        self.setSelected(True)
        self.menu.exec_(event.screenPos())


    def cut(self):
        self.infoLabel.setText("Invoked <b>Edit|Cut</b>")

    def copy(self):
        self.infoLabel.setText("Invoked <b>Edit|Copy</b>")

    def paste(self):
        self.infoLabel.setText("Invoked <b>Edit|Paste</b>")


    # update function for movement of nodes
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.updatePosition()

        return value




# DiagramScene mainly deals with the setting up of the actual diagram window, it is mostly made up of UI code as well as
# logic for the movement, deletion and pretty much all interaction with the scene itsef
class DiagramScene(QtGui.QGraphicsScene):
    InsertItem, InsertLine, InsertText, MoveItem  = range(4)

    itemInserted = QtCore.pyqtSignal(DiagramItem)

    itemSelected = QtCore.pyqtSignal(QtGui.QGraphicsItem)

    # initiation function takes itemMenu which is effectively an object ID for the relevant button.
    def __init__(self, itemMenu, parent=None):
        super(DiagramScene, self).__init__(parent)

        self.myItemMenu = itemMenu
        self.myMode = self.MoveItem
        self.myItemType = DiagramItem.Step
        self.line = None
        self.textItem = None
        self.myItemColor = QtCore.Qt.white
        self.myTextColor = QtCore.Qt.black
        self.myLineColor = QtCore.Qt.black



    # set path (edge) colour
    def setLineColor(self, color):
        self.myLineColor = color
        if self.isItemChange(Path):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()

    # set node colour
    def setItemColor(self, color):
        self.myItemColor = color
        if self.isItemChange(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.myItemColor)

    # set mouse mode
    def setMode(self, mode):
        self.myMode = mode

    # set type
    def setItemType(self, type):
        self.myItemType = type

    # will be used for a future feature
    def editorLostFocus(self, item):
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)

        if item.toPlainText():
            self.removeItem(item)
            item.deleteLater()

    # Mouse logic
    # mouse click
    def mousePressEvent(self, mouseEvent):

        #get the cursor position in the scene on  mouse click
        cursor = QtGui.QCursor()
        position = QtCore.QPointF(mouseEvent.scenePos())
        cursorPosition = position.x(), position.y()
        #position = cursor.pos().x(),  cursor.pos().y()
        x = cursorPosition[0]
        y = cursorPosition[1]
        print 'Cursor Position '' X :', x, 'Y :', y


        if (mouseEvent.button() != QtCore.Qt.LeftButton):
            return

            #NODE STUFF GOES HERE!!!
        if self.myMode == self.InsertItem:
            item = DiagramItem(self.myItemType, self.myItemMenu)
            item.setBrush(self.myItemColor)
            self.addItem(item)
            item.setPos(mouseEvent.scenePos())

            # trying to get node position
            positionN = QtCore.QPointF(mouseEvent.scenePos())
            nodePosition = positionN.x(), positionN.y()
            Xpe = nodePosition[0]
            Ype = nodePosition[1]

            Xo = -47.85
            Yo = -23.05

            Xpo = Xo - Xpe
            Ypo = Yo - Ype
            res = 0.05
            Xe= ((Xpe-Xpo)/res) +Xo
            Ye= ((Ype-Ypo)/res) +Yo 
            print 'Node Position '' X:', Xe, 'Y:', Ye

            self.itemInserted.emit(item)
        elif self.myMode == self.InsertLine:
            self.line = QtGui.QGraphicsLineItem(QtCore.QLineF(mouseEvent.scenePos(),
                                        mouseEvent.scenePos()))
            self.line.setPen(QtGui.QPen(self.myLineColor, 2))
            self.addItem(self.line)
            

        super(DiagramScene, self).mousePressEvent(mouseEvent)



    # moving/ dragging the mouse
    def mouseMoveEvent(self, mouseEvent):
        if self.myMode == self.InsertLine and self.line:
            newLine = QtCore.QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            super(DiagramScene, self).mouseMoveEvent(mouseEvent)



    # releasing/ dropping the mouse
    def mouseReleaseEvent(self, mouseEvent):


        if self.line and self.myMode == self.InsertLine:
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None
            

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], DiagramItem) and \
                    isinstance(endItems[0], DiagramItem) and \
                    startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                arrow = Path(startItem, endItem)
                arrow.setColor(self.myLineColor)
                startItem.addArrow(arrow)
                endItem.addArrow(arrow)
                arrow.setZValue(-1000.0)
                self.addItem(arrow)
                arrow.updatePosition()

            

        self.line = None
        super(DiagramScene, self).mouseReleaseEvent(mouseEvent)

    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False


############################################################################

# Properties window layout and widgets
class SlidersGroup(QtGui.QGroupBox):

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, label, parent=None):
        super(SlidersGroup, self).__init__(parent)

        self.formGroupBox = QtGui.QGroupBox("Node Properties")
        
    # Node Properties
    # editing the name property
        self.nlineEdit = QtGui.QLineEdit()
        self.nlineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)

    # map 
        self.mlineEdit = QtGui.QLineEdit()
        self.mlineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.elineEdit = QtGui.QLineEdit()
        self.lineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)


    # edge action combo box
        self.comboBox = QtGui.QComboBox()
        self.comboBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox.addItem("Run")
        self.comboBox.addItem("Walk")
        self.comboBox.addItem("climb")
 
    # changing node size slider
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)
        #self.slider.setBorder: 1px solid #999999

    # X axis (position for node)
        self.spinBoxX = QtGui.QSpinBox()
        self.spinBoxX.setFocusPolicy(QtCore.Qt.StrongFocus)

    # Y axis (position for node)
        self.spinBoxY = QtGui.QSpinBox()
        self.spinBoxY.setFocusPolicy(QtCore.Qt.StrongFocus)

    # Z axis -------
        self.spinBoxZ = QtGui.QSpinBox()
        self.spinBoxZ.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.spinBoxW = QtGui.QSpinBox()
        self.spinBoxW.setFocusPolicy(QtCore.Qt.StrongFocus)


        self.spinBoxVX = QtGui.QSpinBox()
        self.spinBoxVX.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.spinBoxVY = QtGui.QSpinBox()
        self.spinBoxVY.setFocusPolicy(QtCore.Qt.StrongFocus)

    # check box
        self.checkBox = QtGui.QCheckBox()
        self.checkBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.checkBox.toggle()

    # node orientation dial
        self.dial = QtGui.QDial()
        self.dial.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.dial.valueChanged.connect(self.slider.setValue)
        self.dial.valueChanged.connect(self.valueChanged)

    # Add widgets to the property window
        slidersLayout = QtGui.QFormLayout()
        slidersLayout.addRow(QtGui.QLabel("Name:"), self.nlineEdit)
        slidersLayout.addRow(QtGui.QLabel("Map:"), self.mlineEdit)
        slidersLayout.addRow(QtGui.QLabel("Pointset:"), self.lineEdit)
        slidersLayout.addRow(QtGui.QLabel("X axis:"), self.spinBoxX)
        slidersLayout.addRow(QtGui.QLabel("Y axis:"), self.spinBoxY)
        slidersLayout.addRow(QtGui.QLabel("Z axis"), self.spinBoxZ)
        slidersLayout.addRow(QtGui.QLabel("W axis"), self.spinBoxW)
        slidersLayout.addRow(QtGui.QLabel("Verts:"))
        slidersLayout.addRow(QtGui.QLabel("X axis:"), self.spinBoxVX)
        slidersLayout.addRow(QtGui.QLabel("Y axis:"), self.spinBoxVY)
        slidersLayout.addRow(QtGui.QLabel("Edges:"), self.elineEdit)


        slidersLayout.addRow(QtGui.QLabel("Orientation:"), self.dial)
        slidersLayout.addRow(QtGui.QLabel("Actions:"), self.comboBox)
        slidersLayout.addRow(QtGui.QLabel("Size:"), self.slider)

        self.setLayout(slidersLayout) 



    def setValue(self, value):    
        self.slider.setValue(value)    

    def setMinimum(self, value):    
        self.slider.setMinimum(value)
        self.dial.setMinimum(value)    

    def setMaximum(self, value):    
        self.slider.setMaximum(value)
        self.dial.setMaximum(value)    

   

############################################################################
# MainWindow class sets up the qt window and a bit of functionality
class MainWindow(QtGui.QMainWindow):
    InsertTextButton = 10

    # default init function sets up the window properties
    def __init__(self):
        super(MainWindow, self).__init__()

    # create main window widgets, menus and toolbars
        self.createActions()
        self.createMenus()
        self.createToolBox()
        self.createToolbars()

        pixmap = QtGui.QImage('collection1-cropped.pgm')
    
        self.scene = DiagramScene(self.itemMenu)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 1000, 1000))
        self.scene.itemInserted.connect(self.itemInserted)
        self.scene.itemSelected.connect(self.itemSelected)
        #self.scene.addPixmap(pixmap)

    # main window layout and adding widgets:toolbox, scene and property window 
    # sequential order of drawing objects on main window
        # adding toolbox to the main window layout
        mainlayout = QtGui.QHBoxLayout()
        mainlayout.addWidget(self.toolBox)

        # adding scene/ view to the main window layout
        self.view = QtGui.QGraphicsView(self.scene)
        mainlayout.addWidget(self.view)

        
        # adding properties panel to the main window layout
        self.properties = SlidersGroup(self)
        mainlayout.addWidget(self.properties)

        # main window settings
        self.widget = QtGui.QWidget()
        self.widget.setLayout(mainlayout)
        self.setCentralWidget(self.widget)
        self.setWindowTitle("Topological Navigation Editor")


    # Widget logic setup, will be grouped into more classes in future just put here for convinence
    # changing the background colour
    def backgroundButtonGroupClicked(self, button):
        buttons = self.backgroundButtonGroup.buttons()
        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)

        text = button.text()
        if text == "Blue Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background1.png')))
        elif text == "White Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background2.png')))
        elif text == "Gray Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background3.png')))
        else:
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background4.png')))

        self.scene.update()
        self.view.update()

    # logic for map buttons to open maps
    def mapButtonGroupClicked(self, button):
        buttons = self.mapButtonGroup.buttons()


        map_fullpath = QtGui.QFileDialog.getOpenFileName()
        dir_path = path.dirname(map_fullpath)
        print dir_path

        if map_fullpath is not '':
            with open(map_fullpath, 'r') as stream:
                map_data = load(stream)
                print(map_data)
                #print path.join(dir_path, map_data['image'])
                map_data = map_data['image']
                d = QtGui.QImage(map_data)




        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)

        text = button.text()
        if text == "Map 1":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QImage(map_data)))
        elif text == "Map 2":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QImage(d)))
        elif text == "Gray Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background3.png')))
        else:
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background4.png')))

        self.scene.update()
        self.view.update()


    def buttonGroupClicked(self, id):
        buttons = self.buttonGroup.buttons()
        for button in buttons:
            if self.buttonGroup.button(id) != button:
                button.setChecked(False)

        if id == self.InsertTextButton:
            self.scene.setMode(DiagramScene.InsertText)
        else:
            self.scene.setItemType(id)
            self.scene.setMode(DiagramScene.InsertItem)

    def deleteItem(self):
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                item.removeArrows()
            self.scene.removeItem(item)

    def pointerGroupClicked(self, i):
        self.scene.setMode(self.pointerTypeGroup.checkedId())


    def itemInserted(self, item):
        self.pointerTypeGroup.button(DiagramScene.MoveItem).setChecked(True)
        self.scene.setMode(self.pointerTypeGroup.checkedId())
        self.buttonGroup.button(item.diagramType).setChecked(False)
        

    def textInserted(self, item):
        self.buttonGroup.button(self.InsertTextButton).setChecked(False)
        self.scene.setMode(self.pointerTypeGroup.checkedId())


    def sceneScaleChanged(self, scale):
        newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0
        oldMatrix = self.view.matrix()
        self.view.resetMatrix()
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.view.scale(newScale, newScale)

    def itemColorChanged(self):
        self.fillAction = self.sender()
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon(
                    ':/images/floodfill.png',
                    QtGui.QColor(self.fillAction.data())))
        self.fillButtonTriggered()


    def lineColorChanged(self):
        self.lineAction = self.sender()
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon(
                    ':/images/linecolor.png',
                    QtGui.QColor(self.lineAction.data())))
        self.lineButtonTriggered()


    def fillButtonTriggered(self):
        self.scene.setItemColor(QtGui.QColor(self.fillAction.data()))


    def lineButtonTriggered(self):
        self.scene.setLineColor(QtGui.QColor(self.lineAction.data()))


    def itemSelected(self, item):
        font = item.font()
        color = item.defaultTextColor()
        self.fontCombo.setCurrentFont(font)
        self.fontSizeCombo.setEditText(str(font.pointSize()))
        self.boldAction.setChecked(font.weight() == QtGui.QFont.Bold)
        self.italicAction.setChecked(font.italic())
        self.underlineAction.setChecked(font.underline())


    def about(self):
        QtGui.QMessageBox.about(self, "About Diagram Scene",
                "Test program for robot mapping application for university of lincoln")


    # grid layout toolbox for nodes (different shapes)
    def createToolBox(self):
        self.buttonGroup = QtGui.QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

    # adding nodes to the toolbox
        layout = QtGui.QGridLayout()
        layout.addWidget(self.createCellWidget("Conditional", DiagramItem.Conditional),
                0, 0)
        layout.addWidget(self.createCellWidget("Process", DiagramItem.Step), 0,
                1)
        layout.addWidget(self.createCellWidget("Input/Output", DiagramItem.Io),
                1, 0)
       
    # set row and column size
        layout.setRowStretch(3, 10)
        layout.setColumnStretch(2, 10)
        itemWidget = QtGui.QWidget()
        itemWidget.setLayout(layout)

    # buttons for changing the background
        self.backgroundButtonGroup = QtGui.QButtonGroup()
        self.backgroundButtonGroup.buttonClicked.connect(self.backgroundButtonGroupClicked)

        backgroundLayout = QtGui.QGridLayout()
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Blue Grid",
                ':/images/background1.png'), 0, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("White Grid",
                ':/images/background2.png'), 0, 1)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Gray Grid",
                ':/images/background3.png'), 1, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("No Grid",
                ':/images/background4.png'), 1, 1)

        backgroundLayout.setRowStretch(2, 10)
        backgroundLayout.setColumnStretch(2, 10)
        backgroundWidget = QtGui.QWidget()
        backgroundWidget.setLayout(backgroundLayout)


    # buttons for changing the maps
        self.mapButtonGroup = QtGui.QButtonGroup()
        self.mapButtonGroup.buttonClicked.connect(self.mapButtonGroupClicked)

        mapLayout = QtGui.QGridLayout()
        mapLayout.addWidget(self.createMapCellWidget("Map 1",
                'collection1-cropped.pgm'), 0, 0)
        mapLayout.addWidget(self.createMapCellWidget("Map 2",
                ':/images/background4.png'), 0, 1)
        mapLayout.addWidget(self.createMapCellWidget("Map 3",
                ':/images/background4.png'), 1, 0)
        mapLayout.addWidget(self.createMapCellWidget("map 4",
                ':/images/background4.png'), 1, 1)

        mapLayout.setRowStretch(2, 10)
        mapLayout.setColumnStretch(2, 10)
        mapWidget = QtGui.QWidget()
        mapWidget.setLayout(mapLayout)

    # creating a toolbox and adding menu widgets 
        self.toolBox = QtGui.QToolBox()
        self.toolBox.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox.addItem(itemWidget, "Nodes")
        self.toolBox.addItem(backgroundWidget, "Backgrounds")
        self.toolBox.addItem(mapWidget, "Maps")



    def createActions(self):
        self.deleteAction = QtGui.QAction(QtGui.QIcon(':/images/delete.png'),
                "&Delete", self, shortcut="Delete",
                statusTip="Delete item from diagram",
                triggered=self.deleteItem)

        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+X",
                statusTip="Quit Scenediagram example", triggered=self.close)

        self.aboutAction = QtGui.QAction("A&bout", self, shortcut="Ctrl+B",
                triggered=self.about)



    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.exitAction)

        self.itemMenu = self.menuBar().addMenu("&Item")
        self.itemMenu.addAction(self.deleteAction)
        self.itemMenu.addSeparator()

        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.aboutAction)



    def createToolbars(self):
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.deleteAction)

        # node colour tool button
        self.fillColorToolButton = QtGui.QToolButton()
        self.fillColorToolButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.fillColorToolButton.setMenu(
                self.createColorMenu(self.itemColorChanged, QtCore.Qt.white))
        self.fillAction = self.fillColorToolButton.menu().defaultAction()
        self.fillColorToolButton.setIcon(
                self.createColorToolButtonIcon(':/images/floodfill.png',
                        QtCore.Qt.white))
        self.fillColorToolButton.clicked.connect(self.fillButtonTriggered)

        # edge colour tool button
        self.lineColorToolButton = QtGui.QToolButton()
        self.lineColorToolButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.lineColorToolButton.setMenu(
                self.createColorMenu(self.lineColorChanged, QtCore.Qt.black))
        self.lineAction = self.lineColorToolButton.menu().defaultAction()
        self.lineColorToolButton.setIcon(
                self.createColorToolButtonIcon(':/images/linecolor.png',
                        QtCore.Qt.black))
        self.lineColorToolButton.clicked.connect(self.lineButtonTriggered)

        # add widgets to colour tool bar
        self.colorToolBar = self.addToolBar("Color")
        self.colorToolBar.addWidget(self.fillColorToolButton)
        self.colorToolBar.addWidget(self.lineColorToolButton)

        # toolbar (pointer tool)
        pointerButton = QtGui.QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setIcon(QtGui.QIcon(':/images/pointer.png'))

        # toolbar (edge tool)
        linePointerButton = QtGui.QToolButton()
        linePointerButton.setCheckable(True)
        linePointerButton.setIcon(QtGui.QIcon(':/images/linepointer.png'))

        self.pointerTypeGroup = QtGui.QButtonGroup()
        self.pointerTypeGroup.addButton(pointerButton, DiagramScene.MoveItem)
        self.pointerTypeGroup.addButton(linePointerButton,
                DiagramScene.InsertLine)
        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)

        self.pointerToolbar = self.addToolBar("Pointer type")
        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(linePointerButton)

    # creating buttons for changing backgroung
    def createBackgroundCellWidget(self, text, image):
        button = QtGui.QToolButton()
        button.setText(text)
        button.setIcon(QtGui.QIcon(image))
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        return widget


    # creating buttons to load maps
    def createMapCellWidget(self, text, image):
        button = QtGui.QToolButton()
        button.setText(text)
        button.setIcon(QtGui.QIcon(image))
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.mapButtonGroup.addButton(button)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        return widget


    # creating buttons to be used as nodes 
    def createCellWidget(self, text, diagramType):
        item = DiagramItem(diagramType, self.itemMenu)
        icon = QtGui.QIcon(item.image())

        button = QtGui.QToolButton()
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, diagramType)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        return widget

    # colour menu
    def createColorMenu(self, slot, defaultColor):
        colors = [QtCore.Qt.black, QtCore.Qt.white, QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.yellow]
        names = ["black", "white", "red", "blue", "yellow"]

        colorMenu = QtGui.QMenu(self)
        for color, name in zip(colors, names):
            action = QtGui.QAction(self.createColorIcon(color), name, self,
                    triggered=slot)
            action.setData(QtGui.QColor(color))
            colorMenu.addAction(action)
            if color == defaultColor:
                colorMenu.setDefaultAction(action)

        return colorMenu



    def createColorToolButtonIcon(self, imageFile, color):
        pixmap = QtGui.QPixmap(50, 80)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        image = QtGui.QPixmap(imageFile)
        target = QtCore.QRect(0, 0, 50, 60)
        source = QtCore.QRect(0, 0, 42, 42)
        painter.fillRect(QtCore.QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()

        return QtGui.QIcon(pixmap)


    # colour icon
    def createColorIcon(self, color):
        pixmap = QtGui.QPixmap(20, 20)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillRect(QtCore.QRect(0, 0, 20, 20), color)
        painter.end()

        return QtGui.QIcon(pixmap)


# Main function which calls the window
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 1000, 600)
    mainWindow.show()

    

    sys.exit(app.exec_())


