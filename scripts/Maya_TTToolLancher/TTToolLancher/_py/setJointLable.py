import maya.cmds as cmds
import re

def setJointLabel():
    jnts = cmds.ls(type="joint")

    for jnt in jnts:
        side = 0
        if re.search(".*_r_.*$|.*_R_.*$|.*_r$|.*_R$", jnt):
            side = 2
        if re.search(".*_l_.*$|.*_L_.*$|.*_l$|.*_L$", jnt):
            side = 1

        cmds.setAttr(f"{jnt}.side", side)
        cmds.setAttr(f"{jnt}.type", 18)
        cmds.setAttr(f"{jnt}.otherType", jnt, type="string")