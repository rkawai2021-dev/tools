import maya.cmds as cmds
import maya.api.OpenMaya as om

class JointOrientTool:
    def __init__(self):
        self.window_name = "jointOrientToolWindow"
        self.window_width = 400
        self.window_height = 250
        
    def create_ui(self):
        """UIウィンドウを作成"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        
        cmds.window(self.window_name, title="Joint Orient Tool", widthHeight=(self.window_width, self.window_height))
        
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 15))
        
        cmds.text(label="ジョイントオリエント修正ツール", font="boldLabelFont", height=30)
        cmds.separator(height=10, style="in")
        
        cmds.text(label="選択したジョイントの現在の姿勢を保ったまま統一します", align="left")
        cmds.text(label="※スキンクラスター接続済みジョイントにも対応", align="left", font="smallPlainLabelFont")
        cmds.separator(height=10)
        
        cmds.text(label="統一方法を選択:", align="left", font="boldLabelFont")
        self.mode_radio = cmds.radioButtonGrp(
            numberOfRadioButtons=2,
            label="",
            labelArray2=["Joint Orientに統一", "Rotateに統一"],
            select=1,
            columnWidth3=(20, 150, 150)
        )
        
        cmds.separator(height=15)
        
        cmds.button(
            label="選択ジョイントに適用",
            height=40,
            backgroundColor=(0.4, 0.6, 0.4),
            command=lambda x: self.execute()
        )
        
        cmds.separator(height=5)
        
        cmds.button(
            label="閉じる",
            height=30,
            command=lambda x: cmds.deleteUI(self.window_name)
        )
        
        cmds.showWindow(self.window_name)
    
    def get_world_matrix(self, node):
        """ノードのワールド行列を取得"""
        sel = om.MSelectionList()
        sel.add(node)
        dag_path = sel.getDagPath(0)
        return dag_path.inclusiveMatrix()
        # return dag_path.exclusiveMatrix()

    def get_local_matrix(self, node):
        """ノードのローカル行列を取得"""
        sel = om.MSelectionList()
        sel.add(node)
        dag_path = sel.getDagPath(0)
        fn = om.MFnTransform(dag_path)

        return fn.transformation().asMatrix()

    def get_skin_clusters(self, joint):
        """ジョイントに接続されているスキンクラスターを取得"""
        skin_clusters = []
        connections = cmds.listConnections(joint, type="skinCluster", source=False, destination=True) or []
        for conn in connections:
            if conn not in skin_clusters:
                skin_clusters.append(conn)
        return skin_clusters
    
    def matrix_to_euler(self, matrix, rotation_order="xyz"):
        """行列からオイラー角を取得"""
        transform_matrix = om.MTransformationMatrix(matrix)
        euler = transform_matrix.rotation(asQuaternion=False)

        # 回転オーダーを設定
        order_map = {
            "xyz": om.MEulerRotation.kXYZ,
            "yzx": om.MEulerRotation.kYZX,
            "zxy": om.MEulerRotation.kZXY,
            "xzy": om.MEulerRotation.kXZY,
            "yxz": om.MEulerRotation.kYXZ,
            "zyx": om.MEulerRotation.kZYX
        }
        euler.reorderIt(order_map.get(rotation_order, om.MEulerRotation.kXYZ))
        print([om.MAngle(euler.x).asDegrees(), 
                om.MAngle(euler.y).asDegrees(), 
                om.MAngle(euler.z).asDegrees()])
        return [om.MAngle(euler.x).asDegrees(), 
                om.MAngle(euler.y).asDegrees(), 
                om.MAngle(euler.z).asDegrees()]
    
    def freeze_joint_to_orient(self, joint):
        """現在の姿勢をJoint Orientに統一"""
        # 回転オーダーを取得
        rot_order = cmds.getAttr(f"{joint}.rotateOrder")
        rot_order_names = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]
        rot_order_name = rot_order_names[rot_order]

        local_matrix = self.get_world_matrix(joint)
        
        
        # ローカル行列からオイラー角を取得
        euler_angles = self.matrix_to_euler(local_matrix, rot_order_name)
        
        # Joint Orientに設定、Rotateを0に
        cmds.setAttr(f"{joint}.jointOrient", *euler_angles)
        cmds.setAttr(f"{joint}.rotate", 0, 0, 0)
        
    
    def freeze_joint_to_rotate(self, joint):
        """現在の姿勢をRotateに統一"""
        # 回転オーダーを取得
        rot_order = cmds.getAttr(f"{joint}.rotateOrder")
        rot_order_names = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]
        rot_order_name = rot_order_names[rot_order]
        
        # ローカル行列を計算
        local_matrix = self.get_local_matrix(joint)
        
        # ローカル行列からオイラー角を取得
        euler_angles = self.matrix_to_euler(local_matrix, rot_order_name)
        
        # Rotateに設定、Joint Orientを0に
        cmds.setAttr(f"{joint}.rotate", *euler_angles)
        cmds.setAttr(f"{joint}.jointOrient", 0, 0, 0)
    
    def execute(self):
        """実行"""
        selected = cmds.ls(selection=True, type="joint")
        
        if not selected:
            cmds.warning("ジョイントを選択してください")
            return
        
        mode = cmds.radioButtonGrp(self.mode_radio, query=True, select=True)
        
        cmds.undoInfo(openChunk=True)
        
        try:
            processed_count = 0
            for joint in selected:
                try:
                    if mode == 1:
                        self.freeze_joint_to_orient(joint)
                    else:
                        self.freeze_joint_to_rotate(joint)
                    processed_count += 1
                except Exception as e:
                    cmds.warning(f"ジョイント '{joint}' の処理中にエラー: {str(e)}")
            
            cmds.select(selected)
            mode_name = "Joint Orient" if mode == 1 else "Rotate"
            print(f"完了: {processed_count}個のジョイントを{mode_name}に統一しました(姿勢保持)")
            
        finally:
            cmds.undoInfo(closeChunk=True)

def show():
    tool = JointOrientTool()
    tool.create_ui()

if __name__ == "__main__":
    show()