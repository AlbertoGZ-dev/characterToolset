'''
-----------------------------------------
Description: CharacterToolset is a tool to set repetitive settings for polygon meshes, shading, texture files and scene.

Autor: AlbertoGZ
Email: albertogzonline@gmail.com
-----------------------------------------
'''

from select import select
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
from collections import OrderedDict

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import re
import os


# GENERAL VARS
version = '0.1.1'
winWidth = 900
winHeight = 400
red = '#872323'
green = '#207527'
lightblue = '#7d654b'
lightpurple = '#604b69'
lightgreen = '#5b694b'

global meshSelected


def getMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return mainWindow


class characterToolset(QtWidgets.QMainWindow):

    def __init__(self, parent=getMainWindow()):
        super(characterToolset, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        # Creates object, Title Name and Adds a QtWidget as our central widget/Main Layout
        self.setObjectName('characterToolsetUI')
        self.setWindowTitle('Character Toolset' + ' ' + 'v' + version)
        mainLayout = QtWidgets.QWidget(self)
        self.setCentralWidget(mainLayout)

        
        # Adding a Horizontal layout to divide the UI in columns
        columns = QtWidgets.QHBoxLayout(mainLayout)

        # Creating N vertical layout
        self.col1 = QtWidgets.QVBoxLayout()
        self.col2 = QtWidgets.QVBoxLayout()
        self.col3 = QtWidgets.QVBoxLayout()
        self.col4 = QtWidgets.QVBoxLayout()
        self.col5 = QtWidgets.QVBoxLayout()
        

        # Set columns for each layout using stretch policy
        columns.addLayout(self.col1, 3)
        columns.addLayout(self.col2, 0)
        columns.addLayout(self.col3, 3)
        columns.addLayout(self.col4, 3)
        columns.addLayout(self.col5, 3)
    

        # Adding layouts
        layout = QtWidgets.QVBoxLayout()
        layout1 = QtWidgets.QVBoxLayout()
        layout1A = QtWidgets.QVBoxLayout()
        layout1B = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QGridLayout(alignment=QtCore.Qt.AlignTop)
        layout3 = QtWidgets.QVBoxLayout()
        layout3A = QtWidgets.QVBoxLayout()
        layout3B = QtWidgets.QHBoxLayout()
        layout4 = QtWidgets.QGridLayout(alignment=QtCore.Qt.AlignTop)
        layout5 = QtWidgets.QGridLayout(alignment=QtCore.Qt.AlignTop)
    
        
        self.col1.addLayout(layout1)
        self.col2.addLayout(layout2)
        self.col3.addLayout(layout3)   
        self.col4.addLayout(layout4)      
        self.col5.addLayout(layout5) 
    
        layout1.addLayout(layout1A)
        layout1.addLayout(layout1B)
        layout2.addLayout(layout2, 1, 1)
        layout3.addLayout(layout3A)
        layout3.addLayout(layout3B)
        layout4.addLayout(layout4, 1, 1)
        layout5.addLayout(layout5, 1, 1)
        
       

        

        ### UI ELEMENTS
        #     

        ## GEOMETRY
        self.geometryLabel = QtWidgets.QLabel('Geometry (Objects)')
        self.geometryFooLabel = QtWidgets.QLabel('')
       
        # SearchBox input for filter list (mesh)
        self.meshSearchBox = QtWidgets.QLineEdit('', self)
        self.meshRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.meshValidator = QtGui.QRegExpValidator(self.meshRegex)
        self.meshSearchBox.setValidator(self.meshValidator)
        self.meshSearchBox.textChanged.connect(self.meshFilter)
        self.meshSearchBox.setStyleSheet('background-color:' + lightblue)

        # List of polygon objects (mesh)
        self.meshQList = QtWidgets.QListWidget(self)
        self.meshQList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.meshQList.setMinimumWidth(150)
        self.meshQList.itemSelectionChanged.connect(self.meshSel)
        self.meshQList.setStyleSheet('background-color:' + lightblue)

        self.selectMeshLabel = QtWidgets.QLabel('Select')
        
        # All button select (mesh)
        self.selAllMeshBtn = QtWidgets.QPushButton('All')
        self.selAllMeshBtn.setFixedWidth(70)
        self.selAllMeshBtn.clicked.connect(self.selectAllMesh)
        self.selAllMeshBtn.setStyleSheet('background-color:' + lightblue)

        # None button select (mesh)
        self.selNoneMeshBtn = QtWidgets.QPushButton('None')
        self.selNoneMeshBtn.setFixedWidth(70)
        self.selNoneMeshBtn.clicked.connect(self.selectNoneMesh)
        self.selNoneMeshBtn.setStyleSheet('background-color:' + lightblue)

        # Mesh Reload button (mesh)
        self.reloadMeshBtn = QtWidgets.QPushButton('Reload')
        self.reloadMeshBtn.clicked.connect(self.reloadMesh)
        self.reloadMeshBtn.setStyleSheet('background-color:' + lightblue)

        # Viewport Subdiv button
        self.viewportSubdivBtn = QtWidgets.QPushButton('Viewport Subdiv to 0')
        self.viewportSubdivBtn.clicked.connect(self.setViewportSubdiv)
        self.viewportSubdivBtn.setFixedWidth(200)
        self.viewportSubdivBtn.setStyleSheet('background-color:' + lightblue)

        # Arnold Subdiv button
        self.subdivBtn = QtWidgets.QPushButton('Arnold Subdiv')
        self.subdivBtn.clicked.connect(self.setSubdiv)
        self.subdivBtn.setStyleSheet('background-color:' + lightblue)

        self.subdivValue = QtWidgets.QSpinBox()
        self.subdivValue.setValue(2)
        self.subdivValue.setStyleSheet('background-color:' + lightblue)
        self.subdivValue.setFixedHeight(22)


        ## SHADING
        self.shadingLabel = QtWidgets.QLabel('Shading (Textures)')
        self.shadingFooLabel = QtWidgets.QLabel('')
       
        # SearchBox input for filter texture list (file)
        self.fileSearchBox = QtWidgets.QLineEdit('', self)
        self.fileRegex = QtCore.QRegExp('[0-9A-Za-z_]+')
        self.fileValidator = QtGui.QRegExpValidator(self.fileRegex)
        self.fileSearchBox.setValidator(self.fileValidator)
        self.fileSearchBox.textChanged.connect(self.fileFilter)
        self.fileSearchBox.setStyleSheet('background-color:' + lightpurple)

        # List of textures (file)
        self.fileQList = QtWidgets.QListWidget(self)
        self.fileQList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.fileQList.setMinimumWidth(150)
        self.fileQList.itemSelectionChanged.connect(self.fileSel)
        self.fileQList.setStyleSheet('background-color:' + lightpurple)

        self.selectFileLabel = QtWidgets.QLabel('Select')
        
        # All button select (file)
        self.selAllFileBtn = QtWidgets.QPushButton('All')
        self.selAllFileBtn.setFixedWidth(70)
        self.selAllFileBtn.clicked.connect(self.selectAllFile)
        self.selAllFileBtn.setStyleSheet('background-color:' + lightpurple)

        # None button select (file)
        self.selNoneFileBtn = QtWidgets.QPushButton('None')
        self.selNoneFileBtn.setFixedWidth(70)
        self.selNoneFileBtn.clicked.connect(self.selectNoneFile)
        self.selNoneFileBtn.setStyleSheet('background-color:' + lightpurple)

        # Reload button (file)
        self.reloadFileBtn = QtWidgets.QPushButton('Reload')
        self.reloadFileBtn.clicked.connect(self.fileReload)
        self.reloadFileBtn.setStyleSheet('background-color:' + lightpurple)
       
        # Lambert button
        self.lambertBtn = QtWidgets.QPushButton('Lambert Mat')
        self.lambertBtn.clicked.connect(self.setLambertMat)
        self.lambertBtn.setFixedWidth(200)
        self.lambertBtn.setStyleSheet('background-color:' + lightpurple)

        # Remove Unused Materials
        self.removeMatsBtn = QtWidgets.QPushButton('Remove Unused Materials')
        self.removeMatsBtn.clicked.connect(self.removeMats)
        self.removeMatsBtn.setStyleSheet('background-color:' + lightpurple)

        # Ignore Color Space File Rules button
        self.ignoreCsRulesBtn = QtWidgets.QPushButton('Ignore Color Space File Rules')
        self.ignoreCsRulesBtn.clicked.connect(self.ignoreCSRules)
        self.ignoreCsRulesBtn.setStyleSheet('background-color:' + lightpurple)
        self.ignoreCsRulesBtn.setDisabled(False)

        # Set RAW ColorSpace for file texture
        self.fileColorSpaceRawBtn = QtWidgets.QPushButton('Texture ColorSpace to RAW')
        self.fileColorSpaceRawBtn.clicked.connect(self.setColorSpaceRaw)
        self.fileColorSpaceRawBtn.setStyleSheet('background-color:' + lightpurple)

        # Set sRGB ColorSpace for file texture
        self.fileColorSpaceSRGBBtn = QtWidgets.QPushButton('Texture ColorSpace to sRGB')
        self.fileColorSpaceSRGBBtn.clicked.connect(self.setColorSpaceSRGB)
        self.fileColorSpaceSRGBBtn.setStyleSheet('background-color:' + lightpurple)


        

        ## OUTLINER
        self.outlinerLabel = QtWidgets.QLabel('Outliner')

        # Hide Default Views button
        self.hideViewsBtn = QtWidgets.QPushButton('Hide views')
        self.hideViewsBtn.clicked.connect(self.hideViews)
        self.hideViewsBtn.setFixedWidth(200)
        self.hideViewsBtn.setStyleSheet('background-color:' + lightgreen)

        # Hide Default Sets button
        self.hideSetsBtn = QtWidgets.QPushButton('Hide Sets')
        self.hideSetsBtn.clicked.connect(self.hideSets)
        self.hideSetsBtn.setStyleSheet('background-color:' + lightgreen)

    

        # Status bar
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.messageChanged.connect(self.statusChanged)

        # Spacer
        separator = QtWidgets.QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color:rgb(255,0,0)")           
        
       
        #### Adding all elements to layouts
        layout1A.addWidget(self.geometryLabel)
        layout1A.addWidget(self.meshSearchBox)
        layout1A.addWidget(self.meshQList)
        layout1B.addWidget(self.selectMeshLabel)
        layout1B.addWidget(self.selAllMeshBtn)
        layout1B.addWidget(self.selNoneMeshBtn)
        layout1A.addWidget(self.reloadMeshBtn)

        layout2.addWidget(self.geometryFooLabel)
        layout2.addWidget(self.viewportSubdivBtn, 1,0)
        layout2.addWidget(self.subdivBtn, 2,0)
        layout2.addWidget(self.subdivValue, 2,1)

        layout3A.addWidget(self.shadingLabel)
        layout3A.addWidget(self.fileSearchBox)
        layout3A.addWidget(self.fileQList)
        layout3B.addWidget(self.selectFileLabel)
        layout3B.addWidget(self.selAllFileBtn)
        layout3B.addWidget(self.selNoneFileBtn)
        layout3A.addWidget(self.reloadFileBtn)

        layout4.addWidget(self.shadingFooLabel)
        layout4.addWidget(self.lambertBtn, 1,0)
        layout4.addWidget(self.removeMatsBtn, 2,0)
        layout4.addWidget(self.ignoreCsRulesBtn, 3,0)
        layout4.addWidget(self.fileColorSpaceRawBtn, 4,0)
        layout4.addWidget(self.fileColorSpaceSRGBBtn, 5,0)
        
        layout5.addWidget(self.outlinerLabel)
        layout5.addWidget(self.hideViewsBtn)
        layout5.addWidget(self.hideSetsBtn)


        self.resize(winWidth, winHeight)    


        ### INIT   
        self.meshLoad()
        self.fileLoad()
        self.selectNoneMesh()
        self.selectNoneFile()


    
    ### Filter name in meshList (mesh)
    def meshFilter(self):
        textFilter = str(self.meshSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.meshQList.count()):
                self.meshQList.setRowHidden(row, False)
        else:
            for row in range(self.meshQList.count()):
                if textFilter in str(self.meshQList.item(row).text()).lower():
                    self.meshQList.setRowHidden(row, False)
                else:
                    self.meshQList.setRowHidden(row, True)
    

    def reloadMesh(self):
        self.meshQList.clear()
        del meshSelected[:]
        self.meshLoad()


    def meshLoad(self):
        global meshList
        meshList = []
        meshList.append(cmds.ls(type='mesh'))
        
        for mesh in meshList:
            mesh = [w.replace('Shape', '') for w in mesh]
            mesh.sort()
            self.meshQList.addItems(mesh)


    ### Get selected meshes items in meshQList
    def meshSel(self):
        global meshSelected

        items = self.meshQList.selectedItems()
        meshSelected = []
        for i in items:
            meshSelected.append(i.text())
        
        return meshSelected
        #self.statusBar.showMessage(str(meshSelected), 4000) #for testing
    


    ### Set Viewport Subdiv to 0
    def setViewportSubdiv(self):

        if meshSelected != []:
            for mesh in meshSelected:
                cmds.displaySmoothness(mesh, du=0, dv=0, pw=4, ps=1, po=1 )
                
            self.statusBar.showMessage('Changed Viewport Subdiv successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    ### Set Arnold Subdiv
    def setSubdiv(self):
        subdivIt = self.subdivValue.value()

        if meshSelected != []:
            for mesh in meshSelected:
                cmds.setAttr( mesh + '.aiSubdivType', 1 )
                cmds.setAttr( mesh + '.aiSubdivIterations', subdivIt)
                
            self.statusBar.showMessage('Changed Arnlod Subdiv successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)



    
    
    
    
    ### Filter name in fileList (file)
    def fileFilter(self):
        textFilter = str(self.fileSearchBox.text()).lower()
        if not textFilter:
            for row in range(self.fileQList.count()):
                self.fileQList.setRowHidden(row, False)
        else:
            for row in range(self.fileQList.count()):
                if textFilter in str(self.fileQList.item(row).text()).lower():
                    self.fileQList.setRowHidden(row, False)
                else:
                    self.fileQList.setRowHidden(row, True)
    

    def fileReload(self):
        self.fileQList.clear()
        del meshSelected[:]
        self.fileLoad()


    def fileLoad(self):
        global fileList
        fileList = []
        fileList.append(cmds.ls(type='file'))
        
        for file in fileList:
            #file = [w.replace('Shape', '') for w in file]
            file.sort()
            self.fileQList.addItems(file)


    ### Get selected files in fileQList (file)
    def fileSel(self):
        global fileSelected

        items = self.fileQList.selectedItems()
        fileSelected = []
        for i in items:
            fileSelected.append(i.text())
        
        return fileSelected
        



    ### Set Lambert Mat
    def setLambertMat(self):
        '''
        def create_shader(name, node_type="lambert"):
            material = cmds.shadingNode(node_type, name=name, asShader=True)
            sg = cmds.sets(name="%sSG" % name, empty=True, renderable=True, noSurfaceShader=True)
            cmds.connectAttr("%s.outColor" % material, "%s.surfaceShader" % sg)
            return material, sg
        
        mtl, sg = create_shader("lambert")
        '''
        
        if meshSelected != []:
            for mesh in meshSelected:
                cmds.sets(mesh, forceElement='initialShadingGroup')
            
            self.statusBar.showMessage('Set Lambert Material successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected. You must to select at least one object', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    ### Remove Unused Materials
    def removeMats(self):
        mel.eval('MLdeleteUnused;')
        self.statusBar.showMessage('Unused materials removed', 4000)
        self.statusBar.setStyleSheet('background-color:' + green)


    ### Ignore Colorspace Rules
    def ignoreCSRules(self):

        if fileSelected != []:
            for file in fileSelected:
                cmds.setAttr(file + '.ignoreColorSpaceFileRules', True)
              
            self.statusBar.showMessage('Set Ignore ColorSpace File Rules successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    
    ### Set RAW ColorSpace for textures
    def setColorSpaceRaw(self):

        if fileSelected != []:
            for file in fileSelected:
                cmds.setAttr(file + '.colorSpace', 'Raw', type='string')
              
            self.statusBar.showMessage('Set texture ColorSpace to RAW successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)


    ### Set sRGB ColorSpace for textures
    def setColorSpaceSRGB(self):

        if fileSelected != []:
            for file in fileSelected:
                cmds.setAttr(file + '.colorSpace', 'sRGB', type='string')
              
            self.statusBar.showMessage('Set texture ColorSpace to RAW successfully!', 4000)
            self.statusBar.setStyleSheet('background-color:' + green)
        else:
            self.statusBar.showMessage('Nothing selected', 4000)
            self.statusBar.setStyleSheet('background-color:' + red)
        
       
    ### Hide Views
    def hideViews(self):
        #mel.eval('setAttr persp.hiddenInOutliner false;AEdagNodeCommonRefreshOutliners();')
        cmds.setAttr('persp.hiddenInOutliner', True)
        cmds.setAttr('top.hiddenInOutliner', True)
        cmds.setAttr('front.hiddenInOutliner', True)
        cmds.setAttr('side.hiddenInOutliner', True)
        mel.eval('AEdagNodeCommonRefreshOutliners();')     
        
        self.statusBar.showMessage('Hidding views successfully!', 4000)
        self.statusBar.setStyleSheet('background-color:' + green)


    ### Hide Default Sets
    def hideSets(self):
        cmds.setAttr('defaultLightSet.hiddenInOutliner', True)
        cmds.setAttr('defaultObjectSet.hiddenInOutliner', True)
        mel.eval('AEdagNodeCommonRefreshOutliners();')     
        
        self.statusBar.showMessage('Hidding sets successfully!', 4000)
        self.statusBar.setStyleSheet('background-color:' + green)



    def statusChanged(self, args):
        if not args:
            self.statusBar.setStyleSheet('background-color:none')
      

    def selectAllMesh(self):
        self.meshQList.selectAll()

        
    def selectNoneMesh(self):
        self.meshQList.clearSelection()
        del meshSelected[:]
        

    def selectAllFile(self):
        self.fileQList.selectAll()
       
   
    def selectNoneFile(self):
        self.fileQList.clearSelection()
        del fileSelected[:]
       

     
    def closeEvent(self, event):
        del meshSelected[:]
        pass


if __name__ == '__main__':
    win = characterToolset(parent=getMainWindow())
    try:
        win.close()
    except:
        pass
  
    win.show()
    win.raise_()
