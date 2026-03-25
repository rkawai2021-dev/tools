from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma


def resetBindPose():
    poses = cmds.ls(type="dagPose")
    if poses:
        cmds.delete(poses)

    jnts = cmds.ls(type="joint")

    bpose = cmds.dagPose(jnts, bindPose=True, save=True)

    clusters = getSkinCulsters(jnts)
    if not clusters:
        return

    for cluster in clusters:
        sel = om.MSelectionList()
        sel.add(cluster)
        obj = sel.getDependNode(0)

        skin_fn = oma.MFnSkinCluster(obj)

        infs:list[om.MDagPath] = skin_fn.influenceObjects()

        for i in range(infs.length()):
            dag = infs[i]

            index = skin_fn.indexForInfluenceObject(dag)

            world_matrix = dag.inclusiveMatrix()
            bind_pre = world_matrix.inverse()

            plug = skin_fn.findPlug("bindPreMatrix", False).elementByLogicalIndex(index)
            plug.setMObject(om.MFnMatrixData().create(bind_pre))

        cmds.connectAttr(f"{bpose}.message", f"{cluster}.bindPose", f=True)


def deleteDagPose():
    dagPoses = cmds.ls(type="dagPose")

    cmds.delete(dagPoses)


def getSkinCulsters(joints):
    cl = cmds.ls(type="skinCluster")
    clusterList = []

    if not cl:
        return False

    for c in cl:
        jnts = cmds.listConnections(f"{c}.matrix", s=True, type="joint")

        if not jnts:
            continue
        if not set(jnts).isdisjoint(joints):
            clusterList.append(c)

    return clusterList
