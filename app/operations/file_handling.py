from pathlib import Path
import os

def get_admin_path():
    return Path.home()

def folder_check(type_: str, image_type: str = "png") -> dict:
    try:
        path = Path(get_admin_path()) / ".fastAPI_DATA"
        message = 'we '

        if os.path.isdir(path):
            message += "we found the directory"
        else:
            message += "did not find the directory so creating new one"
            os.mkdir(path)
        if os.path.isdir(path / "uploaded"):
            message += "\n we Already have uploaded folder"
        else:
            message += "\n we have created uploaded folder"
            os.mkdir(path / "uploaded")

        if os.path.isdir(path / "updated"):
            message += "\n we Already have updated folder"
        else:
            message += "\n we have created uploaded folder"
            os.mkdir(path / "updated")

        if os.path.isdir(path / "recreated"):
            message += "\n we Already have output folder"
        else:
            message += "\n we have created new folder for output"
            os.mkdir(path / "recreated")

    except Exception as e:
        return {'message': str(e), 'status': False}

    return {'message': message, 'status': True}
