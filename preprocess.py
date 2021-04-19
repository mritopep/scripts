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

def exception_handle(log_name):
    with open(f"./logs/{log_name}", "r") as log:
        status = log.read().strip()
        if(status == "failed"):
            print(f"\n{log_name} FAILED\n")
            return False
        print(f"\n{log_name} PASSED\n")
        return True

def image_registration(mri_image, pet_image, output_image):
    print("\nIMAGE REGISTRATION\n")
    log_name = "IMAGE_REGISTRATION"
    os.system(
        f"bash {SHELL}/img_rgr.sh {mri_image} {pet_image} {output_image} {log_name}")
    exception_handle(log_name)


def intensity_normalization(input_image, output_image):
    print("\nDENOISING\n")
    log_name = "DENOISING"
    os.system(
        f"bash {SHELL}/denoise.sh {input_image} {output_image} {log_name}")
    exception_handle(log_name)


def skull_strip(input_image):
    print("\nSKULL STRIPPING\n")
    log_name = "SKULL_STRIPPING"
    os.system(
        f"bash {SHELL}/skull_strip.sh {input_image} {SKULL_STRIP} {log_name}")
    scan = input_image.split("/")[-1][:-4]
    upzip_gz(f"{SKULL_STRIP}/{scan}_masked.nii.gz",
             f"{SKULL_STRIP}/{scan}_sk.nii")
    exception_handle(log_name)


def bias_correction(input_image, output_image):
    print("\nBIAS CORRECTION\n")
    log_name = "BIAS_CORRECTION"
    os.system(f"bash {SHELL}/bias.sh {input_image} {output_image} {log_name}")
    exception_handle(log_name)


def petpvc(input_image, output_image):
    print("\nPETPVC\n")
    log_name = "PETPVC"
    os.system(
        f"bash {SHELL}/petpvc.sh {input_image} {output_image} {log_name}")
    exception_handle(log_name)
    
def preprocess(key, src_name, sub_scan):
    scan = sub_scan[key]

    make_dir(TEMP_PATHS)

    mri_path = scan['mri.nii']
    pet_path = scan['pet.nii']

    show_data("path", [mri_path, pet_path])

    if (not image_registration(mri_path, pet_path, f"{IMG_REG}/pet.nii")):
        return False

    if(not preprocess_mri(mri_path, Intensity_Normalization=True, Skull_Strip=True, Bias_Correction=True)):
        return False

    if(not preprocess_pet(f"{IMG_REG}/pet.nii", Skull_Strip=True, Petpvc=True)):
        return False

    make_dir([f"{PREPROCESSED}/{src_name}/{key}"])

    copyfile(f"{TEMP_OUTPUT}/mri.nii",
             f"{PREPROCESSED}/{src_name}/{key}/mri.nii")
    copyfile(f"{TEMP_OUTPUT}/pet.nii",
             f"{PREPROCESSED}/{src_name}/{key}/pet.nii")

    remove_dir(TEMP_PATHS)


def preprocess_mri(input, Intensity_Normalization=True, Skull_Strip=True, Bias_Correction=True):
    print("\n-------------------MRI PREPROCESS STARTED--------------------\n")
    if(Intensity_Normalization):
        if(intensity_normalization(input, f"{DENOISE}/mri")):
            input = f"{DENOISE}/mri.nii"
        else:
            return False
    if(Skull_Strip):
        if(skull_strip(input)):
            input = f"{SKULL_STRIP}/mri_sk.nii"
        else:
            return False
    if(Bias_Correction):
        if(bias_correction(input, f"{BAIS_COR}/mri.nii")):
            input = f"{BAIS_COR}/mri.nii"
        else:
            return False
    copyfile(input, f"{TEMP_OUTPUT}/mri.nii")
    print("\n-------------------MRI PREPROCESS COMPELETED--------------------\n")
    return True


def preprocess_pet(input, Skull_Strip=True, Petpvc=True):
    print("\n--------------------PET PREPROCESS STARTED--------------------\n")
    if(Skull_Strip):
        if(skull_strip(input)):
            input = f"{SKULL_STRIP}/pet_sk.nii"
        else:
            return False
    if(Petpvc):
        if(petpvc(input, f"{PETPVC}/pet.nii")):
            input = f"{PETPVC}/pet.nii"
        else:
            return False
    copyfile(input, f"{TEMP_OUTPUT}/pet.nii")
    print("\n--------------------PET PREPROCESS COMPELETED--------------------\n")
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
        print("\n--------------PROGRESS---------------\n")
        update_progress(count, total_files)
        print("\n-------------------------------------\n")


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

        print(f"\n{src_name.upper()} PREPROCESSING\n")
        driver(extracted_files, src_name)

        print(f"\n{src_name.upper()} ZIPPING\n")
        make_archive(f"{PREPROCESSED}/{src_name}", f"{ZIPPED}/{dest_name}.zip")

        # print("REMOVING")
        # shutil.rmtree(f"{PREPROCESSED}/{src_name}")


if __name__ == "__main__":
    print("\nPREPROCESSING SCRIPT\n")
    # Testing
    # stub()
    # Process
    process_data()
