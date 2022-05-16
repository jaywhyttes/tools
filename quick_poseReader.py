__VERSION__ = "1.01"
#1.01 - updated to work in maya 2022.0
"""
+--------------------------------+
|      POSE READER CREATION      |
|   JASON WHYTTES - 27/09/2021   |
+--------------------------------+
|          DESCRIPTION           |
| Create three locators and      |
| calculate the angle between    |
| using a cone shape.  			 |
+--------------------------------+
|            USE CASE            |
+--------------------------------+
| Find angle between shoulder    |
| and head to trigger a          |
| corrective blend shape.        |
+--------------------------------+
|           DIRECTIONS           |
+--------------------------------+
| Enter a name for the pose      |
| reader and click 'run'.        |
+~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ +
| *Optional* Click on 1 to 3 DAG |
| nodes to create the base, pose,|
| and target locators at those   |
| positions respectively.        |
+--------------------------------+
"""

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

def connect_nodes(output_node,output_con,input_node,input_con):
	cmds.connectAttr('{0}.{1}'.format(output_node,output_con),'{0}.{1}'.format(input_node,input_con),f=1)

def point_const(driver,driven):
	const = cmds.pointConstraint(driver,driven,mo=0)
	cmds.delete(const)

def check_exists(nodeName, start):
	n = 1
	if start == 0:
		nodeNameOut = nodeName	
	else:
		nodeNameOut = nodeName + '_{:02d}'.format(n) 
	if cmds.objExists(nodeNameOut): 
		nodeNameOut = nodeName + '_{:02d}'.format(n) 			#adds 01 to the end of the input
		while True:												#while the name exists in Maya	
			if cmds.objExists(nodeNameOut):										
				nodeNameOut = nodeName + '_{:02d}'.format(n)    #apply the same rule
				n += 1                                          #increment the value
			else:
				break
	return nodeNameOut

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class PoseReaderCreation(QtWidgets.QDialog):

	dlg_instance = None

	@classmethod
	def show_dialog(cls):
		if not cls.dlg_instance:
			cls.dlg_instance = PoseReaderCreation()
		
		if cls.dlg_instance.isHidden():
			cls.dlg_instance.show()
		else:
			cls.dlg_instance.raise_()
			cls.dlg_instance.activateWindow()

	def __init__(self, parent=maya_main_window()):
		super(PoseReaderCreation, self).__init__(parent)

		self.setWindowTitle("Make Pose Reader")
		self.setMinimumSize(250,20)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		self.pose_reader_name_le = QtWidgets.QLineEdit()
		self.pose_reader_name_le.setPlaceholderText('Enter Pose Reader Name')

		self.pose_reader_run_pb = QtWidgets.QPushButton('RUN')

	def create_layouts(self):
		pose_reader_name_layout = QtWidgets.QHBoxLayout()
		pose_reader_name_layout.addWidget(self.pose_reader_name_le)
		pose_reader_name_layout.addWidget(self.pose_reader_run_pb)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addLayout(pose_reader_name_layout)

		main_layout.setContentsMargins(2,2,2,2)
		main_layout.setSpacing(2)

	def create_connections(self):
		self.pose_reader_run_pb.clicked.connect(self.create_pose_reader)

	def create_pose_reader(self,name=''):
		cmds.undoInfo(ock=1)

		"""
		node selection is not working currently
		so lets remove selected nodes first for now until its fixed
		"""
		
		#check how many nodes are currently selected
		nodes_selected = False
		cmds.select(cl=1)
		sel = cmds.ls(sl=True,dag=True,type='transform')


		if len(sel) > 0 and len(sel) < 4:
			nodes_selected = True

		#get a prefix entered by the user
		pose_reader_name_prefix = self.pose_reader_name_le.text()
		if len(pose_reader_name_prefix) != 0:
			pose_reader_name_prefix = '{0}_'.format(pose_reader_name_prefix)
		else:
			pass
		
		#create unique names for our nodes
		pose_reader_group_name = check_exists('{0}pose_reader_group'.format(pose_reader_name_prefix),0)
		base_loc_name = check_exists('{0}pose_reader_base_loc'.format(pose_reader_name_prefix),0)
		pose_loc_name = check_exists('{0}pose_reader_pose_loc'.format(pose_reader_name_prefix),0)
		target_loc_name = check_exists('{0}pose_reader_target_loc'.format(pose_reader_name_prefix),0)
		base_loc_dcm_name = check_exists('{0}pose_reader_base_loc_dcm'.format(pose_reader_name_prefix),0)
		pose_loc_dcm_name = check_exists('{0}pose_reader_pose_loc_dcm'.format(pose_reader_name_prefix),0)
		target_loc_dcm_name = check_exists('{0}pose_reader_target_loc_dcm'.format(pose_reader_name_prefix),0)
		target_vec_pma_name = check_exists('{0}pose_reader_target_vec_pma'.format(pose_reader_name_prefix),0)
		pose_vec_pma_name = check_exists('{0}pose_reader_pose_vec_pma'.format(pose_reader_name_prefix),0)
		angle_outcome_rev_pma_name = check_exists('{0}pose_reader_angle_outcome_rev_pma'.format(pose_reader_name_prefix),0)
		angle_ab_name = check_exists('{0}pose_reader_angle_ab'.format(pose_reader_name_prefix),0)
		half_angle_mdl_name = check_exists('{0}pose_reader_full_cone_angle_mdl'.format(pose_reader_name_prefix),0)
		ratio_angle_md_name = check_exists('{0}pose_reader_ratio_angle_md'.format(pose_reader_name_prefix),0)
		angle_outcome_clamp_name = check_exists('{0}pose_reader_angle_outcome_clamp_clm'.format(pose_reader_name_prefix),0)
		pose_reader_pose_multMatrix_name = check_exists('{0}pose_reader_inv_pose_mult_matrix_mltMtx'.format(pose_reader_name_prefix),0)
		pose_reader_base_multMatrix_name = check_exists('{0}pose_reader_inv_base_mult_matrix_mltMtx'.format(pose_reader_name_prefix),0)
		pose_reader_target_multMatrix_name = check_exists('{0}pose_reader_inv_target_mult_matrix_mltMtx'.format(pose_reader_name_prefix),0)
		const_group_name = check_exists('{0}pose_reader_constraint_grp'.format(pose_reader_name_prefix),0)
		cone_name = check_exists('{0}pose_reader_angle_cone'.format(pose_reader_name_prefix),0)
		pose_rev_loc_inv_md_node_name = check_exists('{0}pose_reader_pose_rev_loc_inv_md'.format(pose_reader_name_prefix),0)
		pose_rev_loc_name = check_exists('{0}pose_reader_pose_rev_loc'.format(pose_reader_name_prefix),0)
		distance_between_node_name = check_exists('{0}pose_reader_distance_between'.format(pose_reader_name_prefix),0)
		tan_pma_node_name = check_exists('{0}pose_reader_tan_sub_right_angle_pma'.format(pose_reader_name_prefix),0)
		tan_angle_A_sine_premult_mdl_node_name = check_exists('{0}pose_reader_tan_angle_A_sine_premult_mdl'.format(pose_reader_name_prefix),0)
		tan_angle_B_sine_premult_mdl_node_name = check_exists('{0}pose_reader_tan_angle_B_sine_premult_mdl'.format(pose_reader_name_prefix),0)
		tan_angle_A_eulerToQuat_node_name = check_exists('{0}pose_reader_tan_angle_A_eulerToQuat'.format(pose_reader_name_prefix),0)
		tan_angle_B_eulerToQuat_node_name = check_exists('{0}pose_reader_tan_angle_B_eulerToQuat'.format(pose_reader_name_prefix),0)
		tan_sine_out_div_md_node_name = check_exists('{0}pose_reader_tan_sin_out_div_md'.format(pose_reader_name_prefix),0)
		tan_height_mul_mdl_node_name = check_exists('{0}pose_reader_tan_height_mul_mdl'.format(pose_reader_name_prefix),0)
		tan_angle_A_div_zero_counter_adl_node_name = check_exists('{0}pose_reader_angle_A_div_zero_counter_adl'.format(pose_reader_name_prefix),0)
		upper_cls_grp_name = check_exists('{0}pose_reader_upr_cls_grp'.format(pose_reader_name_prefix),0)
		cone_decomp_rev_node_name = check_exists('{0}pose_reader_cone_rev_dcm'.format(pose_reader_name_prefix),0)
		cone_cls_tweak_name = check_exists('{0}pose_reader_cone_tweak'.format(pose_reader_name_prefix),0)

		pose_reader_grp = cmds.group(em=1,n=pose_reader_group_name)
		upper_cls_grp_node = cmds.group(em=1,n=upper_cls_grp_name)
		const_group_node = cmds.group(em=1,n=const_group_name)
		base_loc =  cmds.spaceLocator(n=base_loc_name)[0]
		pose_loc =  cmds.spaceLocator(n=pose_loc_name)[0]
		target_loc = cmds.spaceLocator(n=target_loc_name)[0]
		pose_rev_loc = cmds.spaceLocator(n=pose_rev_loc_name)[0]
		cone_nb = cmds.cone(n=cone_name,p=(0,1,0),ax=(0,-1,0),ssw=0,esw=360,r=1,hr=2,d=1,ut=0,tol=0.01,s=8,nsp=1,ch=0)[0]

		#add custom attr to base loc
		angle_long_name = check_exists('{0}pose_reader_angle_param'.format(pose_reader_name_prefix),0)
		result_long_name = check_exists('{0}pose_reader_result_param'.format(pose_reader_name_prefix),0)
		cmds.addAttr(base_loc,longName=angle_long_name,niceName='Angle',attributeType='double',min=0.1,max=359.9,defaultValue=90)
		cmds.setAttr('{0}.{1}'.format(base_loc,angle_long_name),e=1,keyable=True)
		cmds.addAttr(target_loc,longName=result_long_name,niceName='Result',attributeType='double')
		cmds.setAttr('{0}.{1}'.format(target_loc,result_long_name),e=1,channelBox=True)
		
		#position locators
		if nodes_selected:
			if len(sel) == 1:
				base_pos_t = cmds.xform(sel[0],q=1,t=1,ws=1)
				cmds.xform(base_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(pose_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(target_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.makeIdentity(base_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(pose_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(target_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.xform(pose_loc,t=(0,5,0))
				cmds.xform(target_loc,t=(5,5,0))
			elif len(sel) == 2:
				base_pos_t = cmds.xform(sel[0],q=1,t=1,ws=1)
				pose_pos_t = cmds.xform(sel[1],q=1,t=1,ws=1)
				cmds.xform(base_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(pose_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(target_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.makeIdentity(base_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(pose_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(target_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				point_const(sel[1],pose_loc)
				cmds.xform(target_loc,t=(5,5,0))
			else:
				base_pos_t = cmds.xform(sel[0],q=1,t=1,ws=1)
				pose_pos_t = cmds.xform(sel[1],q=1,t=1,ws=1)
				target_pos_t = cmds.xform(sel[2],q=1,t=1,ws=1)
				cmds.xform(base_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(pose_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.xform(target_loc,t=(base_pos_t),ro=(0,0,0))
				cmds.makeIdentity(base_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(pose_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				cmds.makeIdentity(target_loc,apply=1,t=1,r=1,s=1,n=0,pn=1)
				point_const(sel[1],pose_loc)
				point_const(sel[2],target_loc)
			cmds.select(sel)
		else:
			cmds.xform(base_loc,t=(0,0,0),ro=(0,0,0))
			cmds.xform(pose_loc,t=(0,5,0),ro=(0,0,0))
			cmds.xform(target_loc,t=(5,5,0),ro=(0,0,0))
			cmds.select(cl=1)

		#create our nodes
		base_dcm_node = cmds.createNode('decomposeMatrix',n=base_loc_dcm_name)
		pose_dcm_node = cmds.createNode('decomposeMatrix',n=pose_loc_dcm_name)
		target_dcm_node = cmds.createNode('decomposeMatrix',n=target_loc_dcm_name)
		target_vec_pma_node = cmds.createNode('plusMinusAverage',n=target_vec_pma_name)
		pose_vec_pma_node = cmds.createNode('plusMinusAverage',n=pose_vec_pma_name)
		angle_outcome_rev_pma_node = cmds.createNode('plusMinusAverage',n=angle_outcome_rev_pma_name)
		angle_ab_node = cmds.createNode('angleBetween',n=angle_ab_name)
		half_angle_mdl_node = cmds.createNode('multDoubleLinear',n=half_angle_mdl_name)
		ratio_angle_md_node = cmds.createNode('multiplyDivide',n=ratio_angle_md_name)
		angle_outcome_clamp_node = cmds.createNode('clamp',n=angle_outcome_clamp_name)
		pose_inv_mult_mtx_node = cmds.createNode('multMatrix',n=pose_reader_pose_multMatrix_name)
		base_inv_mult_mtx_node = cmds.createNode('multMatrix',n=pose_reader_base_multMatrix_name)
		target_inv_mult_mtx_node = cmds.createNode('multMatrix',n=pose_reader_target_multMatrix_name)

		#set our node parameters
		cmds.setAttr('{0}.operation'.format(target_vec_pma_node),2)
		cmds.setAttr('{0}.operation'.format(pose_vec_pma_node),1)
		cmds.setAttr('{0}.operation'.format(angle_outcome_rev_pma_node),2)
		cmds.setAttr('{0}.operation'.format(ratio_angle_md_node),2)
		cmds.setAttr('{0}.input1D[0]'.format(angle_outcome_rev_pma_node),1)
		cmds.setAttr('{0}.minR'.format(angle_outcome_clamp_node),0)
		cmds.setAttr('{0}.maxR'.format(angle_outcome_clamp_node),1)
		cmds.setAttr('{0}.input2'.format(half_angle_mdl_node),0.5)

		#connect our nodes
		connect_nodes(pose_reader_grp,'inverseMatrix',pose_inv_mult_mtx_node,'matrixIn[0]')
		connect_nodes(pose_reader_grp,'inverseMatrix',target_inv_mult_mtx_node,'matrixIn[0]')
		connect_nodes(pose_reader_grp,'inverseMatrix',base_inv_mult_mtx_node,'matrixIn[0]')
		connect_nodes(pose_loc,'worldMatrix[0]',pose_inv_mult_mtx_node,'matrixIn[1]')
		connect_nodes(target_loc,'worldMatrix[0]',target_inv_mult_mtx_node,'matrixIn[1]')
		connect_nodes(base_loc,'worldMatrix[0]',base_inv_mult_mtx_node,'matrixIn[1]')
		connect_nodes(base_inv_mult_mtx_node,'matrixSum',base_dcm_node,'inputMatrix')
		connect_nodes(pose_inv_mult_mtx_node,'matrixSum',pose_dcm_node,'inputMatrix')
		connect_nodes(target_inv_mult_mtx_node,'matrixSum',target_dcm_node,'inputMatrix')
		connect_nodes(target_dcm_node,'outputTranslate',target_vec_pma_node,'input3D[0]')
		connect_nodes(base_dcm_node,'outputTranslate',target_vec_pma_node,'input3D[1]')
		connect_nodes(base_dcm_node,'outputTranslate',pose_vec_pma_node,'input3D[0]')
		connect_nodes(pose_dcm_node,'outputTranslate',pose_vec_pma_node,'input3D[1]')
		connect_nodes(base_loc,'{0}pose_reader_angle_param'.format(pose_reader_name_prefix),half_angle_mdl_node,'input1')
		connect_nodes(target_vec_pma_node,'output3D',angle_ab_node,'vector1')
		connect_nodes(pose_vec_pma_node,'output3D',angle_ab_node,'vector2')
		connect_nodes(angle_ab_node,'angle',ratio_angle_md_node,'input1X')
		connect_nodes(half_angle_mdl_node,'output',ratio_angle_md_node,'input2X')
		connect_nodes(ratio_angle_md_node,'outputX',angle_outcome_rev_pma_node,'input1D[1]')
		connect_nodes(angle_outcome_rev_pma_node,'output1D',angle_outcome_clamp_node,'inputR')
		connect_nodes(angle_outcome_clamp_node,'outputR',target_loc,result_long_name)

		cmds.parent(pose_loc,pose_reader_grp)
		cmds.parent(base_loc,pose_reader_grp)
		cmds.parent(target_loc,pose_reader_grp)

		distance_between_node = cmds.createNode('distanceBetween',n=distance_between_node_name)
		
		pose_rev_loc_inv_md_node = cmds.createNode('multiplyDivide',n=pose_rev_loc_inv_md_node_name)
		cmds.setAttr('{0}.input2X'.format(pose_rev_loc_inv_md_node),-1)
		cmds.setAttr('{0}.input2Y'.format(pose_rev_loc_inv_md_node),-1)
		cmds.setAttr('{0}.input2Z'.format(pose_rev_loc_inv_md_node),-1)

		#CreateCluster;
		upper_cone_cls = cmds.cluster('{0}.cv[0][0:8]'.format(cone_name),n='{0}_upr_cls'.format(cone_name))
		lower_cone_cls = cmds.cluster('{0}.cv[1][0:8]'.format(cone_name),n='{0}_lwr_cls'.format(cone_name))
		#cls_tweak_node = cmds.listConnections(cmds.listRelatives(cone_nb,type='shape'),type='tweak')
		#cmds.rename(cls_tweak_node,cone_cls_tweak_name)

		point_const(base_loc,upper_cone_cls)
		point_const(base_loc,lower_cone_cls)
		cmds.parent(upper_cone_cls[1],upper_cls_grp_node)
		cmds.parent(upper_cls_grp_node,pose_reader_grp)
		cmds.parent(pose_rev_loc,pose_reader_grp)
		cmds.parent(lower_cone_cls[1],base_loc)
		point_const(pose_loc,upper_cls_grp_node)

		#aim upper cluster at lower cluster
		aim_const = cmds.aimConstraint(lower_cone_cls,upper_cone_cls,mo=0,weight=1,aimVector=(0,-1,0),upVector=(0,0,1),worldUpType="none")

		#connect nodes
		connect_nodes(pose_loc,'translate',pose_rev_loc_inv_md_node,'input1')
		connect_nodes(pose_rev_loc_inv_md_node,'output',pose_rev_loc,'translate')
		connect_nodes(pose_dcm_node,'outputTranslate',distance_between_node,'point1')
		connect_nodes(base_dcm_node,'outputTranslate',distance_between_node,'point2')
		connect_nodes(distance_between_node,'distance',upper_cone_cls[1],'scaleX')
		connect_nodes(distance_between_node,'distance',upper_cone_cls[1],'scaleY')
		connect_nodes(distance_between_node,'distance',upper_cone_cls[1],'scaleZ')

		con_vis_long_name = '{0}pose_reader_cone_vis_param'.format(pose_reader_name_prefix)
		cmds.addAttr(base_loc,longName=con_vis_long_name,niceName='Cone Visibility',attributeType='long',min=0,max=1,defaultValue=1)
		cmds.setAttr('{0}.{1}'.format(base_loc,con_vis_long_name),e=1,keyable=True)
		connect_nodes(base_loc,con_vis_long_name,cone_nb,'visibility')
		cmds.setAttr('{0}.template'.format(cone_nb),1)
		cmds.parent(cone_nb,pose_reader_grp)

		#setup sdk
		upr_cls_point_const = cmds.pointConstraint(pose_loc,pose_rev_loc,upper_cls_grp_node)[0]
		cmds.setAttr('{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix),179.99)
		cmds.setAttr('{0}.{1}W0'.format(upr_cls_point_const,pose_loc),1)
		cmds.setAttr('{0}.{1}W1'.format(upr_cls_point_const,pose_rev_loc),0)
		cmds.setDrivenKeyframe('{0}.{1}W0'.format(upr_cls_point_const,pose_loc), cd='{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix))
		cmds.setDrivenKeyframe('{0}.{1}W1'.format(upr_cls_point_const,pose_rev_loc), cd='{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix))
		cmds.setAttr('{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix),180.00)
		cmds.setAttr('{0}.{1}W0'.format(upr_cls_point_const,pose_loc),0)
		cmds.setAttr('{0}.{1}W1'.format(upr_cls_point_const,pose_rev_loc),1)
		cmds.setDrivenKeyframe('{0}.{1}W0'.format(upr_cls_point_const,pose_loc), cd='{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix))
		cmds.setDrivenKeyframe('{0}.{1}W1'.format(upr_cls_point_const,pose_rev_loc), cd='{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix))
		cmds.setAttr('{0}.{1}pose_reader_angle_param'.format(base_loc,pose_reader_name_prefix),90)

		#create our tan nodes
		tan_pma_node = cmds.createNode('plusMinusAverage',n=tan_pma_node_name)
		tan_angle_A_sine_premult_mdl_node = cmds.createNode('multDoubleLinear',n=tan_angle_A_sine_premult_mdl_node_name)
		tan_angle_B_sine_premult_mdl_node = cmds.createNode('multDoubleLinear',n=tan_angle_B_sine_premult_mdl_node_name)
		tan_angle_A_eulerToQuat_node = cmds.createNode('eulerToQuat',n=tan_angle_A_eulerToQuat_node_name)
		tan_angle_B_eulerToQuat_node = cmds.createNode('eulerToQuat',n=tan_angle_B_eulerToQuat_node_name)
		tan_sine_out_div_md_node = cmds.createNode('multiplyDivide',n=tan_sine_out_div_md_node_name)
		tan_height_mul_mdl_node = cmds.createNode('multDoubleLinear',n=tan_height_mul_mdl_node_name)
		tan_angle_A_div_zero_counter_adl_node = cmds.createNode('addDoubleLinear',n=tan_angle_A_div_zero_counter_adl_node_name)

		#set parameters
		cmds.setAttr('{0}.input1D[0]'.format(tan_pma_node), 90)
		cmds.setAttr('{0}.operation'.format(tan_pma_node), 2)
		cmds.setAttr('{0}.operation'.format(tan_sine_out_div_md_node), 2)
		cmds.setAttr('{0}.input2'.format(tan_angle_A_sine_premult_mdl_node), 2)
		cmds.setAttr('{0}.input2'.format(tan_angle_B_sine_premult_mdl_node), 2)
		cmds.setAttr('{0}.input2'.format(tan_angle_A_div_zero_counter_adl_node), 0.0001)

		#connect nodes
		connect_nodes(half_angle_mdl_node,'output',tan_pma_node,'input1D[1]')
		connect_nodes(half_angle_mdl_node,'output',tan_angle_B_sine_premult_mdl_node,'input1')
		connect_nodes(tan_pma_node,'output1D',tan_angle_A_sine_premult_mdl_node,'input1')
		connect_nodes(tan_angle_A_sine_premult_mdl_node,'output',tan_angle_A_eulerToQuat_node,'inputRotateX')
		connect_nodes(tan_angle_B_sine_premult_mdl_node,'output',tan_angle_B_eulerToQuat_node,'inputRotateX')
		connect_nodes(tan_angle_A_eulerToQuat_node,'outputQuatX',tan_angle_A_div_zero_counter_adl_node,'input1')
		connect_nodes(tan_angle_A_div_zero_counter_adl_node,'output',tan_sine_out_div_md_node,'input2X')
		connect_nodes(tan_angle_B_eulerToQuat_node,'outputQuatX',tan_sine_out_div_md_node,'input1X')
		connect_nodes(tan_sine_out_div_md_node,'outputX',tan_height_mul_mdl_node,'input1')
		connect_nodes(distance_between_node,'distance',tan_height_mul_mdl_node,'input2')
		connect_nodes(tan_height_mul_mdl_node,'output',upper_cone_cls[1],'scaleX')
		connect_nodes(tan_height_mul_mdl_node,'output',upper_cone_cls[1],'scaleY')
		connect_nodes(tan_height_mul_mdl_node,'output',upper_cone_cls[1],'scaleZ')

		cmds.setAttr('{0}.visibility'.format(pose_rev_loc),0)
		cmds.setAttr('{0}.visibility'.format(upper_cone_cls[1]),0)
		cmds.setAttr('{0}.visibility'.format(lower_cone_cls[1]),0)

		cone_rev_dcm_node = cmds.createNode('decomposeMatrix',n=cone_decomp_rev_node_name)
		connect_nodes(pose_reader_grp,'inverseMatrix',cone_rev_dcm_node,'inputMatrix')
		connect_nodes(cone_rev_dcm_node,'outputTranslate',cone_nb,'translate')
		connect_nodes(cone_rev_dcm_node,'outputRotate',cone_nb,'rotate')
		cmds.select(pose_reader_grp)

		#cleanup
		cmds.setAttr('{0}.sx'.format(pose_reader_grp),lock=1)
		cmds.setAttr('{0}.sy'.format(pose_reader_grp),lock=1)
		cmds.setAttr('{0}.sz'.format(pose_reader_grp),lock=1)
		cmds.setAttr('{0}.sx'.format(base_loc),lock=1)
		cmds.setAttr('{0}.sy'.format(base_loc),lock=1)
		cmds.setAttr('{0}.sz'.format(base_loc),lock=1)
		cmds.setAttr('{0}.sx'.format(pose_loc),lock=1)
		cmds.setAttr('{0}.sy'.format(pose_loc),lock=1)
		cmds.setAttr('{0}.sz'.format(pose_loc),lock=1)
		cmds.setAttr('{0}.sx'.format(target_loc),lock=1)
		cmds.setAttr('{0}.sy'.format(target_loc),lock=1)
		cmds.setAttr('{0}.sz'.format(target_loc),lock=1)
		cmds.setAttr('{0}.sx'.format(cone_nb),lock=1)
		cmds.setAttr('{0}.sy'.format(cone_nb),lock=1)
		cmds.setAttr('{0}.sz'.format(cone_nb),lock=1)
		cmds.setAttr('{0}.sx'.format(upper_cls_grp_node),lock=1)
		cmds.setAttr('{0}.sy'.format(upper_cls_grp_node),lock=1)
		cmds.setAttr('{0}.sz'.format(upper_cls_grp_node),lock=1)
		cmds.setAttr('{0}.sx'.format(pose_rev_loc),lock=1)
		cmds.setAttr('{0}.sy'.format(pose_rev_loc),lock=1)
		cmds.setAttr('{0}.sz'.format(pose_rev_loc),lock=1)

		cmds.parent(const_group_node,pose_reader_grp)
		cmds.parent(upr_cls_point_const,const_group_node)
		cmds.parent(aim_const,const_group_node)

		cmds.undoInfo(cck=1)
if __name__ == "__main__":
	try:
		pose_reader_creation.close()
		pose_reader_creation.deleteLater()
	except:
		pass
	pose_reader_creation = PoseReaderCreation()
	pose_reader_creation.show()