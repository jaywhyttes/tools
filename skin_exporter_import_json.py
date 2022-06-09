#maya skinWeight exporter/import in json format
##############################################
#Author: Jason Whyttes
#Date: 17/05/2022
##############################################
#usage: allowers user to export and import
#       skin cluster information out and in
#       of maya in a json format
##############################################


import re
import sys
import json
import os

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds


class UserData():
    """
    handles the user data
    """
    def __init__(self, userName=None, userTime=None, platform=None):
        self.userName = userName
        self.userTime = userTime
        self.platform = platform
    # get the username, the time the file was created and the platform
    def get_user_data(self, user_name):
        self.userName = user_name
        self.userTime = '{0} - {1}'.format(cmds.about(currentDate=True),cmds.about(currentTime=True))
        self.platform = cmds.about(installedVersion=True)
        
    # set the user data json formatting
    def to_json(self):
        return {
            "user": self.userName,
            "created": self.userTime,
            "platform": self.platform
        }

class DeformerData():
    """
    get all the deformer data. skincluster, mesh, verts, and influences
    """
    def __init__(self, scName=None, meshName=None, meshVerts=None, influenceWeights=None):
        self.scName = scName
        self.meshName = meshName
        self.meshVerts = meshVerts
        self.influenceWeights = influenceWeights


    # get the bind data
    def get_mesh_data(self, mesh_deformer):
        inf_data = []
        # get the mesh name and the skin clusters influences
        sc_deformer = mesh_deformer
        mesh = cmds.skinCluster(sc_deformer, q=1, g=1)[0]
        influences = cmds.skinCluster(sc_deformer, query=True, influence=True)
        
        # get the influence values per vert on the mesh
        for i in range(0, len(influences)):
            inf_weight_data = []
            inf_info = {}
            inf_info["name"]=influences[i]
            inf_info["index"]=i
            for v in range(0, cmds.polyEvaluate(mesh,v=1)):
                inf_weight_data.append(cmds.skinPercent(sc_deformer,'{0}.vtx[{1}]'.format(mesh,v),t=influences[i],q=1,v=1))
            inf_info[str(i)]=inf_weight_data
            inf_data.append(inf_info)

        self.scName = sc_deformer
        self.meshName = cmds.listRelatives(cmds.skinCluster(sc_deformer, q=True, g=True),p=True, fullPath=True)[0]
        self.meshVerts = [v for v in range(cmds.polyEvaluate(mesh, v=True))]
        self.influenceWeights = inf_data

    # set the deformer data json formatting
    def to_json(self):
        return {
            "cluster": self.scName,
            "mesh": self.meshName,
            "vtx": self.meshVerts,
            "inf": self.influenceWeights
        }

