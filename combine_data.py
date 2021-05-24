import os
import shutil
from shutil import move
from os import path
import time

from get_data import get_nii

def get_id_and_mod(name):
  mod=""
  if(name.find('_P') !=-1):
    mod="PT"
    id_index=name.find('_P') 
  if(name.find('_M') !=-1):
    mod="MR"
    id_index=name.find('_M')
  sub_id=name[5:id_index]
  return [sub_id,mod]

def make_dir(file_data):
  sub_id,mod=get_id_and_mod(file_data["name"])
  loc=ADNI+sub_id+"/"+mod
  if(path.isdir(loc)==False):
    try:  
      os.makedirs(loc) 
    except OSError as error:  
        print(error) 
  move(file_data["path"], loc+"/"+file_data["name"])
  print(f"File Name: {file_data['name']}\n Loc: {loc}/{file_data['name']}")

def make_struct():
    print("MAKING STRUCTRE")
    files = get_nii(EXTRACT)
    for file in files:
        make_dir(file)
  

if __name__ == "__main__":
  make_struct()