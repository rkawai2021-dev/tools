# -*- coding: utf-8 -*-
"""_summary_
"""
try:
    from importlib import reload
except BaseException:
    pass
from maya import cmds
from maya.common.ui import LayoutManager
from . import _py
import os
reload(_py)


def debug():
    print("aaaa")


def makeUI():
    winName = "TTRig"
    version = "0.1"
    btn_h = 32
    itemDict = _py.getModuleDict()
    iconPath = '{}/_icon'.format(os.path.dirname(__file__))

    # make window
    if cmds.window(winName, q=True, exists=True):
        cmds.deleteUI(winName)

    window = cmds.window(winName, title=u"TTTools v{}".format(version), sizeable=True,
                         maximizeButton=False, minimizeButton=False)
    # Layout
    with LayoutManager(cmds.tabLayout("tabs", innerMarginWidth=5, innerMarginHeight=5, tp="west")):
        for key in itemDict:
            with LayoutManager(cmds.columnLayout(key, adj=True)):
                for module in itemDict[key]:
                    with LayoutManager(cmds.rowLayout(nc=2, adj=2)):
                        iconpath = '{}/{}.png'.format(iconPath, module["icn"])
                        if not os.path.exists(iconpath):
                            iconpath = '{}/{}.png'.format(iconPath, "icon_default")
                        cmds.iconTextButton(l="aaa", h=btn_h, w=btn_h, style='iconOnly',
                                            image1=iconpath)
                        cmds.button(module["name"], h=btn_h, c=module["cmd"])

    cmds.showWindow(window)
    cmds.window(winName, e=True, widthHeight=(220, 240), sizeable=True)
