import json
import os
import re
import uuid
import maya.cmds as cmds
from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from maya.common.ui import LayoutManager


CURRENT_FILE = os.path.normpath(__file__)
path, ext = os.path.splitext(CURRENT_FILE)
UI_FILE = path + ".ui"
print(UI_FILE)

class node_color_editor(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(node_color_editor, self).__init__(*args, **kwargs)

        self.widget = QUiLoader().load(UI_FILE)
        self.setWindowTitle(self.widget.windowTitle())

        self.setCentralWidget(self.widget)


        self.connect_ui()


        self.window_name = "node_color_editor"
        self.use_rgb = False
        self.color_presets = {}

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def create_main_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        self.window = cmds.window(self.window_name, title="ノード色変更ツール", widthHeight=(400, 350))
        self.layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        with LayoutManager(cmds.frameLayout(label="カラーモード選択")) as mode_frame:
            self.use_rgb = cmds.radioButtonGrp(
                label="カラーモード：",
                labelArray2=["Index", "RGB"],
                numberOfRadioButtons=2,
                select=2,
                onCommand=self.switch_type
            )

        with LayoutManager(cmds.frameLayout(label="カラー入力")) as color_frame:
            self.index_field = cmds.colorIndexSliderGrp(
                label="Index",
                min=0,
                max=31,
                value=1,
                enable=False
            )
            self.rgb_field = cmds.colorSliderGrp(
                label="RGB",
                rgb=(1, 0, 0),
            )
            self.use_olr = cmds.checkBox(
                "outlinerCB",
                label="アウトライナーへ反映",
                value=True
            )
            self.reset_wireframecolor = cmds.checkBox(
                "wireframeColorCB",
                label = "ワイヤーフレームカラーをリセット",
                value=True
            )

        cmds.button(label="選択ノードに色を適用", command=self.apply_color)
        cmds.button(label="選択ノードをデフォルトにリセット", command=self.reset_color)

        cmds.button(label="正規表現プリセットを適用", command=self.apply_preset_regex)

        cmds.separator(style="in")
        cmds.button(label="JSONプリセット読み込み", command=self.load_presets)
        cmds.button(label="JSONプリセット書き出し（選択ノード）", command=self.export_presets)

        cmds.showWindow(self.window)

    def file_browse(self):
        path = cmds.fileDialog2(
            fileFilter="*.json",
            fileMode=0
        )[0]

        if not path:
            return
        
        self.widget.le_dirc.setText(path)

        with open(path, 'r') as f:
            self.color_presets = json.load(f)
        self.apply_preset_regex()

        cmds.inViewMessage(amg='プリセット読み込み完了', pos='topCenter', fade=True)

    def connect_ui(self):
        # レイアウトを作成（QVBoxLayoutなど）
        self.layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_main)
        
        # QGroupBoxをウィジェットとして作成
        self.groupbox_main = QtWidgets.QGroupBox()
        self.groupbox_main.setObjectName("NODE_COLOR_EDITOR_GB_EDIT_NAME_" + str(uuid.uuid4()))
        
        # QGroupBoxをレイアウトに追加
        self.layout_main.addWidget(self.groupbox_main)
        
        # Mayaのコマンドで親を設定
        cmds.setParent(self.groupbox_main.objectName())
        self.rgb = cmds.colorSliderGrp()

        self.widget.pb_browse.clicked.connect(self.file_browse)
        self.widget.pb_apply_json.clicked.connect(self.apply_preset_regex)

    # ---------------------------------------------------------
    # Mode Switch
    # ---------------------------------------------------------
    def switch_type(self, *args):
        selected = cmds.radioButtonGrp(self.color_mode, query=True, select=True)
        self.use_rgb = (selected == 2)
        cmds.colorIndexSliderGrp(self.index_field, edit=True, enable=not self.use_rgb)
        cmds.colorSliderGrp(self.rgb_field, edit=True, enable=self.use_rgb)

    # ---------------------------------------------------------
    # Apply Color manually
    # ---------------------------------------------------------
    def apply_color(self, *args):
        selection = self.get_selected_nodes()
        if not selection:
            cmds.warning("ノードを選択してください")
            return
        
        for node in selection:
            node = self.get_fullpath_node(node)

            cmds.setAttr(f"{node}.overrideEnabled", 1)
            print(self.use_rgb)
            if self.use_rgb:
                rgb = cmds.colorSliderGrp(self.rgb_field, query=True, rgbValue=True)
                
                cmds.setAttr(f"{node}.overrideRGBColors", 1)
                cmds.setAttr(f"{node}.overrideColorRGB", *rgb)
            else:
                idx = cmds.colorIndexSliderGrp(self.index_field, query=True, value=True)
                cmds.setAttr(f"{node}.overrideRGBColors", 0)
                cmds.setAttr(f"{node}.overrideColor", int(idx))

            if cmds.checkBox(self.use_olr, query=True, value=True):
                cmds.setAttr(f"{node}.useOutlinerColor", 1)
                if self.use_rgb:
                    cmds.setAttr(f"{node}.outlinerColor", *rgb)
                else:
                    # index → RGB 変換はしない（outliner は RGB のみ）
                    pass

    # ---------------------------------------------------------
    # Apply JSON preset by Regex
    # ---------------------------------------------------------
    def apply_preset_regex(self, *args):
        if not self.color_presets:
            cmds.warning("プリセットが読み込まれていません")
            return

        selection = self.get_selected_nodes()
        if not selection:
            cmds.warning("ノードを選択してください")
            return

        for node in selection:
            node_full = self.get_fullpath_node(node)

            for pattern, data in self.color_presets.items():
                if re.match(pattern, node_full):
                    self.apply_color_from_dict(node_full, data)

    def apply_color_from_dict(self, node, data):
        if not data["override"]:
            self.reset_color()
            return
        if cmds.checkBox(self.reset_wireframecolor, query=True, value=True):
            cmds.color(node)

        cmds.setAttr(f"{node}.overrideEnabled", 1)

        if data["is_rgb"]:
            r, g, b = data["display_color"]
            cmds.setAttr(f"{node}.overrideRGBColors", 1)
            cmds.setAttr(f"{node}.overrideColorRGB", r, g, b)
        else:
            cmds.setAttr(f"{node}.overrideRGBColors", 0)
            cmds.setAttr(f"{node}.overrideColor", int(data["display_color"]))

        if data["use_outliner"]:
            cmds.setAttr(f"{node}.useOutlinerColor", 1)
            if data["outliner_color"]:
                cmds.setAttr(f"{node}.outlinerColor", *data["outliner_color"])

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------
    def reset_color(self, *args):
        selection = self.get_selected_nodes()
        if cmds.checkBox(self.reset_wireframecolor, query=True, value=True):
            cmds.color(selection)

        if not selection:
            cmds.warning("ノードを選択してください")
            return

        for node in selection:
            node = self.get_fullpath_node(node)
            cmds.setAttr(f"{node}.overrideEnabled", 0)
            cmds.setAttr(f"{node}.overrideRGBColors", 0)
            cmds.setAttr(f"{node}.useOutlinerColor", 0)
            cmds.setAttr(f"{node}.overrideColor", 0)

    # ---------------------------------------------------------
    # JSON IO
    # ---------------------------------------------------------
    def load_presets(self, *args):
        file_path = cmds.fileDialog2(fileMode=1, caption="JSONプリセットを選択")
        if not file_path:
            return

        with open(file_path[0], 'r') as f:
            self.color_presets = json.load(f)

        cmds.inViewMessage(amg='プリセット読み込み完了', pos='topCenter', fade=True)

    def export_presets(self, *args):
        selection = self.get_selected_nodes()
        if not selection:
            cmds.warning("ノードを選択して実行してください")
            return
        
        file_path = cmds.fileDialog2(ff="*.json", dialogStyle=1, fileMode=0)
        if not file_path:
            return

        export_dict = {}

        for node in selection:
            info = self.get_state(node)
            export_dict.update(info)

        with open(file_path[0], "w", encoding="utf-8") as f:
            json.dump(export_dict, f, indent=4)

        cmds.inViewMessage(amg='JSON書き出し完了', pos='topCenter', fade=True)

    # ---------------------------------------------------------
    # Node State
    # ---------------------------------------------------------
    def get_state(self, node):
        node = self.get_fullpath_node(node)
        is_override = cmds.getAttr(f"{node}.overrideEnabled")
        is_rgb = cmds.getAttr(f"{node}.overrideRGBColors")

        if is_rgb:
            display_color = cmds.getAttr(f"{node}.overrideColorRGB")[0]
        else:
            display_color = cmds.getAttr(f"{node}.overrideColor")

        is_outliner = cmds.getAttr(f"{node}.useOutlinerColor")
        if is_outliner:
            outline_color = cmds.getAttr(f"{node}.outlinerColor")[0]
        else:
            outline_color = []

        return {
            node: {
                "override": is_override,
                "is_rgb": is_rgb,
                "display_color": display_color,
                "use_outliner": is_outliner,
                "outliner_color": outline_color
            }
        }

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def get_selected_nodes(self):
        return cmds.ls(sl=True) or []

    def get_fullpath_node(self, node):
        return cmds.ls(node, long=True)[0]
