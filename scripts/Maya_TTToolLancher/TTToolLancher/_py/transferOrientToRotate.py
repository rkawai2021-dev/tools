import maya.cmds as cmds


def transferOrientToRotate():
    jnts = cmds.ls(type="joint")


    for jnt in jnts:
        world_m = cmds.xform(jnt, q=True, m=True, ws=True)
        
        cmds.setAttr(f"{jnt}.jo", 0, 0, 0)
        cmds.setAttr(f"{jnt}.r", 0, 0, 0)

        cmds.xform(jnt, m=world_m, ws=True)