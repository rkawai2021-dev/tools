import maya.cmds as cmds


def hideLocalAxis():
    jnts = cmds.ls(type="joint")
    for jnt in jnts:
        cmds.setAttr(f"{jnt}.displayLocalAxis", 0)