class SCImportExport(QtWidgets.QDialog):
    """
    Create a gui for the exporter
    """
    TITLE = "Skin Cluster Exporter/Importer"
    json_data = None
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SCImportExport()
        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self):
        # check which version of python is being used by maya
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        else:
            maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        # parent our gui to mayas main window
        super(SCImportExport, self).__init__(maya_main_window)

        self.setWindowTitle(SCImportExport.TITLE)
        self.setMinimumSize(501,443)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.set_initial_values()

    def create_widgets(self):
        #export
        self.export_sc_node_cb = QtWidgets.QComboBox()
        self.export_sc_node_cb.setFixedWidth(336)
        self.export_sc_node_refresh_btn = QtWidgets.QPushButton(QtGui.QIcon(":refresh.png"), "")
        self.export_sc_node_refresh_btn.setFixedSize(26, 19)

        self.export_dir_path_le = QtWidgets.QLineEdit()
        self.export_dir_path_le.setPlaceholderText("{project}/data")
        self.export_dir_path_show_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.export_dir_path_show_folder_btn.setFixedSize(26, 19)
        self.export_dir_path_show_folder_btn.setToolTip("Open Explorer")

        self.sc_export_name_le = QtWidgets.QLineEdit()
        self.sc_export_creator_le = QtWidgets.QLineEdit()

        self.export_sc_h_line = QtWidgets.QFrame()
        self.export_sc_h_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.export_sc_h_line.setFrameShape(QtWidgets.QFrame.HLine)

        self.export_sc_cb_force_cb = QtWidgets.QCheckBox("Force overwrite")
        self.export_sc_cb_force_cb.setChecked(False)
        self.export_sc_btn = QtWidgets.QPushButton("Export")
        
        #import
        self.import_sc_node_cb = QtWidgets.QComboBox()
        self.import_sc_node_cb.setFixedWidth(336)
        self.import_sc_node_refresh_btn = QtWidgets.QPushButton(QtGui.QIcon(":refresh.png"), "")
        self.import_sc_node_refresh_btn.setFixedSize(26, 19)

        self.import_dir_path_le = QtWidgets.QLineEdit()
        self.import_dir_path_le.setPlaceholderText("{projects}/data")
        self.import_dir_path_show_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.import_dir_path_show_folder_btn.setFixedSize(26, 19)
        self.import_dir_path_show_folder_btn.setToolTip("Open Explorer")

        self.sc_import_name_le = QtWidgets.QLineEdit()
        self.sc_import_name_le.setReadOnly(True)
        self.sc_import_creator_le = QtWidgets.QLineEdit()
        self.sc_import_creator_le.setReadOnly(True)
        self.sc_created_import_date_le = QtWidgets.QLineEdit()
        self.sc_created_import_date_le.setReadOnly(True)
        self.sc_platform_le = QtWidgets.QLineEdit()
        self.sc_platform_le.setReadOnly(True)

        self.import_sc_btn = QtWidgets.QPushButton("Import")
        self.close_btn = QtWidgets.QPushButton("Close")
        
        self.import_sc_h_line_01 = QtWidgets.QFrame()
        self.import_sc_h_line_01.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.import_sc_h_line_01.setFrameShape(QtWidgets.QFrame.HLine)

        self.import_sc_h_line_02 = QtWidgets.QFrame()
        self.import_sc_h_line_02.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.import_sc_h_line_02.setFrameShape(QtWidgets.QFrame.HLine)

    def create_layouts(self):
        #export
        export_sc_find_def_layout = QtWidgets.QHBoxLayout()
        export_sc_find_def_layout.setSpacing(4)
        export_sc_find_def_layout.addWidget(self.export_sc_node_cb)
        export_sc_find_def_layout.addWidget(self.export_sc_node_refresh_btn)

        export_explorer_layout = QtWidgets.QHBoxLayout()
        export_explorer_layout.setSpacing(4)
        export_explorer_layout.addWidget(self.export_dir_path_le)
        export_explorer_layout.addWidget(self.export_dir_path_show_folder_btn)

        export_sc_layout = QtWidgets.QHBoxLayout()
        export_sc_layout.setSpacing(4)
        export_sc_layout.addWidget(self.export_sc_cb_force_cb)
        export_sc_layout.addStretch()
        export_sc_layout.addWidget(self.export_sc_btn)
        
        export_layout = QtWidgets.QFormLayout()
        export_layout.setSpacing(4)
        export_layout.addRow("Existing Clusters:", export_sc_find_def_layout)
        export_layout.addRow("Directory:", export_explorer_layout)
        export_layout.addRow("Name:", self.sc_export_name_le)
        export_layout.addRow("Creator:", self.sc_export_creator_le)
        export_layout.addRow(self.export_sc_h_line)
        export_layout.addRow("", export_sc_layout)

        #import
        import_sc_find_def_layout = QtWidgets.QHBoxLayout()
        import_sc_find_def_layout.setSpacing(4)
        import_sc_find_def_layout.addWidget(self.import_sc_node_cb)
        import_sc_find_def_layout.addWidget(self.import_sc_node_refresh_btn)

        import_explorer_layout = QtWidgets.QHBoxLayout()
        import_explorer_layout.setSpacing(4)
        import_explorer_layout.addWidget(self.import_dir_path_le)
        import_explorer_layout.addWidget(self.import_dir_path_show_folder_btn)

        import_sc_layout = QtWidgets.QHBoxLayout()
        import_sc_layout.setSpacing(4)
        import_sc_layout.addStretch()
        import_sc_layout.addWidget(self.import_sc_btn)

        import_layout = QtWidgets.QFormLayout()
        import_layout.setSpacing(4)
        import_layout.addRow("Existing Clusters:", import_sc_find_def_layout)
        import_layout.addRow("Directory:", import_explorer_layout)
        import_layout.addRow(self.import_sc_h_line_01)
        import_layout.addRow("Name:", self.sc_import_name_le)
        import_layout.addRow("Creator:", self.sc_import_creator_le)
        import_layout.addRow("Created:", self.sc_created_import_date_le)
        import_layout.addRow("Platform:", self.sc_platform_le)
        import_layout.addRow(self.import_sc_h_line_02)
        import_layout.addRow("",import_sc_layout)


        close_layout = QtWidgets.QHBoxLayout()
        close_layout.setContentsMargins(0,0,11,0)
        close_layout.addStretch()
        close_layout.addWidget(self.close_btn)

        #groups
        export_grp = QtWidgets.QGroupBox("Export")
        export_grp.setLayout(export_layout)

        import_grp = QtWidgets.QGroupBox("Import")
        import_grp.setFixedHeight(215)
        import_grp.setLayout(import_layout)
        
        #main
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(export_grp)
        main_layout.addWidget(import_grp)
        main_layout.addLayout(close_layout)
        main_layout.addStretch()

    def create_connections(self):
        self.export_sc_node_cb.currentTextChanged.connect(self.export_cb_changed)
        self.export_sc_btn.clicked.connect(self.sc_do_export)
        self.export_sc_node_refresh_btn.clicked.connect(self.refresh_export_cb)
        self.import_sc_node_refresh_btn.clicked.connect(self.refresh_import_cb)
        self.export_dir_path_show_folder_btn.clicked.connect(self.select_export_dir)
        self.import_dir_path_show_folder_btn.clicked.connect(self.select_import_dir)
        self.import_sc_btn.clicked.connect(self.sc_do_import)
        self.close_btn.clicked.connect(self.close)
    
    # get the current projects directory to be the path the gui will open to initially
    def get_project_dir_path(self):
        return cmds.workspace(q=True, rootDirectory=True)
    
    def resolve_output_directory_path(self, dir_path):
        if "{project}/" in dir_path:
            dir_path = dir_path.replace("{project}/", self.get_project_dir_path())

        return dir_path
    
    # let the user select a export directory
    def select_export_dir(self):
        current_dir_path = self.export_dir_path_le.text()
        if not current_dir_path:
            current_dir_path = self.export_dir_path_le.placeholderText()
        current_dir_path = self.resolve_output_directory_path(current_dir_path)
        file_info = QtCore.QFileInfo(current_dir_path)
        if not file_info.exists():
            current_dir_path = self.get_project_dir_path()

        new_dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", current_dir_path)
        if new_dir_path:
            self.export_dir_path_le.setText(new_dir_path)

    # let the user select a file to import
    def select_import_dir(self):
        current_dir_path = self.export_dir_path_le.text()
        if not current_dir_path:
            current_dir_path = self.export_dir_path_le.placeholderText()
        current_dir_path = self.resolve_output_directory_path(current_dir_path)
        file_info = QtCore.QFileInfo(current_dir_path)
        if not file_info.exists():
            current_dir_path = self.get_project_dir_path()
        new_dir_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", current_dir_path,filter=('Json Files (*.json)'))

        if new_dir_path:
            self.import_dir_path_le.setText(new_dir_path[0])
            self.populate_data(new_dir_path[0])

    # query the user to overwrite the file
    def export_overwrite(self):
        overwrite = QtWidgets.QMessageBox.question(self, "Overwrite File?", "File Exists, Overwrite?")
        if overwrite == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False
        
    # get all skincluster deformers in the scene
    def get_scene_deformers(self):
        scene_sc = cmds.ls(type='skinCluster')
        if scene_sc:
            return scene_sc
        else:
            return False

    # get the users name using the os login credentials
    def get_user_data(self):
        self.userName = os.getlogin()
        return self.userName

    # set the skincluster line edit to reflect the combo box when changed
    def export_cb_changed(self):
        export_found_deformer = self.export_sc_node_cb.currentText()

        sc_export_name = self.sc_export_name_le.text()
        if not sc_export_name:
            self.sc_export_name_le.setPlaceholderText(export_found_deformer)
    
    # populate the gui with some data gathered from the users detail and scene skinclusters
    def set_initial_values(self):
        s_clusters = self.get_scene_deformers()
        user_details = self.get_user_data()

        if s_clusters:
            self.sc_export_name_le.setPlaceholderText(s_clusters[0])
            
            for sc in s_clusters:
                self.export_sc_node_cb.addItem(sc)
                self.import_sc_node_cb.addItem(sc)
        else:
            pass
        self.sc_export_creator_le.setPlaceholderText(user_details)

    # refresh the export combobox
    def refresh_export_cb(self):
        s_clusters = self.get_scene_deformers()
        cur_export_cb = self.export_sc_node_cb.currentText()
        self.export_sc_node_cb.clear()
        if s_clusters != False:
            for sc in s_clusters:
                self.export_sc_node_cb.addItem(sc)
        if cur_export_cb:
            try:
                if cur_export_cb in s_clusters:
                    index = self.export_sc_node_cb.findText(cur_export_cb, QtCore.Qt.MatchFixedString)
                    self.export_sc_node_cb.setCurrentIndex(index)
            except TypeError:
                pass
    # refresh the import combobox
    def refresh_import_cb(self):
        s_clusters = self.get_scene_deformers()
        cur_import_cb = self.import_sc_node_cb.currentText()
        self.import_sc_node_cb.clear()
        if s_clusters != False:
            for sc in s_clusters:
                self.import_sc_node_cb.addItem(sc)
        if cur_import_cb:
            try:
                if cur_import_cb in s_clusters:
                    index = self.import_sc_node_cb.findText(cur_import_cb, QtCore.Qt.MatchFixedString)
                    self.import_sc_node_cb.setCurrentIndex(index)
            except TypeError:
                pass
    # export the skincluster and user data to a json file
    def sc_do_export(self):
        result = False
        self.refresh_export_cb()
        export_cb = self.export_sc_node_cb.currentText()
        export_userName = self.sc_export_creator_le.text()
        force_replace = self.export_sc_cb_force_cb.isChecked()
        
        # perform checks 
        if not export_cb:
            cmds.warning("No Skin Clusters Found In Scene For Export")
            return
        export_dir_path = self.export_dir_path_le.text()
        
        if not export_dir_path:
            export_dir_path = self.export_dir_path_le.placeholderText()
        export_dir_path = self.resolve_output_directory_path(export_dir_path)

        if not export_userName:
            export_userName = self.sc_export_creator_le.placeholderText()

        folder_info = QtCore.QFileInfo(export_dir_path)

        if not folder_info.exists():
            cmds.warning("Directory Not Found")
        else:
            file_name = self.sc_export_name_le.text()
            if not file_name:
                file_name = self.sc_export_name_le.placeholderText()
            export_file = '{0}/{1}.json'.format(export_dir_path, file_name)
        file_info = QtCore.QFileInfo(export_file)

        if file_info.exists():
            if force_replace:
                result = True
            else:
                result = self.export_overwrite()
        else:
            result = True
        # write to json
        if result:
            meta_data = UserData()
            meta_data.get_user_data(export_userName)
            deformer_data = DeformerData()
            deformer_data.get_mesh_data(export_cb)

            data_to_dump = {}
            data_to_dump["User Info"] = meta_data.to_json()
            data_to_dump["Deformer Info"] = deformer_data.to_json()
            with open(export_file,"w") as file_for_write:
                json.dump(data_to_dump, file_for_write)
    
    # when user selects file to import grab the data and populate the gui
    def populate_data(self, file_path):
    
        with open(file_path,"r") as file_for_read:
            data = json.load(file_for_read)
        SCImportExport.json_data = data
        sc_name = data["Deformer Info"]["cluster"]
        user_name = data["User Info"]["user"]
        file_create = data["User Info"]["created"]
        platform = data["User Info"]["platform"]
        self.sc_import_name_le.setText(sc_name)
        self.sc_import_creator_le.setText(user_name)
        self.sc_created_import_date_le.setText(file_create)
        self.sc_platform_le.setText(platform)

    # import the skincluster from a json file
    def sc_do_import(self):
        self.refresh_import_cb()
        import_cb = self.import_sc_node_cb.currentText()
        
        # perform checks
        if not import_cb:
            cmds.warning("No Skin Cluster Found In Scene To Import Data To")
            return

        import_dir_le = self.import_dir_path_le.text()
        if not import_dir_le:
            cmds.warning("No Import File Selected")
            return

        import_data = SCImportExport.json_data
        vtx_count = import_data["Deformer Info"]["vtx"]
        import_to_geo_name = cmds.listRelatives(cmds.skinCluster(import_cb, q=True, g=True),p=True, fullPath=True)[0]
        import_to_geo_vtx_count = cmds.polyEvaluate(import_to_geo_name, v=True)
        if len(vtx_count) != import_to_geo_vtx_count:
            cmds.warning("Skin Clusters Must Have Geo With The Same Vertex Count")

        json_influences = import_data["Deformer Info"]["inf"]
        json_inf_lst = []
        for f in json_influences:
            json_inf_lst.append(f["name"])
        found_influences = cmds.skinCluster(import_cb, query=True, influence=True)

        check_inf = self.equal_ignore_order(json_inf_lst,found_influences)
        if not check_inf:
            cmds.warning("Skin Clsuters Must Have Same Influence Joints")
            return
        
        for jnt in range(0, len(found_influences)):
            for vtx in range(0, len(vtx_count)):   
                get_val = json_influences[jnt][str(jnt)][vtx]
                cmds.skinPercent( import_cb, '{0}.vtx[{1}]'.format(import_to_geo_name,vtx), tv=[json_inf_lst[jnt], get_val])
    
    # check the import file has the same influences
    def equal_ignore_order(self, a, b):
        if len(a) != len(b):
            return False
        unmatched = list(b)
        
        for element in a:
            try:
                unmatched.remove(element)
            except ValueError:
                return False
        return not unmatched
        

if __name__ == "__main__":
    try:
        sc_import_export.close()
        sc_import_export.deleteLater()
    except:
        pass
    sc_import_export = SCImportExport()
    sc_import_export.show()
