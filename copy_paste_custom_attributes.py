# Copy Attributes
# Creation Date: 06/07/2021
# Author: Jason Whyttes
# Copies attributes from one control to another with built in word search/replace

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class CopyAttributesOver(QtWidgets.QDialog):

	dlg_instance = None
	left_list_node = ''
	right_list_node = ''
	
	@classmethod
	def show_dialog(cls):
		if not cls.dlg_instance:
			cls.dlg_instance = CopyAttributesOver()
		
		if cls.dlg_instance.isHidden():
			cls.dlg_instance.show()
		else:
			cls.dlg_instance.raise_()
			cls.dlg_instance.activateWindow()

	def __init__(self, parent=maya_main_window()):
		super(CopyAttributesOver, self).__init__(parent)

		self.left_list_attr = ''
		self.right_list_attr = ''
		self.setWindowTitle("Copy Attributes (left to right)")
		self.setMinimumSize(520,310)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		self.attributes_left_tsl = QtWidgets.QListWidget()
		self.attributes_left_tsl.resize(260,244)
		self.attributes_right_tsl = QtWidgets.QListWidget()
		self.attributes_right_tsl.resize(260,244)

		self.attributes_direction = QtWidgets.QLabel("  >>  ")
		self.attributes_direction.setStyleSheet(
            "QLabel {"
            "font-size: 13pt;"
            "font-weight: bold;"
            "}"
            );

		self.select_left_node_btn = QtWidgets.QPushButton("LOAD LEFT")
		self.select_left_node_btn.setStyleSheet(
            "QPushButton {"
            "font-size: 12pt;"
            "}"
            );

		self.select_right_node_btn = QtWidgets.QPushButton("LOAD RIGHT")
		self.select_right_node_btn.setStyleSheet(
            "QPushButton {"
            "font-size: 12pt;"
            "}"
            );

		self.run_button = QtWidgets.QPushButton("RUN")
		self.run_button.setStyleSheet(
            "QPushButton {"
            "font-size: 12pt;"
            "font-weight: bold;"
            "color: #d9d9d9;"
            "border-radius: 2px;"
            "padding: 0.2em 0.2em 0.3em 0.2em;"
            "border: 1px solid rgb(100, 100, 100);"
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #2b6e2f, stop:0.1 #3fbf3f, stop:1  #2ea32e);"
            "}"
            "QPushButton:hover {"
    		"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #2b6e2f, stop:0.1 #3fbf3f, stop:1  #44d444);"
			"}"
            );

		self.close_button = QtWidgets.QPushButton("CLOSE")
		self.close_button.setStyleSheet(
            "QPushButton {"
            "font-size: 12pt;"
            "font-weight: bold;"
            "color: #d9d9d9;"
            "border-radius: 2px;"
            "padding: 0.2em 0.2em 0.3em 0.2em;"
            "border: 1px solid rgb(100, 100, 100);"
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #6e2c2b, stop:0.1 #bf3f3f, stop:1  #a32e2e);"
            "}"
            "QPushButton:hover {"
    		"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #6e2c2b, stop:0.1 #bf3f3f, stop:1  #d44444);"
			"}"
            );
		self.select_left_node_btn.setSizePolicy(
    									QtWidgets.QSizePolicy.Expanding,
    									QtWidgets.QSizePolicy.Preferred)
		self.select_right_node_btn.setSizePolicy(
    									QtWidgets.QSizePolicy.Expanding,
    									QtWidgets.QSizePolicy.Preferred)
		self.run_button.setSizePolicy(
    									QtWidgets.QSizePolicy.Preferred,
    									QtWidgets.QSizePolicy.Preferred)
		self.close_button.setSizePolicy(
    									QtWidgets.QSizePolicy.Preferred,
    									QtWidgets.QSizePolicy.Preferred)

		self.search_lb = QtWidgets.QLabel("Search:	")
		self.replace_lb = QtWidgets.QLabel("Replace: ")
		self.search_str_le = QtWidgets.QLineEdit()
		self.replace_str_le = QtWidgets.QLineEdit()

	def create_layouts(self):
		scroll_list_layout = QtWidgets.QHBoxLayout()
		scroll_list_layout.addWidget(self.attributes_left_tsl)
		scroll_list_layout.addWidget(self.attributes_direction)
		scroll_list_layout.addWidget(self.attributes_right_tsl)

		search_replace_lb_layout = QtWidgets.QVBoxLayout()
		search_replace_lb_layout.addWidget(self.search_lb)
		search_replace_lb_layout.addWidget(self.replace_lb)

		search_replace_bt_layout = QtWidgets.QVBoxLayout()
		search_replace_bt_layout.addWidget(self.search_str_le)
		search_replace_bt_layout.addWidget(self.replace_str_le)

		select_node_btn_layout = QtWidgets.QHBoxLayout()
		select_node_btn_layout.addWidget(self.select_left_node_btn)
		select_node_btn_layout.addLayout(search_replace_lb_layout)
		select_node_btn_layout.addLayout(search_replace_bt_layout)
		select_node_btn_layout.addWidget(self.select_right_node_btn)

		run_layout = QtWidgets.QHBoxLayout()
		run_layout.addWidget(self.run_button)
		run_layout.addWidget(self.close_button)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addLayout(scroll_list_layout)
		main_layout.addLayout(select_node_btn_layout)
		main_layout.addLayout(run_layout)
		main_layout.setContentsMargins(2,2,2,2)
		main_layout.setSpacing(2)

	def create_connections(self):
		self.select_left_node_btn.clicked.connect(lambda: self.add_custom_attrs(self.select_left_node_btn))
		self.select_right_node_btn.clicked.connect(lambda: self.add_custom_attrs(self.select_right_node_btn))
		self.attributes_left_tsl.itemClicked.connect(self.itemActivated_event_left)
		self.attributes_right_tsl.itemClicked.connect(self.itemActivated_event_right)

		self.run_button.clicked.connect(self.move_attr)
		self.close_button.clicked.connect(self.close)

	def itemActivated_event_left(self,item):
		self.left_list_attr = item.text()

	def itemActivated_event_right(self,item):
		self.attributes_right_tsl.clearSelection()

	def add_custom_attrs(self, button):
		if button.text() == "LOAD LEFT":
			try:
				sel = cmds.ls(sl=True)[0]
				self.left_list_node = sel
				if self.right_list_node == sel:
					self.attributes_right_tsl.clear()
				self.attributes_left_tsl.clear()
				try:
					custom_attrs = cmds.listAttr(sel, userDefined=True)
					self.attributes_left_tsl.addItem(self.left_list_node)
					try:
						for items in custom_attrs:
							self.attributes_left_tsl.addItem('     {}'.format(items))
					except:
						pass
				except IndexError:
					pass
			except IndexError:
				pass
		elif button.text() == "LOAD RIGHT":
			try:
				sel = cmds.ls(sl=True)[0]
				self.right_list_node = sel
				if self.left_list_node == sel:
					self.attributes_left_tsl.clear()

				self.attributes_right_tsl.clear()
				try:
					custom_attrs = cmds.listAttr(sel, userDefined=True)
					self.attributes_right_tsl.addItem(self.right_list_node)
					try:
						for items in custom_attrs:
							self.attributes_right_tsl.addItem('     {}'.format(items))
					except:
						pass
				except  IndexError:
					pass
			except IndexError:
				pass
		else:
			pass

	def move_attr(self):
		left_check = self.attributes_left_tsl.count()
		right_check = self.attributes_right_tsl.count()
		search_str = self.search_str_le.text()
		replace_str = self.replace_str_le.text()

		if left_check != 0 and right_check != 0:
			left_attrs = []
			right_attrs = []
			toMove = []

			for i in range(1, left_check ):
				left_attrs.append(self.attributes_left_tsl.item(i).text())

			for i in range(1, right_check ):
				right_attrs.append(self.attributes_right_tsl.item(i).text())

			for p in left_attrs:
				if p.replace(search_str,replace_str) not in right_attrs:
					toMove.append(p)

			for i in toMove:
				param = i.replace(' ','')

				long_name_p = None
				nice_name_p = None
				keyable_p = None
				channelBox_p = None
				hidden_p = None
				data_type_p = None
				enumName_p = None
				min_p = None
				max_p = None
				default_p = None

				long_name_p = cmds.attributeQuery(param, node = self.left_list_node,ln=1)
				nice_name_p = cmds.attributeQuery(param, node = self.left_list_node,nn=1)
				keyable_p = cmds.getAttr('{}.{}'.format(self.left_list_node,param),k=1)
				channelBox_p = cmds.getAttr('{}.{}'.format(self.left_list_node,param),cb=1)
				hidden_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,h=1)
				data_type_p = cmds.getAttr('{}.{}'.format(self.left_list_node,param),typ=1)
				
				if data_type_p == "long":
					min_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,min=1)
					max_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,max=1)
					default_p =cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,dv=1)

				if data_type_p == "double":
					min_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,min=1)
					max_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,max=1)
					default_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,dv=1)

				if data_type_p == "enum":
					enumName_p = cmds.addAttr('{}.{}'.format(self.left_list_node,param),q=1,enumName=1)


				param_blueprint_int = { 'longName':long_name_p,
										'niceName': nice_name_p,
										'attributeType': 'double',
										'minValue': min_p,
										'maxValue': max_p,
										'defaultValue': default_p
										}

				param_blueprint_float = { 'longName':long_name_p,
										  'niceName': nice_name_p,
										  'attributeType': "float",
										  'minValue': min_p,
										  'maxValue': max_p,
										  'defaultValue': default_p
										  }

				param_blueprint_enum = {'longName':long_name_p,
										'niceName': nice_name_p,
										'attributeType': 'enum',
										'enumName': enumName_p}

				param_blueprint_boolean = {'longName':long_name_p,
										   'niceName': nice_name_p,
										   'attributeType': 'bool'}

				if data_type_p == 'double':
					has_min = False
					has_max = False
					if param_blueprint_int['minValue'] != None:
						has_min = True
					if param_blueprint_int['maxValue'] != None:
						has_max = True

					if has_min and has_max:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_int['attributeType'],
							longName = param_blueprint_int['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_int['niceName'].replace(search_str,replace_str),
							minValue=param_blueprint_int['minValue'],
							maxValue=param_blueprint_int['maxValue'],
							defaultValue=param_blueprint_int['defaultValue'])

					elif has_min == False and has_max:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_int['attributeType'],
							longName = param_blueprint_int['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_int['niceName'].replace(search_str,replace_str),
							maxValue=param_blueprint_int['maxValue'],
							defaultValue=param_blueprint_int['defaultValue'])

					elif has_min and has_max == False:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_int['attributeType'],
							longName = param_blueprint_int['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_int['niceName'].replace(search_str,replace_str),
							minValue=param_blueprint_int['minValue'],
							defaultValue=param_blueprint_int['defaultValue'])

					else:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_int['attributeType'],
							longName = param_blueprint_int['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_int['niceName'].replace(search_str,replace_str),
							defaultValue=param_blueprint_int['defaultValue'])

				elif data_type_p == 'float':
					has_min = False
					has_max = False
					if param_blueprint_float['minValue'] != None:
						has_min = True
					if param_blueprint_float['maxValue'] != None:
						has_max = True

					if has_min and has_max:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_float['attributeType'],
							longName = param_blueprint_float['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_float['niceName'].replace(search_str,replace_str),
							minValue=param_blueprint_float['minValue'],
							maxValue=param_blueprint_float['maxValue'],
							defaultValue=param_blueprint_float['defaultValue'])

					elif has_min == False and has_max:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_float['attributeType'],
							longName = param_blueprint_float['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_float['niceName'].replace(search_str,replace_str),
							maxValue=param_blueprint_float['maxValue'],
							defaultValue=param_blueprint_float['defaultValue'])

					elif has_min and has_max == False:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_float['attributeType'],
							longName = param_blueprint_float['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_float['niceName'].replace(search_str,replace_str),
							minValue=param_blueprint_float['minValue'],
							defaultValue=param_blueprint_float['defaultValue'])

					else:
						cmds.addAttr(self.right_list_node, 
							attributeType = param_blueprint_float['attributeType'],
							longName = param_blueprint_float['longName'].replace(search_str,replace_str),
							niceName=param_blueprint_float['niceName'].replace(search_str,replace_str),
							defaultValue=param_blueprint_float['defaultValue'])


				elif data_type_p == 'enum':
					cmds.addAttr(self.right_list_node,
						attributeType = param_blueprint_enum['attributeType'],
						longName = param_blueprint_enum['longName'].replace(search_str,replace_str),
						niceName=param_blueprint_enum['niceName'].replace(search_str,replace_str),
						enumName=param_blueprint_enum['enumName'])

				elif data_type_p == 'bool':
					cmds.addAttr(self.right_list_node,
						attributeType = param_blueprint_boolean['attributeType'],
						longName = param_blueprint_enum['longName'].replace(search_str,replace_str),
						niceName=param_blueprint_enum['niceName'].replace(search_str,replace_str))
					
				else:
					pass
				cmds.setAttr('{}.{}'.format(self.right_list_node,param.replace(search_str,replace_str)),k=keyable_p,cb=channelBox_p)


if __name__ == "__main__":
	try:
		copy_attributes_over.close()
		copy_attributes_over.deleteLater()
	except:
		pass
	copy_attributes_over = CopyAttributesOver()
	copy_attributes_over.show()
