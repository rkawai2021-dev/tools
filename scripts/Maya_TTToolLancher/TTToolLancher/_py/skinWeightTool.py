import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import json
import os
from functools import partial

class SkinWeightManager:
    """スキンウェイトの書き出し・読み込みを管理するクラス"""
    
    def __init__(self):
        self.window_name = "skinWeightManagerWindow"
        self.weight_folder = ""
        self.available_files = []
        
    def export_weights(self, mesh, filepath):
        """指定メッシュのスキンウェイトをJSONファイルに書き出す"""
        # スキンクラスタを取得
        skin_cluster = self.get_skin_cluster(mesh)
        if not skin_cluster:
            om.MGlobal.displayWarning(f"{mesh} にスキンクラスタが見つかりません")
            return False
        
        # 影響を与えるジョイントのリストを取得
        influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        
        # 頂点数を取得
        vertex_count = cmds.polyEvaluate(mesh, vertex=True)
        
        # 各頂点の位置とウェイト情報を取得
        weight_data = {
            'mesh_name': mesh.split('|')[-1],  # ショートネーム
            'skin_cluster': skin_cluster,
            'influences': influences,
            'vertex_count': vertex_count,
            'weights': []
        }
        
        for vtx_id in range(vertex_count):
            # 頂点位置を取得
            pos = cmds.xform(f"{mesh}.vtx[{vtx_id}]", query=True, worldSpace=True, translation=True)
            
            # ウェイト値を取得
            weights = {}
            for inf in influences:
                weight_value = cmds.skinPercent(
                    skin_cluster,
                    f"{mesh}.vtx[{vtx_id}]",
                    transform=inf,
                    query=True
                )
                if weight_value > 0.0001:  # 微小値は除外
                    weights[inf] = weight_value
            
            weight_data['weights'].append({
                'index': vtx_id,
                'position': pos,
                'weights': weights
            })
        
        # JSONファイルに書き出し
        with open(filepath, 'w') as f:
            json.dump(weight_data, f, indent=2)
        
        return True
    
    def import_weights_by_index(self, mesh, filepath):
        """頂点番号ベースでウェイトを読み込む"""
        if not os.path.exists(filepath):
            om.MGlobal.displayError(f"ファイルが見つかりません: {filepath}")
            return False
        
        # JSONファイルを読み込み
        with open(filepath, 'r') as f:
            weight_data = json.load(f)
        
        # スキンクラスタを取得または作成
        skin_cluster = self.get_skin_cluster(mesh)
        if not skin_cluster:
            # スキンクラスタが存在しない場合は作成
            if not weight_data['influences']:
                om.MGlobal.displayError("ウェイトデータにインフルエンスが含まれていません")
                return False
            skin_cluster = cmds.skinCluster(weight_data['influences'], mesh, tsb=True)[0]
        
        # 現在のインフルエンスを取得
        current_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        
        # 不足しているインフルエンスを追加
        for inf in weight_data['influences']:
            if inf not in current_influences:
                if cmds.objExists(inf):
                    cmds.skinCluster(skin_cluster, edit=True, addInfluence=inf, weight=0)
                else:
                    om.MGlobal.displayWarning(f"ジョイント {inf} が見つかりません")
        
        # 頂点番号ベースでウェイトを設定
        vertex_count = cmds.polyEvaluate(mesh, vertex=True)
        for vtx_data in weight_data['weights']:
            vtx_id = vtx_data['index']
            if vtx_id >= vertex_count:
                continue
            
            # ウェイト値を設定
            transform_value = []
            for inf, weight in vtx_data['weights'].items():
                if cmds.objExists(inf):
                    transform_value.append((inf, weight))
            
            if transform_value:
                cmds.skinPercent(skin_cluster, f"{mesh}.vtx[{vtx_id}]", transformValue=transform_value)
        
        return True
    
    def import_weights_by_distance(self, mesh, filepath):
        """最近接点ベースでウェイトを読み込む"""
        if not os.path.exists(filepath):
            om.MGlobal.displayError(f"ファイルが見つかりません: {filepath}")
            return False
        
        # JSONファイルを読み込み
        with open(filepath, 'r') as f:
            weight_data = json.load(f)
        
        # スキンクラスタを取得または作成
        skin_cluster = self.get_skin_cluster(mesh)
        if not skin_cluster:
            if not weight_data['influences']:
                om.MGlobal.displayError("ウェイトデータにインフルエンスが含まれていません")
                return False
            skin_cluster = cmds.skinCluster(weight_data['influences'], mesh, tsb=True)[0]
        
        # 現在のインフルエンスを取得
        current_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        
        # 不足しているインフルエンスを追加
        for inf in weight_data['influences']:
            if inf not in current_influences:
                if cmds.objExists(inf):
                    cmds.skinCluster(skin_cluster, edit=True, addInfluence=inf, weight=0)
                else:
                    om.MGlobal.displayWarning(f"ジョイント {inf} が見つかりません")
        
        # ターゲットメッシュの頂点数を取得
        vertex_count = cmds.polyEvaluate(mesh, vertex=True)
        
        # 各頂点に対して最近接点を探してウェイトをコピー
        for vtx_id in range(vertex_count):
            # 現在の頂点位置
            current_pos = cmds.xform(f"{mesh}.vtx[{vtx_id}]", query=True, worldSpace=True, translation=True)
            
            # 最近接点を探す
            min_distance = float('inf')
            closest_vtx_data = None
            
            for vtx_data in weight_data['weights']:
                source_pos = vtx_data['position']
                distance = self.calculate_distance(current_pos, source_pos)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_vtx_data = vtx_data
            
            # 最近接点のウェイトを適用
            if closest_vtx_data:
                transform_value = []
                for inf, weight in closest_vtx_data['weights'].items():
                    if cmds.objExists(inf):
                        transform_value.append((inf, weight))
                
                if transform_value:
                    cmds.skinPercent(skin_cluster, f"{mesh}.vtx[{vtx_id}]", transformValue=transform_value)
        
        return True
    
    @staticmethod
    def calculate_distance(pos1, pos2):
        """2点間の距離を計算"""
        return ((pos1[0] - pos2[0]) ** 2 + 
                (pos1[1] - pos2[1]) ** 2 + 
                (pos1[2] - pos2[2]) ** 2) ** 0.5
    
    @staticmethod
    def get_skin_cluster(mesh):
        """メッシュに関連付けられたスキンクラスタを取得"""
        history = cmds.listHistory(mesh, pruneDagObjects=True)
        if history:
            skin_clusters = cmds.ls(history, type='skinCluster')
            if skin_clusters:
                return skin_clusters[0]
        return None
    
    def create_ui(self):
        """UIを作成"""
        # 既存のウィンドウを削除
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        # ウィンドウを作成
        window = cmds.window(self.window_name, title="Skin Weight Manager", widthHeight=(450, 500))
        
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))
        
        # エクスポートセクション
        cmds.frameLayout(label="Export Weights", collapsable=True, collapse=False, marginHeight=5, marginWidth=5)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        cmds.text(label="選択したメッシュのウェイトを書き出し", align='left', font='boldLabelFont')
        cmds.separator(height=5, style='none')
        
        export_layout = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 350), (2, 80)])
        cmds.textField('exportPathField', text='', editable=False)
        cmds.button(label="Browse", command=self.browse_export_folder)
        cmds.setParent('..')
        
        cmds.separator(height=5, style='none')
        cmds.button(label="Export Selected Meshes", height=30, backgroundColor=(0.4, 0.6, 0.4), 
                   command=self.export_selected_meshes)
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        cmds.separator(height=10)
        
        # インポートセクション
        cmds.frameLayout(label="Import Weights", collapsable=True, collapse=False, marginHeight=5, marginWidth=5)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        cmds.text(label="ウェイトファイルのフォルダを選択", align='left', font='boldLabelFont')
        cmds.separator(height=5, style='none')
        
        import_layout = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 350), (2, 80)])
        cmds.textField('importPathField', text='', editable=False)
        cmds.button(label="Browse", command=self.browse_import_folder)
        cmds.setParent('..')
        
        cmds.separator(height=5, style='none')
        cmds.button(label="Refresh File List", command=self.refresh_file_list)
        
        cmds.separator(height=5, style='none')
        cmds.text(label="利用可能なウェイトファイル:", align='left')
        cmds.textScrollList('weightFileList', numberOfRows=8, allowMultiSelection=False, 
                           selectCommand=self.on_file_selected)
        
        cmds.separator(height=10)
        cmds.text(label="ペースト方式:", align='left', font='boldLabelFont')
        cmds.radioButtonGrp('pasteMethodRadio', labelArray2=['頂点番号', '最近接距離'], 
                           numberOfRadioButtons=2, select=1, columnWidth2=[100, 100])
        
        cmds.separator(height=10)
        cmds.button(label="Import to Selected Meshes (Name Match)", height=35, 
                   backgroundColor=(0.4, 0.5, 0.6),
                   command=self.import_to_selected_meshes)
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        cmds.separator(height=10)
        
        # ステータス表示
        cmds.frameLayout(label="Status", collapsable=True, collapse=False, marginHeight=5, marginWidth=5)
        cmds.columnLayout(adjustableColumn=True)
        cmds.textField('statusField', editable=False, text='Ready')
        cmds.setParent('..')
        cmds.setParent('..')
        
        cmds.showWindow(window)
    
    def browse_export_folder(self, *args):
        """エクスポート先フォルダを選択"""
        folder = cmds.fileDialog2(fileMode=3, caption="Select Export Folder")
        if folder:
            cmds.textField('exportPathField', edit=True, text=folder[0])
    
    def browse_import_folder(self, *args):
        """インポート元フォルダを選択"""
        folder = cmds.fileDialog2(fileMode=3, caption="Select Import Folder")
        if folder:
            self.weight_folder = folder[0]
            cmds.textField('importPathField', edit=True, text=self.weight_folder)
            self.refresh_file_list()
    
    def refresh_file_list(self, *args):
        """ウェイトファイルリストを更新"""
        cmds.textScrollList('weightFileList', edit=True, removeAll=True)
        self.available_files = []
        
        if not self.weight_folder or not os.path.exists(self.weight_folder):
            self.update_status("フォルダが選択されていません")
            return
        
        # .jsonファイルを検索
        for filename in os.listdir(self.weight_folder):
            if filename.endswith('.json'):
                self.available_files.append(filename)
                cmds.textScrollList('weightFileList', edit=True, append=filename)
        
        self.update_status(f"{len(self.available_files)} 個のウェイトファイルが見つかりました")
    
    def on_file_selected(self, *args):
        """ファイルが選択された時の処理"""
        selected = cmds.textScrollList('weightFileList', query=True, selectItem=True)
        if selected:
            self.update_status(f"選択: {selected[0]}")
    
    def export_selected_meshes(self, *args):
        """選択されたメッシュのウェイトを書き出し"""
        export_path = cmds.textField('exportPathField', query=True, text=True)
        if not export_path:
            self.update_status("エクスポート先フォルダを選択してください")
            om.MGlobal.displayError("エクスポート先フォルダを選択してください")
            return
        
        selected = cmds.ls(selection=True, type='transform')
        if not selected:
            self.update_status("メッシュが選択されていません")
            om.MGlobal.displayError("メッシュを選択してください")
            return
        
        exported_count = 0
        for obj in selected:
            # メッシュシェイプを取得
            shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
            if not shapes:
                continue
            
            mesh_name = obj.split('|')[-1]  # ショートネーム
            filepath = os.path.join(export_path, f"{mesh_name}_weights.json")
            
            if self.export_weights(obj, filepath):
                exported_count += 1
                om.MGlobal.displayInfo(f"エクスポート完了: {filepath}")
        
        self.update_status(f"{exported_count} 個のメッシュをエクスポートしました")
    
    def import_to_selected_meshes(self, *args):
        """選択されたメッシュに名前が一致するウェイトファイルを読み込み"""
        if not self.weight_folder:
            self.update_status("インポート元フォルダを選択してください")
            om.MGlobal.displayError("インポート元フォルダを選択してください")
            return
        
        selected = cmds.ls(selection=True, type='transform')
        if not selected:
            self.update_status("メッシュが選択されていません")
            om.MGlobal.displayError("メッシュを選択してください")
            return
        
        # ペースト方式を取得
        paste_method = cmds.radioButtonGrp('pasteMethodRadio', query=True, select=True)
        
        imported_count = 0
        for obj in selected:
            # メッシュシェイプを取得
            shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
            if not shapes:
                continue
            
            mesh_name = obj.split('|')[-1]  # ショートネーム
            filepath = os.path.join(self.weight_folder, f"{mesh_name}_weights.json")
            
            if not os.path.exists(filepath):
                om.MGlobal.displayWarning(f"{mesh_name} に対応するウェイトファイルが見つかりません")
                continue
            
            # ペースト方式に応じて実行
            success = False
            if paste_method == 1:  # 頂点番号
                success = self.import_weights_by_index(obj, filepath)
            else:  # 最近接距離
                success = self.import_weights_by_distance(obj, filepath)
            
            if success:
                imported_count += 1
                om.MGlobal.displayInfo(f"インポート完了: {mesh_name}")
        
        method_name = "頂点番号" if paste_method == 1 else "最近接距離"
        self.update_status(f"{imported_count} 個のメッシュに {method_name} 方式でインポートしました")
    
    def update_status(self, message):
        """ステータスメッセージを更新"""
        if cmds.textField('statusField', exists=True):
            cmds.textField('statusField', edit=True, text=message)


# ツールを起動
def show():
    manager = SkinWeightManager()
    manager.create_ui()