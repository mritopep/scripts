import os
import shutil
import pickle

from util.general import make_dir, get_data, store_data, remove_dir
from util.paths import *

if __name__ == "__main__":
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
