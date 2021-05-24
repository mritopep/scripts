from zipfile import ZipFile
import os
import shutil
from distutils.dir_util import copy_tree

from paths import *
from general import update_progress, make_dir


def divide(name, path, parts):
    print("\nDIVIDING FILES\n")
    divided_dirs = []
    dirs = []

    dir_list = os.listdir(path)
    num_dir = len(dir_list)
    div = int(num_dir/parts)

    for i in range(1, num_dir+1):
        if(i % div == 0):
            dirs.append(dir_list[i-1])
            divided_dirs.append(dirs)
            dirs = []
        else:
            dirs.append(dir_list[i-1])

    if(dirs not in divided_dirs and len(dirs) != 0):
        divided_dirs.append(dirs)

    dir_count = 0
    file_count = 0
    for divide in divided_dirs:
        dir_count += 1
        for folder in divide:
            file_count += 1

    print(f"\nDIR COUNT:{dir_count} FILE COUNT: {file_count}\n")

    count = 0

    for divide in divided_dirs:
        os.makedirs(f"{DIVIDE}/{name}")
        divided_file_paths = []
        count += 1
        for folder in divide:
            dest_directory = f"{DIVIDE}/{name}/{folder}"
            src_directory = f"{path}/{folder}"
            os.makedirs(dest_directory)
            shutil.copyfile(f"{src_directory}/mri.nii",
                            f"{dest_directory}/mri.nii")
            shutil.copyfile(f"{src_directory}/pet.nii",
                            f"{dest_directory}/pet.nii")
        shutil.make_archive(f"{DIVIDE}/{name}_{count}",
                            'zip', f"{DIVIDE}/{name}")
        shutil.rmtree(f"{DIVIDE}/{name}")
        update_progress(count, file_count)


if __name__ == "__main__":
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    divide("filter", FILTERED, 5)
