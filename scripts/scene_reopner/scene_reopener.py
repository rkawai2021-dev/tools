import maya.cmds as cmds

def maya_scene_reopener():
    path = cmds.file(query=True, sceneName=True)

    if path:
        cmds.file(path, open=True, force=True)

    else:
        cmds.file(force=True, new=True)

maya_scene_reopener()