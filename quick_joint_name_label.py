import maya.cmds as cmds

def quick_joint_name_label():
    jnt = cmds.ls(sl=True,type='joint')
    for j in jnt:
        jntLblName = j[2:]
        jntLblSide = j[0]
        if jntLblSide == 'C':
            jntLblSide = 0  
        elif jntLblSide == 'L':
            jntLblSide = 1
        elif jntLblSide == 'R':
            jntLblSide = 2
        else:
            jntLblSide = 3
    
        cmds.setAttr('{0}.side'.format(j),jntLblSide)
        cmds.setAttr('{0}.type'.format(j),18)
        cmds.setAttr('{0}.otherType'.format(j),jntLblName,type='string')

quick_joint_name_label()
