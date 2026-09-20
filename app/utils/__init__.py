import os


def convert_size(text, bits=2):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024
    for i in range(len(units)):
        if (text / size) < 1:
            return f"%.{bits}f%s" % (text, units[i])
        text = text / size


def sanitize_path_component(name, fallback="未知"):
    """清洗外部文本（演员名/标题/番号）作为路径段，去除路径分隔符、空字符与首尾点，防止目录穿越。"""
    text = "" if name is None else str(name)
    text = text.replace("\x00", "").replace("/", "_").replace("\\", "_")
    text = text.replace("\r", " ").replace("\n", " ").strip().strip(".").strip()
    if not text:
        return fallback
    return text


def remove_empty_directory(path: str):
    parent = os.path.abspath(os.path.join(path, '..'))
    if os.path.isdir(path):
        ds_store = os.path.join(path, '.DS_Store')
        if os.path.exists(ds_store):
            os.remove(ds_store)

        children = os.listdir(path)
        if children:
            return
        else:
            os.rmdir(path)
            remove_empty_directory(parent)
    else:
        remove_empty_directory(parent)
