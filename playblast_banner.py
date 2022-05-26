"""
+--------------------------------------------------
| Playblast Banner
+--------------------------------------------------
| Author: Jason Whyttes
| Date: 17/05/2022
+--------------------------------------------------
| Description: Creates a banner that the 
| animator can playblast with to show the
| animators name, shot name, and frame number.
+--------------------------------------------------
| Usage: 1) Input Animator name, default is user
| login name.
|		 2) Input shot name.
|		 3) Select camera from drop down.
|		 4) Click create.
|
| *Adjust the banner position with the 		  
|  adjustment buttons or with mayas translate/
|  rotate/scale tools.						  
+--------------------------------------------------
"""
import os
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

class PlayblastBanner(QtWidgets.QDialog):
	TITLE = "Playblast Banner Creator"
	dlg_instance = None

	@classmethod
	def show_dialog(cls):
		if not cls.dlg_instance:
			cls.dlg_instance = PlayblastBanner()
		
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
			
		super(PlayblastBanner, self).__init__(maya_main_window)

		self.setWindowTitle(PlayblastBanner.TITLE)
		self.setMinimumSize(400,300)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()
		self.get_scene_cameras()

	def create_widgets(self):
		self.animator_name_le = QtWidgets.QLineEdit()
		self.animator_name_le.setFixedWidth(250)
		self.animator_name_le.setPlaceholderText(self.get_animator_loging())
		self.animation_shot_le = QtWidgets.QLineEdit()
		self.animation_shot_le.setFixedWidth(250)
		self.animation_shot_le.setPlaceholderText("Shot Name")
		self.camera_select_cb = QtWidgets.QComboBox()
		self.camera_select_cb.setFixedWidth(220)
		self.camera_refresh_btn = QtWidgets.QPushButton(QtGui.QIcon(":refresh.png"), "")
		self.camera_refresh_btn.setFixedSize(26, 19)
		self.create_banner_btn = QtWidgets.QPushButton("Create")
		self.close_bnt = QtWidgets.QPushButton("Close")
		self.adjust_size_le = QtWidgets.QLineEdit("1")
		self.adjust_size_le.setFixedSize(40,20)
		self.adjust_width_le = QtWidgets.QLineEdit("1")
		self.adjust_width_le.setFixedSize(40,20)
		self.adjust_height_le = QtWidgets.QLineEdit("1")
		self.adjust_height_le.setFixedSize(40,20)
		self.select_node_btn = QtWidgets.QPushButton("Select Translator")
		self.separator_01 = QtWidgets.QFrame()
		self.separator_01.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.separator_01.setFrameShape(QtWidgets.QFrame.HLine)
		self.nudge_distance_up = QtWidgets.QPushButton(QtGui.QIcon(":moveUVUp.png"), "")
		self.nudge_distance_up.setFixedSize(13,9)
		self.nudge_distance_down = QtWidgets.QPushButton(QtGui.QIcon(":moveUVDown.png"), "")
		self.nudge_distance_down.setFixedSize(13,9)
		self.nudge_width_up = QtWidgets.QPushButton(QtGui.QIcon(":moveUVUp.png"), "")
		self.nudge_width_up.setFixedSize(13,9)
		self.nudge_width_down = QtWidgets.QPushButton(QtGui.QIcon(":moveUVDown.png"), "")
		self.nudge_width_down.setFixedSize(13,9)
		self.nudge_height_up = QtWidgets.QPushButton(QtGui.QIcon(":moveUVUp.png"), "")
		self.nudge_height_up.setFixedSize(13,9)
		self.nudge_height_down = QtWidgets.QPushButton(QtGui.QIcon(":moveUVDown.png"), "")
		self.nudge_height_down.setFixedSize(13,9)

		#disable adjuster buttons until banner is created
		self.adjust_size_le.setEnabled(False)
		self.adjust_width_le.setEnabled(False)
		self.adjust_height_le.setEnabled(False)
		self.nudge_distance_up.setEnabled(False)
		self.nudge_distance_down.setEnabled(False)
		self.nudge_height_up.setEnabled(False)
		self.nudge_height_down.setEnabled(False)
		self.nudge_width_up.setEnabled(False)
		self.nudge_width_down.setEnabled(False)
		self.select_node_btn.setEnabled(False)

	def create_layouts(self):
		camera_select_layout = QtWidgets.QHBoxLayout()
		camera_select_layout.setSpacing(4)
		camera_select_layout.addWidget(self.camera_select_cb)
		camera_select_layout.addWidget(self.camera_refresh_btn)

		animation_details_layout = QtWidgets.QFormLayout()
		animation_details_layout.setSpacing(4)
		animation_details_layout.addRow("Animator Name:",self.animator_name_le)
		animation_details_layout.addRow("Shot Name:",self.animation_shot_le)
		animation_details_layout.addRow("Camera:", camera_select_layout)

		nudge_distance_layout = QtWidgets.QVBoxLayout()
		nudge_distance_layout.setSpacing(1)
		nudge_distance_layout.addWidget(self.nudge_distance_up)
		nudge_distance_layout.addWidget(self.nudge_distance_down)

		distance_layout = QtWidgets.QHBoxLayout()
		distance_layout.addWidget(self.adjust_size_le)
		distance_layout.addLayout(nudge_distance_layout)

		nudge_width_layout = QtWidgets.QVBoxLayout()
		nudge_width_layout.setSpacing(1)
		nudge_width_layout.addWidget(self.nudge_width_up)
		nudge_width_layout.addWidget(self.nudge_width_down)

		width_layout = QtWidgets.QHBoxLayout()
		width_layout.addWidget(self.adjust_width_le)
		width_layout.addLayout(nudge_width_layout)

		nudge_height_layout = QtWidgets.QVBoxLayout()
		nudge_height_layout.setSpacing(1)
		nudge_height_layout.addWidget(self.nudge_height_up)
		nudge_height_layout.addWidget(self.nudge_height_down)

		height_layout = QtWidgets.QHBoxLayout()
		height_layout.addWidget(self.adjust_height_le)
		height_layout.addLayout(nudge_height_layout)

		adjust_layout_form = QtWidgets.QFormLayout()
		adjust_layout_form.setSpacing(4)
		adjust_layout_form.addRow("Distance:",distance_layout)
		adjust_layout_form.addRow("Width:", width_layout)
		adjust_layout_form.addRow("Height:", height_layout)

		adjust_layout = QtWidgets.QHBoxLayout()
		adjust_layout.addLayout(adjust_layout_form)
		adjust_layout.addWidget(self.select_node_btn)

		close_layout = QtWidgets.QHBoxLayout()
		close_layout.addStretch()
		close_layout.addWidget(self.close_bnt)

		setup_grp = QtWidgets.QGroupBox("Setup")
		setup_grp.setFixedHeight(110)
		setup_grp.setLayout(animation_details_layout)

		adjustment_grp = QtWidgets.QGroupBox("Adjustments")
		adjustment_grp.setFixedHeight(100)
		adjustment_grp.setLayout(adjust_layout)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addWidget(setup_grp)
		main_layout.addWidget(self.create_banner_btn)
		main_layout.addWidget(self.separator_01)
		main_layout.addWidget(adjustment_grp)
		main_layout.addLayout(close_layout)
		main_layout.addStretch()


	def create_connections(self):
		self.camera_refresh_btn.clicked.connect(self.get_scene_cameras)
		self.close_bnt.clicked.connect(self.close)
		self.create_banner_btn.clicked.connect(self.execute)
		self.adjust_size_le.textChanged.connect(self.adjust_size)
		self.adjust_width_le.textChanged.connect(self.adjust_width)
		self.adjust_height_le.textChanged.connect(self.adjust_height)
		self.select_node_btn.clicked.connect(self.select_transform_node)
		self.nudge_distance_up.clicked.connect(self.set_nudge_val)
		self.nudge_distance_down.clicked.connect(self.set_nudge_val)
		self.nudge_width_up.clicked.connect(self.set_nudge_val)
		self.nudge_width_down.clicked.connect(self.set_nudge_val)
		self.nudge_height_up.clicked.connect(self.set_nudge_val)
		self.nudge_height_down.clicked.connect(self.set_nudge_val)

	def set_nudge_val(self):
		if self.sender() == self.nudge_distance_up:
			cur_val = float(self.adjust_size_le.text()) + 0.01
			self.adjust_size_le.setText(str(f'{cur_val:.2f}'))

		elif self.sender() == self.nudge_distance_down:
			cur_val = float(self.adjust_size_le.text()) - 0.01
			self.adjust_size_le.setText(str(f'{cur_val:.2f}'))

		elif self.sender() == self.nudge_width_up:
			cur_val = float(self.adjust_width_le.text()) + 0.01
			self.adjust_width_le.setText(str(f'{cur_val:.2f}'))

		elif self.sender() == self.nudge_width_down:
			cur_val = float(self.adjust_width_le.text()) - 0.01
			self.adjust_width_le.setText(str(f'{cur_val:.2f}'))

		elif self.sender() == self.nudge_height_up:
			cur_val = float(self.adjust_height_le.text()) + 0.01
			self.adjust_height_le.setText(str(f'{cur_val:.2f}'))

		else:
			cur_val = float(self.adjust_height_le.text()) - 0.01
			self.adjust_height_le.setText(str(f'{cur_val:.2f}'))


	def get_animator_loging(self):
		user_name = os.getlogin()
		return user_name

	def get_scene_cameras(self):
		self.camera_select_cb.clear()
		scene_cameras = cmds.listCameras()
		for cams in scene_cameras:
			self.camera_select_cb.addItem(cams)

	def select_transform_node(self):
		cmds.select(self.anim_types[1])
		cmds.setToolTo("Move")

	def adjust_size(self):
		try:
			val = float(self.adjust_size_le.text())
			cmds.setAttr("{0}.scaleX".format(self.anim_types[1]),val-.8)
			cmds.setAttr("{0}.scaleY".format(self.anim_types[1]),val-.8)
			cmds.setAttr("{0}.scaleZ".format(self.anim_types[1]),val-.8)
		except ValueError:
			self.adjust_size_le.setText(self.adjust_size_le.text()[:-1])
			return

	def adjust_height(self):
		try:
			val = float(self.adjust_height_le.text())
			cmds.setAttr("{0}.scaleY".format(self.anim_types[2]),val)
		except ValueError:
			self.adjust_height_le.setText(self.adjust_height_le.text()[:-1])
			return

	def adjust_width(self):
		try:
			val = float(self.adjust_width_le.text())
			cmds.setAttr("{0}.scaleX".format(self.anim_types[2]),val)
		except ValueError:
			self.adjust_width_le.setText(self.adjust_width_le.text()[:-1])
			return

	def execute(self):
		self.anim_types = self.set_up_text()
		self.attatch_to_cam(self.anim_types)
		self.adjust_size_le.setEnabled(True)
		self.adjust_width_le.setEnabled(True)
		self.adjust_height_le.setEnabled(True)
		self.nudge_distance_up.setEnabled(True)
		self.nudge_distance_down.setEnabled(True)
		self.nudge_height_up.setEnabled(True)
		self.nudge_height_down.setEnabled(True)
		self.nudge_width_up.setEnabled(True)
		self.nudge_width_down.setEnabled(True)
		self.select_node_btn.setEnabled(True)

	def set_up_text(self):
		user_name = self.animator_name_le.text()
		if not user_name:
			user_name = self.animator_name_le.placeholderText()
		shot_name = self.animation_shot_le.text()
		if not shot_name:
			shot_name = self.animation_shot_le.placeholderText()
		node_prefix = "{0}_anim_overlay".format(user_name)

		geo_grp_name = self.check_exists("{0}_type_grp".format(node_prefix),0)
		geo_offset_grp_name = self.check_exists("{0}_type_offset_grp".format(node_prefix),0)
		background_node_name = self.check_exists("{0}_type_background_mesh".format(node_prefix),0)
		frame_type_geo_name = self.check_exists("{0}_frame_type".format(node_prefix),0)
		animator_type_geo_name = self.check_exists("{0}_animator_type".format(node_prefix),0)
		shot_type_geo_name = self.check_exists("{0}_shot_type".format(node_prefix),0)
		type_shader_name = self.check_exists("{0}_type_shader".format(node_prefix),0)
		background_shader_name = self.check_exists("{0}_type_background_shader".format(node_prefix),0)
		anchor_loc_frames_name = self.check_exists("{0}_type_frames_anchor_loc".format(node_prefix),0)
		anchor_loc_animator_name = self.check_exists("{0}_type_animator_anchor_loc".format(node_prefix),0)
		anchor_loc_shot_name = self.check_exists("{0}_type_shot_achnor_loc".format(node_prefix),0)

		frame_type_geo = self.create_type_geo(frame_type_geo_name)
		animator_type_geo = self.create_type_geo(animator_type_geo_name)
		shot_type_geo = self.create_type_geo(shot_type_geo_name)

		anchor_loc_frames = cmds.spaceLocator(n=anchor_loc_frames_name)
		anchor_loc_animator = cmds.spaceLocator(n=anchor_loc_animator_name)
		anchor_loc_shot = cmds.spaceLocator(n=anchor_loc_shot_name)

		background_geo = cmds.polyPlane(n=background_node_name,w=10,h=1.5,sx=1,sy=1,ax=(0,0,1),cuv=2,ch=0)
		type_grp = cmds.group(em=1,n=geo_grp_name)
		offset_grp = cmds.group(em=1,n=geo_offset_grp_name)
		cmds.parent(type_grp,offset_grp)
		cmds.parent(background_geo,type_grp)
		cmds.parent(frame_type_geo[1],type_grp)
		cmds.parent(animator_type_geo[1],type_grp)
		cmds.parent(shot_type_geo[1],type_grp)
		cmds.parent(anchor_loc_frames[0],type_grp)
		cmds.parent(anchor_loc_animator[0],type_grp)
		cmds.parent(anchor_loc_shot[0],type_grp)

		cmds.setAttr('{0}.visibility'.format(anchor_loc_frames[0]),0)
		cmds.setAttr('{0}.visibility'.format(anchor_loc_animator[0]),0)
		cmds.setAttr('{0}.visibility'.format(anchor_loc_shot[0]),0)
		cmds.setAttr("{0}.generator".format(frame_type_geo[0]),1)
		cmds.setAttr("{0}.length".format(frame_type_geo[0]),4)
		cmds.setAttr('{0}.textInput'.format(animator_type_geo[0]),self.string_to_hex(user_name),type='string')
		cmds.setAttr('{0}.textInput'.format(shot_type_geo[0]),self.string_to_hex(shot_name),type='string')

		type_shader_node = cmds.shadingNode('lambert',asShader=True,n=type_shader_name)
		type_background_shader_node = cmds.shadingNode('lambert',asShader=True,n=background_shader_name)
		type_shader_set = cmds.sets(type_shader_name,renderable=True,noSurfaceShader=True,empty=True)
		type_background_shader_set = cmds.sets(background_shader_name,renderable=True,noSurfaceShader=True,empty=True)

		cmds.connectAttr("{0}.outColor".format(type_shader_node),"{0}.surfaceShader".format(type_shader_set),f=1)
		cmds.connectAttr("{0}.outColor".format(type_background_shader_node),"{0}.surfaceShader".format(type_background_shader_set),f=1)

		cmds.setAttr("{0}.color".format(type_shader_node),0.85,0.85,0.85,type="double3")
		cmds.setAttr("{0}.color".format(type_background_shader_node),0.1,0.1,0.1,type="double3")
		cmds.setAttr("{0}.transparency".format(type_background_shader_node),0.55,0.55,0.55,type="double3")

		cmds.sets(frame_type_geo[1],e=1,forceElement=(type_shader_set))
		cmds.sets(animator_type_geo[1],e=1,forceElement=(type_shader_set))
		cmds.sets(shot_type_geo[1],e=1,forceElement=(type_shader_set))
		cmds.sets(background_geo,e=1,forceElement=(type_background_shader_set))

		cmds.xform(shot_type_geo[1], cpc=True)

		x_center = cmds.xform(shot_type_geo[1],sp=True,q=1)[0]
		cmds.setAttr('{0}.translateX'.format(shot_type_geo[1]),x_center*-1)
		cmds.setAttr('{0}.translateX'.format(animator_type_geo[1]),-4.8)
		cmds.setAttr('{0}.translateX'.format(frame_type_geo[1]),3.2)
		cmds.setAttr('{0}.translateY'.format(animator_type_geo[1]),-.6)
		cmds.setAttr('{0}.translateY'.format(frame_type_geo[1]),-.6)

		cmds.setAttr("{0}.overrideEnabled".format(type_grp),1)
		cmds.setAttr("{0}.overrideDisplayType".format(type_grp),2)

		popc_frames = cmds.pointOnPolyConstraint(background_geo,anchor_loc_frames,mo=0,o=(0,0,0))
		popc_animator = cmds.pointOnPolyConstraint(background_geo,anchor_loc_animator,mo=0,o=(0,0,0))
		popc_shot = cmds.pointOnPolyConstraint(background_geo,anchor_loc_shot,mo=0,o=(0,0,0))

		cmds.setAttr('{0}.{1}U0'.format(popc_frames[0],background_geo[0]),1)
		cmds.setAttr('{0}.{1}U0'.format(popc_shot[0],background_geo[0]),0.5)
		cmds.setAttr('{0}.{1}V0'.format(popc_shot[0],background_geo[0]),0.15)

		frames_pConst = cmds.pointConstraint(anchor_loc_frames[0],frame_type_geo[1],mo=1)
		animator_pConst = cmds.pointConstraint(anchor_loc_animator[0],animator_type_geo[1],mo=1)
		shot_pConst = cmds.pointConstraint(anchor_loc_shot[0],shot_type_geo[1],mo=1)

		return geo_offset_grp_name, geo_grp_name, background_node_name

	def check_exists(self, nodeName, start):
		n = 1
		if start == 0:
			nodeNameOut = nodeName	
		else:
			nodeNameOut = nodeName + '_{:02d}'.format(n) 
		if cmds.objExists(nodeNameOut): 
			nodeNameOut = nodeName + '_{:02d}'.format(n) 
			while True:						
				if cmds.objExists(nodeNameOut):										
					nodeNameOut = nodeName + '_{:02d}'.format(n)    
					n += 1 
				else:
					break
		return nodeNameOut

	def create_type_geo(self, nodeNames=None):
		time_node = cmds.ls(type="time")[0]

		geo_node_name = self.check_exists("{0}_mesh".format(nodeNames),2)
		type_node_name = self.check_exists("{0}_type".format(nodeNames),2)
		shell_node_name = self.check_exists("{0}_shell".format(nodeNames),2)

		type_geo_node = cmds.createNode("mesh")
		type_node = cmds.createNode("type",n=type_node_name)
		
		shell_node = cmds.createNode("shellDeformer",n=shell_node_name)
		type_geo_node = cmds.rename(cmds.listRelatives(type_geo_node,p=True, fullPath=False)[0],"{0}".format(geo_node_name))
		type_geo_shape_node = cmds.listRelatives(type_geo_node,shapes=True)[0]

		cmds.connectAttr("{0}.outTime".format(time_node),"{0}.time".format(type_node))
		cmds.connectAttr("{0}.outTime".format(time_node),"{0}.time".format(shell_node))
		cmds.connectAttr("{0}.outputMesh".format(type_node),"{0}.input[0].inputGeometry".format(shell_node))
		cmds.connectAttr("{0}.outputGeometry[0]".format(shell_node),"{0}.inMesh".format(type_geo_shape_node))
		cmds.setAttr('{0}.translateZ'.format(type_geo_node),0.1)
		cmds.setAttr('{0}.fontSize'.format(type_node),1)

		return type_node, type_geo_node, type_geo_shape_node

	def string_to_hex(self, s):
		hex_space = ""
		for i in s:
			v = str(i.encode("utf-8").hex())
			hex_space = hex_space + v + " "
		return hex_space[0:len(hex_space)-1]

	def attatch_to_cam(self, anim_banner):

		cam = self.camera_select_cb.currentText()

		t = cmds.xform(cam,q=1,ws=1,t=1)
		r = cmds.xform(cam,q=1,ws=1,ro=1)
		
		cmds.xform(anim_banner[0],ro=(r))
		cmds.xform(anim_banner[0],t=(t))
		cmds.xform(anim_banner[1],translation=(0,0,-5))
		cmds.xform(anim_banner[1],scale=(0.2,0.2,0.2))
		cmds.parentConstraint(cam,anim_banner[0],mo=1)

		cmds.setAttr('{0}.tx'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.ty'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.tz'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.rx'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.ry'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.rz'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.sx'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.sy'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)
		cmds.setAttr('{0}.sz'.format(anim_banner[0]),lock=True, keyable=False,channelBox=False)

if __name__ == "__main__":
	try:
		playblast_banner.close()
		playblast_banner.deleteLater()
	except:
		pass
	playblast_banner = PlayblastBanner()
	playblast_banner.show()
