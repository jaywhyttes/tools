"""
+-------------------------------------------------------------+
| simple tool to create a curve out of a objects bounding box |
|-------------------------------------------------------------|
| 1)	Select your object(s).							      |
| 2)	Run the script.										  |
+-------------------------------------------------------------+
"""
import maya.cmds as cmds
sel = cmds.ls(sl=True)
for i in range(0, len(sel)):
	try:
		bbox = cmds.exactWorldBoundingBox(sel[i])
		crvData = {	"points":[(bbox[0],bbox[4],bbox[2]),
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
		(bbox[0],bbox[1],bbox[2]),],
		"knots":range(0,16)}
		bbox_crv = cmds.curve(n = '{}_bbox_ctrl'.format(sel[i][0]), d=1,p=crvData['points'],k=crvData['knots'])
		cmds.select(cl=1)
	except TypeError:
		pass
