from maya import cmds


def resetBindPose():
    poses = cmds.ls(type="dagPose")
    cmds.delete(poses)

    jnts = cmds.ls(type="joint")

    bpose = cmds.dagPose(jnts, bindPose=True, save=True)
    clusters = getSkinCulsters(jnts)
    if clusters:
        for cluster in clusters:
            cmds.connectAttr(f"{bpose}.message", f"{cluster}.bindPose", f=True)


def new_resetBindPose():
    jnts = cmds.ls(type="joint")

    dagPoses = cmds.ls(type="dagPose")
    for dagPose in dagPoses:
        cmds.listConnections()


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
        print(jnts)
        print(joints)
        if not set(jnts).isdisjoint(joints):
            clusterList.append(c)

    return clusterList
