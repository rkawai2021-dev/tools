from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma
from maya import cmds


class WeightEditor:
    def main(self):
        meshes = self.getTargetMeshes()
        if meshes is None:
            self.printMessage()

        weights = oma.MFnSkinCluster.getWeights(meshes)
        print(weights)

    def getTargetMeshes(self):
        """選択されているメッシュを取得する

        Returns:
            _type_: _description_
        """
        sel:MSelectionList = om.MGlobal.getActiveSelectionList()
        meshPath = sel.get

        if sel.isEmpty():
            return None

        return sel

    def printMessage(self, type=0, message=""):
        """引数で渡された文字列をprintする
        typeでエラー、警告、アナウンスと意味合いを分ける

        Args:
            type (int, optional): _description_. Defaults to 0.
            message (str, optional): _description_. Defaults to "".
        """
        cmds.inViewMessage()

c = WeightEditor()
c.main()