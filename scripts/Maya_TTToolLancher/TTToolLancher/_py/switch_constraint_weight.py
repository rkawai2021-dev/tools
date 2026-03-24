import maya.cmds as cmds


def toggle_constraint_snake():
    p_cns = cmds.ls("model_root", type="parentConstraint", dag=True)
    s_cns = cmds.ls("model_root", type="scaleConstraint", dag=True)

    for p, s in zip(p_cns, s_cns):
        print(p, s)
        j = cmds.listConnections(p, s=True, type="joint")[0]
        name = j.split("|")[-1]
        
        if cmds.objExists(f"{p}.{name}W1"):
            v = cmds.getAttr(f"{p}.{name}W0")

            if v:
                cmds.setAttr(f"{p}.{name}W0", 0)
                cmds.setAttr(f"{s}.{name}W0", 0)
                cmds.setAttr(f"{p}.{name}W1", 1)
                cmds.setAttr(f"{s}.{name}W1", 1)

            else:
                cmds.setAttr(f"{p}.{name}W0", 1)
                cmds.setAttr(f"{s}.{name}W0", 1)
                cmds.setAttr(f"{p}.{name}W1", 0)
                cmds.setAttr(f"{s}.{name}W1", 0)
