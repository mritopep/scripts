import os
import shutil
from shutil import move
from os import path
import time

from paths import *
from get_data import get_nii
from general import make_dir

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
  loc=f"{ADNI}/{sub_id}/{mod}"
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
  
def get_xml_files(extracted_paths):
    print("\n GETTING XML FILE\n")
    xml_files=[]
    for extract_path in extracted_paths:
      for r, d, f in os.walk(extract_path):
          for file in f:
              if file.endswith(".xml") and file.startswith("ADNI"):
                file_name=file
                file_path=os.path.join(r, file)
                xml_files.append({"name":file_name,"path":file_path})
                print(f'Name:{file_name}\nPath: {file_path}')
    return xml_files

def copy_metadata(files,path):
    for file in files:
        move(file["path"], f"{path}/{file['name']}")

def move_xml():
  files = get_xml_files(EXTRACT)
  copy_metadata(files,METADATA_ADNI)

if __name__ == "__main__":
  move_xml()