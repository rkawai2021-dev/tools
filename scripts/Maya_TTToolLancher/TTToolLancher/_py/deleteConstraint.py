import maya.cmds as cmds


def deleteCoonstraint():
    cnst = cmds.ls(type="constraint")

    cmds.delete(cnst)