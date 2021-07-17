import os
import xml.etree.ElementTree as ET
from datetime import date
from shutil import copyfile
import shutil
import numpy as np
import nibabel

from general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive
from paths import *

def nii_dimension(file):
    data = np.asarray(nibabel.load(file).dataobj).T
    row = data.shape[1]
    col = data.shape[2]
    return [row, col]

def dimension_check(path):
    try:
      dim = nii_dimension(path)
      if(dim[1] >= 192 and dim[1] <= 256):
          return True
    except:
      return False

    return False   

def get_metadata(dataset):
    xml_files={}
    for r, d, f in os.walk(dataset):
          for file in f:
              if file.endswith(".xml") and file.startswith("ADNI"):
                file_path=os.path.join(r, file)
                subId,seriesId,imageId,date = get_xml_data(file_path)
                id=f"S{seriesId}_I{imageId}"
                xml_files[id]={"subId":subId,"date":date}
    return xml_files

def get_xml_data(path):
    tree = ET.parse(path)
    root = tree.getroot()
    subId=root.find("./project/subject/subjectIdentifier").text
    seriesId=root.find("./project/subject/study/series/seriesIdentifier").text
    imageId=root.find("./project/subject/study/imagingProtocol/imageUID").text
    date=root.find("./project/subject/study/series/dateAcquired").text
    return [subId,seriesId,imageId,date]

def get_name(scan_path):
    if(scan_path.find("/PT/")!=-1):
        index=scan_path.find("/PT/")
    index=scan_path.find("/MR/")
    return scan_path[index+4:-4]+".xml"

def get_date(scan_path):
    name=get_name(scan_path)
    for k in metadata.keys():
        if(k in name):
            if(metadata[k]["subId"] in name):
                return metadata[k]["date"]

def get_diff(mri_date,pet_date):
    year,month,day=[int(i) for i in mri_date.split("-")]
    d0 = date(year,month,day)
    year,month,day=[int(i) for i in pet_date.split("-")]
    d1 = date(year,month,day)
    diff = abs(d1 - d0)
    return diff.days

metadata=get_metadata(METADATA_ADNI)

def pair_scan_images(MR,PT):
    print("\nPAIR SCANS\n")
    pair_data=[]
    used_mri=[]

    for pet in PT:
        if(not dimension_check(pet)):
            continue
        for mri in MR:
            if(not dimension_check(mri)):
                continue
            if(mri in used_mri):
                continue
            mri_date=get_date(mri)
            pet_date=get_date(pet)
            diff=get_diff(mri_date,pet_date)
            if((diff/366)<=1):
                print(f'MRI: {mri}\n\nPET: {pet}\n\nDAYS: {diff}\n\n')
                pair_data.append({"mr":mri,"pt":pet})
                used_mri.append(mri)
    return pair_data

def filter(remove_files=False):
    subject_ids=os.listdir(ADNI)
    pair_datas=[]
    for id in subject_ids:

        mri=[]
        pet=[]

        try:
            files = os.listdir(f"{ADNI}/{id}/MR")
        except:
            continue

        for file in files:
            mri.append(f"{ADNI}/{id}/MR/{file}")

        try:
            files = os.listdir(f"{ADNI}/{id}/PT")
        except:
            continue

        for file in files:
            pet.append(f"{ADNI}/{id}/PT/{file}")

        if(len(mri) == 0 or len(pet) == 0):
            shutil.rmtree(f"{ADNI}/{id}")
            continue
        
        pair_data = pair_scan_images(mri,pet)
        pair_datas.extend(pair_data)

        print(f"Subject Id: {id}")
        print(f"PET NUM: {len(pet)}")
        print(f"MRI NUM: {len(mri)}")       
        print(f"PAIR DATA NUM: {len(pair_data)}")

        count=0
        for pair in pair_data:
            count+=1
            loc=f"{FILTERED}/{id}_{count}"
            if(os.path.isdir(loc)==False):
              try:  
                os.makedirs(loc) 
              except OSError as error:  
                  print(error) 
            copyfile(pair["mr"], loc+"/mri.nii")
            copyfile(pair["pt"], loc+"/pet.nii")
        
        if(remove_files):
            shutil.rmtree(f"{ADNI}/{id}")
        
    print(f"PAIR DATAS NUM: {len(pair_datas)}")


if __name__ == "__main__":
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    filter(remove_files=True)
