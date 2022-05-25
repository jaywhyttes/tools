"""
+-------------------------------------------------------------+
| simple tool to create a curve out of a objects bounding box |
|-------------------------------------------------------------|
| 1)    Select your object.                                   |
| 2)    Run the script.                                       |
+-------------------------------------------------------------+
"""
import maya.cmds as cmds

def bbox_ctrl():
    sel = cmds.ls(sl=True,fl=True)
    if cmds.objectType(sel[0]) == 'mesh':
        bbox_name = sel[0].split('.')[0]
    else:
        bbox_name = sel[0]
    try:
        bbox = cmds.exactWorldBoundingBox(sel)
        crvData = { "points":[(bbox[0],bbox[4],bbox[2]),
        (bbox[3],bbox[4],bbox[2]),
        (bbox[3],bbox[1],bbox[2]),
        (bbox[3],bbox[4],bbox[2]),
        (bbox[3],bbox[4],bbox[5]),
        (bbox[3],bbox[1],bbox[5]),
        (bbox[3],bbox[4],bbox[5]),
        (bbox[0],bbox[4],bbox[5]),
        (bbox[0],bbox[1],bbox[5]),
        (bbox[0],bbox[4],bbox[5]),
        (bbox[0],bbox[4],bbox[2]),
        (bbox[0],bbox[1],bbox[2]),
        (bbox[3],bbox[1],bbox[2]),
        (bbox[3],bbox[1],bbox[5]),
        (bbox[0],bbox[1],bbox[5]),
        (bbox[0],bbox[1],bbox[2])],
        "knots":range(0,16)}
        bbox_crv = cmds.curve(n = '{}_bbox_ctrl'.format(bbox_name), d=1,p=crvData['points'],k=crvData['knots'])
        cmds.select(cl=1)
    except TypeError:
        pass
bbox_ctrl()
