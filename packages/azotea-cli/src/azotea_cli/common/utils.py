import os

def scan_non_empty_dirs(root_dir: str, depth: int | None =None):
    if os.path.basename(root_dir) == '':
        root_dir = root_dir[:-1]
    dirs = set(dirpath for dirpath, dirs, files in os.walk(root_dir) if files)
    dirs.add(root_dir)   # Add it for images just under the root_dir folder
    if depth is None:
        return list(dirs)
    L = len(root_dir.split(sep=os.sep))
    return list(filter(lambda d: len(d.split(sep=os.sep)) - L <= depth, dirs))
