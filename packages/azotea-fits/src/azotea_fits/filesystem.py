# ----------------------------------------------------------------------
# Copyright (c) 2026 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------
# ----------------
# Standard library
# ----------------
import hashlib
import os
from collections.abc import Iterable
from pathlib import Path


def scan_non_empty_dirs(root_dir: str, depth: int | None = None):
    if os.path.basename(root_dir) == "":
        root_dir = root_dir[:-1]
    dirs = {dirpath for dirpath, dirs, files in os.walk(root_dir) if files}
    dirs.add(root_dir)  # Add it for images just under the root_dir folder
    if depth is None:
        return list(dirs)
    L = len(root_dir.split(sep=os.sep))
    return list(filter(lambda d: len(d.split(sep=os.sep)) - L <= depth, dirs))


def scan_images(
    root_dir: str,
    depth: int,
    extensions: Iterable[str],
) -> list[str]:
    """
    Return absolute paths of images below root_dir, up to depth levels.
    depth = 0 means only files directly inside root_dir.
    depth = 1 includes root_dir and its immediate subdirectories.
    """
    root = Path(root_dir).resolve()
    root_depth = len(root.parts)
    extensions = tuple(ext.lower() for ext in extensions)
    images = []

    for dir_path, _dir_names, file_names in os.walk(root):
        current = Path(dir_path)
        current_depth = len(current.parts) - root_depth
        if current_depth > depth:
            # Avoid descending into directories beyond the requested depth.
            _dir_names[:] = []
            continue
        for file_name in file_names:
            suffix = Path(file_name).suffix.lower()
            if suffix in extensions:
                images.append(str(current / file_name))
    return sorted(images)


def hash_func(path: str) -> bytes:
    """Compute a hash from the image"""
    BLOCK_SIZE = 1048576
    # 1MByte, the size of each read from the file
    # md5() was the fastest algorithm I've tried
    # but I'm using blake2b with twice the digest size for compatibility
    # with the old AZOTEA software
    file_hash = hashlib.blake2b(digest_size=32)
    with open(path, "rb") as f:
        block = f.read(BLOCK_SIZE)
        while len(block) > 0:
            file_hash.update(block)
            block = f.read(BLOCK_SIZE)
    return file_hash.digest()
