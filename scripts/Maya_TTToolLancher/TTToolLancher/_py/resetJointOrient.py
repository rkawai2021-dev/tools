import maya.cmds as cmds

def resetJointOrient():
    jnts = cmds.ls(sl=True, type="joint")

    for jnt in jnts:
        for c in "xyz":
            cmds.setAttr(f"{jnt}.jo{c}", 0)