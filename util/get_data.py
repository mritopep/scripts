# imports
import requests
import zipfile
import os
import shutil
import time

# library files
from util.get_link import get_file_ids
from util.general import store_data, get_data, make_dir, remove_dir, show_data, get_assigned, update_progress, download_progress
from util.paths import *


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
            update_progress(count, total_files)


def download(files):
    downloaded_files = []
    print("\nDOWNLOADING FILES\n")
    for fs in files:
        file_id = fs['id']
        file_name = fs['name']
        file_path = f"{DOWNLOAD}/{file_name}"
        print(f'\nName:{file_name}\nPath: {file_path}\n')
        if(not os.path.exists(file_path)):
            download_file(file_id, file_path)
        downloaded_files.append({"name": file_name, "path": file_path})
    return downloaded_files


def extract(downloaded_files):
    print("\nEXTRACTING FILES\n")
    extract_paths = []
    for file in downloaded_files:
        file_name = file['name'][:-4]
        extract_path = f"{EXTRACT}/{file_name}"
        print(f'\nName:{file_name}\nPath: {extract_path}\n')
        if(not os.path.exists(extract_path)):
            extract_file(file['path'], extract_path)
        extract_paths.append(extract_path)
    store_data(extract_paths, f"{PICKLE}/extract_paths.pkl")
    return extract_paths


def get_nii_files(extracted_paths):
    print("\nSELECTING SCANS FILES \n")
    nii_files = []
    for extract_path in extracted_paths:
        for r, d, f in os.walk(extract_path):
            for file in f:
                if file.endswith(".nii"):
                    file_name = file
                    file_path = os.path.join(r, file)
                    nii_files.append({"name": file_name, "path": file_path})
    return nii_files


def get_files(name):
    nii_files = []
    files = get_file_ids(name)
    show_data("ID", files)
    for file in files:
        downloaded_files = download([file])
        extracted_paths = extract(downloaded_files)
    #   print(f"\nREMOVE: {downloaded_files[0]['path']}\n")
    #   os.remove(downloaded_files[0]['path'])
        nii_files.extend(get_nii_files(extracted_paths))
    store_data(nii_files, f"{PICKLE}/nii_files.pkl")
    return nii_files


def get_assigned_files(name):
    assigned_files = get_assigned()
    nii_files = []
    files = get_file_ids(name)
    show_data("ID", files)
    for file in files:
        if(file["name"] not in assigned_files):
            continue
        downloaded_files = download([file])
        extracted_paths = extract(downloaded_files)
    #   print(f"\nREMOVE: {downloaded_files[0]['path']}\n")
    #   os.remove(downloaded_files[0]['path'])
        nii_files.extend(get_nii_files(extracted_paths))
    store_data(nii_files, f"{PICKLE}/nii_files.pkl")
    return nii_files


if __name__ == "__main__":
    print("\nDOWNLOAD DATA\n")
    get_assigned_files("filtered_adni")
