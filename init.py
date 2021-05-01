import os
import shutil
import pickle

from general import make_dir, get_data, store_data, remove_dir, cred_store
from paths import *

def init():
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    cred_store()
    
if __name__ == "__main__":
    init()
    
    
    
