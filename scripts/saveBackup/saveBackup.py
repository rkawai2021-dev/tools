import os
import shutil
import maya.cmds as cmds

def backup_scene() -> None:
    """現在のmayaシーンのバックアップを作成し、現在の名前で保存し直す"""

    current_file = cmds.file(query=True, sceneName=True)

    # 保存されていないシーン
    if not current_file:
        cmds.inViewMessage(fade=True, message="シーンが保存されていません。")
        return

    base_name, ext = os.path.splitext(current_file)

    # 次のバックアップ名を取得
    backup_name = get_next_backup_name(base_name, ext)

    # --- バックアップ作成 ---
    shutil.copy2(current_file, backup_name)

    # --- 現在のシーンをそのままの名前で保存 ---
    cmds.file(force=True, save=True, type="mayaAscii" if ext == ".ma" else "mayaBinary")

    cmds.inViewMessage(fade=True, message=f"バックアップ作成: {os.path.basename(backup_name)}")


def get_next_backup_name(base_name: str, ext: str) -> str:
    """引数で渡されたファイルと同階層にあるファイルを取得し、新しいインデックスを取得する
    chara_rig.ma
    chara_rig_t01.ma
    chara_rig_t02.ma
    chara_rig_t03.ma
    → chara_rig_t04.ma 次のテイク数
    
    Args:
        base_name (str): ファイル形式を除いたファイルのパス
        ext (str): ファイル形式

    Returns:
        str: ファイルのフルパス
    """
    index = 1
    while os.path.exists(f"{base_name}_t{index:02d}{ext}"):
        index += 1
    return f"{base_name}_t{index:02d}{ext}"