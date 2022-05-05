import os
import sys
import pathlib

def up_one_directory(path):
    """Move file in path up one directory"""
    p = pathlib.Path(path).absolute()
    parent_dir = p.parents[1]
    newPath = parent_dir / p.name
    if os.path.exists(newPath):
        p.unlink()
    else:
        p.rename(newPath)


if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) == 2:
        folderPath = sys.argv[1]
        if os.path.isdir(folderPath):
            topLevelFolder = pathlib.Path(folderPath)
            for root, dirs, files in os.walk(folderPath, topdown=False):
                rootFolder = pathlib.Path(root)
                if rootFolder.parent.parent == topLevelFolder:
                    for file in files:
                        up_one_directory(rootFolder / file)
                    rootFolder.rmdir()