try:
    from importlib import reload
except BaseException:
    pass
from . import ui
reload(ui)


def activate(*args, **kwargs):
    ui.makeUI()
