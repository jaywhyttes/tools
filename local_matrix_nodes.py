# simple tool to add mult matrix nodes between skinclusters and their influences
import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class local_mtx_sc(QtWidgets.QDialog):
    TITLE = "Localize skin matrix"
  
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = local_mtx_sc()
        
        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self):

        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        else:
            maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
            
        super(local_mtx_sc, self).__init__(maya_main_window)

        self.setWindowTitle(local_mtx_sc.TITLE)
        self.setMinimumSize(250,74)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()



    def create_widgets(self):
        self.local_node_le = QtWidgets.QLineEdit()
        self.local_node_le.setPlaceholderText("Leave Blank To Use Skinned Object")
        self.local_node_select_btn = QtWidgets.QPushButton(QtGui.QIcon(":moveUVLeft.png"),'')
        self.local_node_select_btn.setFixedSize(26, 19)
        self.add_mtx_bnt = QtWidgets.QPushButton("Add")
        self.remove_mtx_bnt = QtWidgets.QPushButton("Remove")
        self.close_bnt = QtWidgets.QPushButton("Close")

    def create_layouts(self):
        local_node_input_layout = QtWidgets.QHBoxLayout()

        local_node_input_layout.addWidget(self.local_node_le)
        local_node_input_layout.addWidget(self.local_node_select_btn)
        local_node_btn_layout = QtWidgets.QHBoxLayout()
        local_node_btn_layout.setSpacing(4)
        local_node_btn_layout.addWidget(self.add_mtx_bnt)
        local_node_btn_layout.addWidget(self.remove_mtx_bnt)
        local_node_btn_layout.addWidget(self.close_bnt)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(local_node_input_layout)
        main_layout.addLayout(local_node_btn_layout)
        main_layout.setContentsMargins(2,2,2,2)

    def create_connections(self):
        self.close_bnt.clicked.connect(self.close)
        self.add_mtx_bnt.clicked.connect(self.localizeSkinMtx)
        self.remove_mtx_bnt.clicked.connect(self.deLocalizeSkinMtx)
        self.local_node_select_btn.clicked.connect(self.set_le_text)

    def set_le_text(self):
        sel = cmds.ls(sl=True)[0]
        self.local_node_le.setText(sel)

    def deLocalizeSkinMtx(self):
        sel =cmds.ls(sl=True,type='skinCluster')
        if sel:
            for sc in sel:
                mtxNode = cmds.listConnections('{0}.matrix'.format(sc),source=1,type='multMatrix',et=1)
                for mtx in mtxNode:
                    skinJnt = cmds.listConnections('{0}.matrixIn'.format(mtx),source=1,type='joint',et=1)
                    scMtxPipe = cmds.listConnections('{0}.matrixSum'.format(mtx),plugs=1,type='skinCluster',et=1)

                    cmds.connectAttr('{0}.worldMatrix[0]'.format(skinJnt[0]),scMtxPipe[0],f=1)
                    cmds.delete(mtx)
        else:
            cmds.warning("[{0}]: Select a skincluster".format(local_mtx_sc.TITLE))
            return

    def localizeSkinMtx(self):
        localNode = self.local_node_le.text()
        if not localNode:
            localNode = None
        elif not cmds.objExists(localNode):
            localNode = None
        sel =cmds.ls(sl=True,type='skinCluster')

        if sel:
            for sc in sel:
                skinJnts = cmds.listConnections('{0}.matrix'.format(sc),source=1,type='joint',et=1)
                skinGeo = cmds.listConnections('{0}.outputGeometry'.format(sc),destination=1)
                for jnt in skinJnts:
                    scMtxPipe = cmds.listConnections('{0}.worldMatrix'.format(jnt),plugs=1,type='skinCluster',et=1)
                    for pipe in scMtxPipe:
                        if sc in pipe:
                            scJntMtx = pipe.split('.')[1]
                    mltMtxNode = cmds.createNode('multMatrix',n='{0}_local_mtx_mulMtx'.format(jnt))
                    cmds.connectAttr('{0}.worldMatrix[0]'.format(jnt),'{0}.matrixIn[0]'.format(mltMtxNode),f=1)
                    if localNode != None:
                        try:
                            cmds.connectAttr('{0}.worldInverseMatrix[0]'.format(localNode),'{0}.matrixIn[1]'.format(mltMtxNode),f=1)
                        except:
                            cmds.connectAttr('{0}.worldInverseMatrix[0]'.format(skinGeo[0]),'{0}.matrixIn[1]'.format(mltMtxNode),f=1)
                    else:
                        cmds.connectAttr('{0}.worldInverseMatrix[0]'.format(skinGeo[0]),'{0}.matrixIn[1]'.format(mltMtxNode),f=1)
                    cmds.connectAttr('{0}.matrixSum'.format(mltMtxNode),'{0}.{1}'.format(sc,scJntMtx),f=1)
                
        else:
            cmds.warning("[{0}]: Select a skincluster".format(local_mtx_sc.TITLE))
            return

if __name__ == "__main__":
    try:
        local_mtx_sc.close()
        local_mtx_sc.deleteLater()
    except:
        pass
    local_mtx_sc = local_mtx_sc()
    local_mtx_sc.show()
