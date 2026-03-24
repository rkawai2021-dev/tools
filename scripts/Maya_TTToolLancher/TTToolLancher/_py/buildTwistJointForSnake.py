import maya.cmds as cmds

twist_dict = {
    "thigh_l": ["thigh_twist_01_l", -0.7],
    "thigh_r": ["thigh_twist_01_r", -0.7],
    "upperarm_l": ["upperarm_twist_01_l", -0.345],
    "upperarm_l": ["upperarm_twist_02_l", -0.5116],
    "upperarm_l": ["upperarm_twist_03_l", -0.317],
    "upperarm_r": ["upperarm_twist_01_r", -0.345],
    "upperarm_r": ["upperarm_twist_02_r", -0.5116],
    "upperarm_r": ["upperarm_twist_03_r", -0.317],
}


def buildTwistJoint():
    drivers = twist_dict.keys()
    # drivens = twist_dict.values()

    for d in drivers:
        target, rate = twist_dict[d]
        value = cmds.getAttr(f"{target}.rotateX")

        adl = cmds.createNode("addDoubleLinear", n=f"{target}_adl")
        mdl = cmds.createNode("multDoubleLinear", n=f"{target}_mdl")

        cmds.setAttr(f"{adl}.input2", value)
        cmds.setAttr(f"{mdl}.input2", rate)
        cmds.connectAttr(f"{d}.rotateX", f"{mdl}.input1")
        cmds.connectAttr(f"{mdl}.output", f"{adl}.input1")
        cmds.connectAttr(f"{adl}.output", f"{target}.rotateX")


def createUI():
    winName = "SnakeToolWindow"

    if cmds.window(winName, exists=True):
        cmds.deleteUI(winName)

    cmds.window(winName)
    cmds.columnLayout()
    cmds.button(label="BuildTwistJoint", command=buildTwistJoint())

    cmds.showWindow()
