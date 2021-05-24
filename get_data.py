# imports
import requests
import zipfile
import os
import shutil
import time

# library files
from get_link import get_file_ids
from general import store_data, get_data, make_dir, remove_dir, show_data, update_progress, download_progress, extract_progress
from paths import *


def download_file(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def save_response_content(response, destination):
    print("PROGRESS BAR COMPARED TO 1GB MAY NOT BE ACURATE")
    CHUNK_SIZE = 32768
    count = 0
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                count += CHUNK_SIZE
                f.write(chunk)
                download_progress(count)


def extract_file(source, destination):
    with zipfile.ZipFile(source, 'r') as zip_ref:
        files = zip_ref.infolist()
        total_files = len(files)
        count = 0
        for file in files:
            count += 1
            try:
                zip_ref.extract(file, path=destination)
            except:
                print(f"\nBAD FILE: {file.filename}\n")
            extract_progress(count, total_files)


def download(file):
    print("\nDOWNLOADING FILE\n")
    file_id = file['id']
    file_name = file['name']
    file_path = f"{DOWNLOAD}/{file_name}"
    print(f'\nName:{file_name}\nPath: {file_path}\n')
    if(not os.path.exists(file_path)):
        download_file(file_id, file_path)
    return file_name


def extract(file_name):
    print("\nEXTRACTING FILE\n")
    file_name_without_ext = file_name[:-4]
    download_path = f"{DOWNLOAD}/{file_name}"
    extract_path = f"{EXTRACT}/{file_name_without_ext}"
    print(f'\nName:{file_name_without_ext}\nPath: {extract_path}\n')
    if(not os.path.exists(extract_path)):
        extract_file(download_path, extract_path)
    return extract_path


def get_nii(extract_path):
    print("\nSELECTING SCANS FILES \n")
    nii_files = []
    for r, d, f in os.walk(extract_path):
        for file in f:
            if file.endswith(".nii"):
                file_name = file
                file_path = os.path.join(r, file)
                nii_files.append({"name": file_name, "path": file_path})
    return nii_files


def fetch_files(name,assigned_files=[],store_nii_metadata=False, remove_files=False):
    files_assigned=False
    if(len(assigned_files)!=0):
        files_assigned=True
    nii_files = []
    files = get_file_ids(name)
    for file in files:
        if(files_assigned):
            if(file["name"] not in assigned_files):
                continue
        file_name = download(file)
        extract_path = extract(file_name)
        if(remove_files):
            download_path = f"{DOWNLOAD}/{file_name}"
            print(f"\nREMOVE: {download_path}\n")
            os.remove(download_path)
        if(store_nii_metadata):
            nii_files.extend(get_nii(extract_path))
    store_data(nii_files, f"{PICKLE}/nii_files.pkl")
    return extract_path

if __name__ == "__main__":
    print("\nDOWNLOAD DATA\n")
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    fetch_files("postprocessed_adni")
