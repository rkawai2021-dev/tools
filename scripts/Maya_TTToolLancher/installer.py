# -*- coding: utf-8 -*-
"""_summary_
"""
import os
from maya import cmds, mel


def onMayaDroppedPythonFile(*args, **kwargs):
    create_shelf()


def create_shelf():
    script_path = os.path.dirname(__file__)

    command = """try:
    from importlib import reload
except:
    pass

import sys
from maya import cmds
if not '{0}' in sys.path:
    sys.path.append('{0}')
def TTToolLancher_Activate(*args,**kwargs):
    import TTToolLancher
    reload(TTToolLancher)
    TTToolLancher.activate()
TTToolLancher_Activate()
""".format(script_path)

    print(command)
    shelf = mel.eval("$gShelfTopLevel=$gShelfTopLevel")
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)
    try:
        cmds.shelfButton(command=command,
                         image1='commandButton.xpm',
                         label="TTToolLancher",
                         sourceType="Python",
                         parent=parent
                         )
    except BaseException:
        import traceback
        print(traceback.format_exc())
