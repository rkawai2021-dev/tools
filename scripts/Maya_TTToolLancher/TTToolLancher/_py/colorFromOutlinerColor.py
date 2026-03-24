import maya.cmds as cmds


def color_from_outlinerColor():
    jnts = cmds.ls(type="joint")
    cmds.color(jnts)
    for jnt in jnts:
        use = cmds.getAttr(f"{jnt}.useOutlinerColor")
        if use:
            r = cmds.getAttr(f"{jnt}.outlinerColorR")
            g = cmds.getAttr(f"{jnt}.outlinerColorG")
            b = cmds.getAttr(f"{jnt}.outlinerColorB")
            cmds.setAttr(f"{jnt}.overrideRGBColors", 1)
            cmds.setAttr(f"{jnt}.overrideEnabled", 1)
            cmds.setAttr(f"{jnt}.overrideColorR", r)
            cmds.setAttr(f"{jnt}.overrideColorG", g)
            cmds.setAttr(f"{jnt}.overrideColorB", b)


    jnts = cmds.ls(type="joint")

    for jnt in jnts:
        if jnt.startswith("CSB_"):
            cmds.setAttr(f"{jnt}.overrideRGBColors", 1)
            cmds.setAttr(f"{jnt}.overrideColorRGB", (0.0, 0.5, 0.5))
            cmds.setAttr(f"{jnt}.useOutlinerColor", 1)
            cmds.setAttr(f"{jnt}.outlinerColor", (0.0, 0.5, 0.5))
