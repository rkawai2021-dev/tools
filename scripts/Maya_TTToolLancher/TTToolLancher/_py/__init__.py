# -*- coding: utf-8 -*-
""" """

try:
    from importlib import reload
except BaseException:
    pass

import maya.cmds as cmds


def getModuleDict():
    """_summary_

    Returns:
        _type_: _description_
    """
    moduleDict = {}
    moduleDict["Common"] = [
        {
            "index": 0,
            "name": "sampleScript",
            "label": "Sample script",
            "cmd": Activate_sampleMethod,
            "icn": "icon_sample",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
    ]
    moduleDict["Check"] = [
        {
            "index": 0,
            "name": "sampleScript",
            "label": "Sample script",
            "cmd": Activate_sampleMethod,
            "icn": "JS",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
    ]
    moduleDict["Rig"] = [
        {
            "index": 0,
            "name": "sampleScript",
            "label": "Sample script",
            "cmd": Activate_sampleMethod,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 1,
            "name": "JointLabel",
            "label": "Joint Label",
            "cmd": Activate_setJointLabelMethod,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 2,
            "name": "ResetJointOrient",
            "label": "Reset Joint Orient",
            "cmd": Activate_resetJointOrientMethod,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 3,
            "name": "ResetBindPose",
            "label": "Reset Bind Pose",
            "cmd": Activate_resetBindPoseMethod,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 4,
            "name": "SkinWeightTool",
            "label": "Skin Weight Tool",
            "cmd": Activate_resetBindPoseMethod,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 5,
            "name": "SnakeSupportBone",
            "label": "Snake Support Bone",
            "cmd": Activate_buildSanake,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 6,
            "name": "ConnectLocator",
            "label": "Connect Locator Snake",
            "cmd": Activate_connectLocator,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 7,
            "name": "SwitchConstraintWeight",
            "label": "Switch Constraint Weight",
            "cmd": Activate_switchConstraint,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 8,
            "name": "EditColor",
            "label": "Edit OverrideColor from outliner",
            "cmd": Activate_colorFromOutliner,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 9,
            "name": "HideLocalAxis",
            "label": "Hide Local Axis",
            "cmd": Activate_hideLocalAxis,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 10,
            "name": "DeleteConstraint",
            "label": "Delete Constraint Nodes",
            "cmd": Activate_deleteConst,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },
        {
            "index": 11,
            "name": "Orient To Rotate",
            "label": "Convert Orient to Rotate",
            "cmd": Activate_transferOToR,
            "icn": "",
            "annotation": "",
            "document": None,
            "tutorial": None,
        },

    ]
    return moduleDict


def getErrorDeco(func):
    def wrapper(*args, **kwargs):
        try:
            print("Activate success!")
            cmds.inViewMessage(fage=True, amg=func)
            func(*args, **kwargs)
        except BaseException:
            import traceback

            print(traceback.format_exc())

    return wrapper


# Common Tools
@getErrorDeco
def Activate_sampleMethod(*args, **kwargs):
    from . import sampleMethod

    reload(sampleMethod)
    sampleMethod.executeSampleScript()


@getErrorDeco
def Activate_setJointLabelMethod(*args, **kwargs):
    from . import setJointLable

    reload(setJointLable)
    setJointLable.setJointLabel()


@getErrorDeco
def Activate_resetJointOrientMethod(*args, **kwargs):
    from . import resetJointOrient

    reload(resetJointOrient)
    resetJointOrient.resetJointOrient()


@getErrorDeco
def Activate_resetBindPoseMethod(*args, **kwargs):
    from . import resetBindPose

    reload(resetBindPose)
    resetBindPose.resetBindPose()


@getErrorDeco
def Activate_skinWeightTool(*args, **kwargs):
    from . import skinWeightTool

    reload(skinWeightTool)
    skinWeightTool.show()


@getErrorDeco
def Activate_buildSanake(*args, **kwargs):
    from . import buildTwistJointForSnake as snake

    reload(snake)
    snake.createUI()


@getErrorDeco
def Activate_connectLocator(*args, **kwargs):
    from . import connect_locator_snake as cls

    reload(cls)
    cls.connect_locator_snake()


@getErrorDeco
def Activate_switchConstraint(*args, **kwargs):
    from . import switch_constraint_weight as scw

    reload(scw)
    scw.toggle_constraint_snake()


@getErrorDeco
def Activate_colorFromOutliner(*args, **kwargs):
    from . import colorFromOutlinerColor as cfo

    reload(cfo)
    cfo.color_from_outlinerColor()


@getErrorDeco
def Activate_hideLocalAxis(*args, **kwargs):
    from . import hideLocalAxis as hla

    reload(hla)
    hla.hideLocalAxis()


@getErrorDeco
def Activate_deleteConst(*args, **kwargs):
    from . import deleteConstraint as dc

    reload(dc)
    dc.deleteCoonstraint()


@getErrorDeco
def Activate_transferOToR(*args, **kwargs):
    from . import transferOrientToRotate as tor

    reload(tor)
    tor.transferOrientToRotate()