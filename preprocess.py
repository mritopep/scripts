import os
from datetime import date
from shutil import copyfile
import shutil
import pickle
import gzip

# import
from get_data import extract, get_nii_files
from general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive, get_assigned
from paths import *


def image_registration(mri_image, pet_image, output_image):
    print("\nIMAGE REGISTRATION\n")
    log_name = "IMAGE_REGISTRATION"
    os.system(
        f"bash {SHELL}/img_rgr.sh {mri_image} {pet_image} {output_image} {log_name}")
    with open(log_name, "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            return False
        return True


def intensity_normalization(input_image, output_image):
    print("\nDENOISING\n")
    log_name = "DENOISING"
    os.system(
        f"bash {SHELL}/denoise.sh {input_image} {output_image} {log_name}")
    with open(log_name, "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            return False
        return True


def skull_strip(input_image):
    print("\nSKULL STRIPPING\n")
    log_name = "SKULL_STRIPPING"
    os.system(
        f"bash {SHELL}/skull_strip.sh {input_image} {SKULL_STRIP} {log_name}")
    scan = input_image.split("/")[-1][:-4]
    upzip_gz(f"{SKULL_STRIP}/{scan}_masked.nii.gz",
             f"{SKULL_STRIP}/{scan}_sk.nii")
    with open(log_name, "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            return False
        return True


def bias_correction(input_image, output_image):
    print("\nBIAS CORRECTION\n")
    log_name = "BIAS_CORRECTION"
    os.system(f"bash {SHELL}/bias.sh {input_image} {output_image} {log_name}")
    with open(log_name, "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            return False
        return True


def petpvc(input_image, output_image):
    print("\nPETPVC\n")
    log_name = "PETPVC"
    os.system(f"bash {SHELL}/petpvc.sh {input_image} {output_image} {log_name}")
    with open(log_name, "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            return False
        return True


def preprocess(key, src_name, sub_scan):
    scan = sub_scan[key]

    make_dir(TEMP_PATHS)

    mri_path = scan['mri.nii']
    pet_path = scan['pet.nii']

    show_data("path", [mri_path, pet_path])

    if (not image_registration(mri_path, pet_path, f"{IMG_REG}/pet.nii")):
        return False

    if(not preprocess_mri(mri_path, intensity_normalization=True, skull_strip=True, bias_correction=True)):
        return False

    if(not preprocess_pet(f"{IMG_REG}/pet.nii", skull_strip=True, petpvc=True)):
        return False

    make_dir([f"{PREPROCESSED}/{src_name}/{key}"])

    copyfile(f"{TEMP_OUTPUT}/mri.nii",
             f"{PREPROCESSED}/{src_name}/{key}/mri.nii")
    copyfile(f"{TEMP_OUTPUT}/pet.nii",
             f"{PREPROCESSED}/{src_name}/{key}/pet.nii")

    remove_dir(TEMP_PATHS)


def preprocess_mri(input, intensity_normalization=True, skull_strip=True, bias_correction=True):
    if(intensity_normalization):
        if(intensity_normalization(input, f"{DENOISE}/mri")):
            input = f"{DENOISE}/mri"
        else:
            return False
    if(skull_strip):
        if(skull_strip(input)):
            input = f"{SKULL_STRIP}/mri_sk.nii"
        else:
            return False
    if(bias_correction):
        if(bias_correction(input, f"{BAIS_COR}/mri.nii")):
            input = f"{BAIS_COR}/mri.nii"
        else:
            return False
    copyfile(input, f"{TEMP_OUTPUT}/mri.nii")
    return True


def preprocess_pet(input, skull_strip=True, petpvc=True):
    if(skull_strip):
        if(skull_strip(input)):
            input = f"{SKULL_STRIP}/pet_sk.nii"
        else:
            return False
    if(petpvc):
        if(petpvc(input, f"{PETPVC}/pet.nii")):
            input = f"{PETPVC}/pet.nii"
        else:
            return False
    copyfile(input, f"{TEMP_OUTPUT}/pet.nii")
    return True


def get_folder_name(path):
    return path.split("/")[-2]


def driver(extracted_files, src_name):
    preprocessed_files = []
    sub_scan = {}

    for i in extracted_files:
        folder = get_folder_name(i['path'])
        if(folder not in sub_scan.keys()):
            sub_scan[folder] = {}
            sub_scan[folder].update({i['name']: i['path']})
        else:
            sub_scan[folder].update({i['name']: i['path']})

    preprocessed_files = list_directory(f"{PREPROCESSED}/{src_name}")

    total_files = len(sub_scan)/2
    count = 0

    for k in sub_scan:
        count += 1
        if(k not in preprocessed_files):
            if(not preprocess(k, src_name, sub_scan)):
                continue
        update_progress(count, total_files)


def driver_stup():
    sub_scan = {}
    file_name = 'filtered_adni_4.zip'
    file_path = f"{DOWNLOAD}/{file_name}"
    file = {"name": file_name, "path": file_path}
    extracted_paths = extract([file])
    extracted_files = get_nii_files(extracted_paths)
    for i in extracted_files:
        folder = get_folder_name(i['path'])
        if(folder not in sub_scan.keys()):
            sub_scan[folder] = {}
            sub_scan[folder].update({i['name']: i['path']})
        else:
            sub_scan[folder].update({i['name']: i['path']})
    if(not preprocess("002_S_2073_2", "sample", sub_scan)):
        exit


def stub():
    print("\nSTUB\n")
    driver_stup()
    src_name = dest_name = "sample"
    print("\nZIPPING\n")
    make_archive(f"{PREPROCESSED}/{src_name}", f"{ZIPPED}/{dest_name}.zip")


def process_data():
    nii_files = []
    downloaded_files = []
    assigned_files = get_assigned()

    # Downloaded files
    for file_name in os.listdir(DOWNLOAD):
        file_path = f"{DOWNLOAD}/{file_name}"
        downloaded_files.append({"name": file_name, "path": file_path})

    for file in downloaded_files:
        if(file["name"] not in assigned_files):
            continue
        src_name = file['name'][:-4]
        dest_name = src_name.replace("filtered", "preprocessed")
        show_data("name", [src_name, dest_name])

        extracted_paths = extract([file])
        extracted_files = get_nii_files(extracted_paths)

        print("\nPREPROCESSING\n")
        driver(extracted_files, src_name)

        print("\nZIPPING\n")
        make_archive(f"{PREPROCESSED}/{src_name}", f"{ZIPPED}/{dest_name}.zip")

        # print("REMOVING")
        # shutil.rmtree(f"{PREPROCESSED}/{src_name}")


if __name__ == "__main__":
    print("\nPREPROCESSING SCRIPT\n")
    # Testing
    # stub()
    # Process
    process_data()
