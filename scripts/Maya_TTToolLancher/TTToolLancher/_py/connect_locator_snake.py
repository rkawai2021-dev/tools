import maya.cmds as cmds

def connect_locator_snake():
    jnts = cmds.ls("model_root", dag=True, type="joint")

    nodes = cmds.ls("BindPose", dag=True)
    locs = []

    for node in nodes:
        nodeType = cmds.nodeType(node)
        if nodeType == "transform":
            locs.append(node)

    for jnt in jnts:
        name = jnt.split("|")[-1]
        sufix = name.split("_")[-1]
        if sufix == "phy":
            continue
        for loc in locs:
            n = loc.split("|")[-1]
            if name == n:
                p = cmds.parentConstraint(loc, jnt)
                s = cmds.scaleConstraint(loc, jnt)