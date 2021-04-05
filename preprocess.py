import os
from datetime import date
from shutil import copyfile
import shutil
import pickle
import gzip

# import
from util.get_data import extract, get_nii_files
from util.general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive
from util.paths import *


def image_registration(mri_image, pet_image, output_image):
    print("IMAGE REGISTRATION\n")
    os.system(
        f"bash {SHELL}/img_rgr.sh {mri_image} {pet_image} {output_image} &> null.txt")


def intensity_normalization(input_image, output_image):
    print("DENOISING\n")
    os.system(
        f"bash {SHELL}/denoise.sh {input_image} {output_image} &> null.txt")


def skull_strip(input_image):
    print("SKULL STRIPPING\n")
    os.system(
        f"bash {SHELL}/skull_strip.sh {input_image} {SKULL_STRIP} &> null.txt")


def bias_correction(input_image, output_image):
    print("BIAS CORRECTION\n")
    os.system(f"bash {SHELL}/bias.sh {input_image} {output_image} &> null.txt")


def petpvc(input_image, output_image):
    print("PETPVC\n")
    os.system(
        f"bash {SHELL}/petpvc.sh {input_image} {output_image} &> null.txt")


def preprocess(key, src_name, sub_scan):
    scan = sub_scan[key]

    make_dir([SKULL_STRIP, IMG_REG, DENOISE, PETPVC, BAIS_COR,
             TEMP_OUTPUT, f"{PREPROCESSED}/{src_name}/{key}"])

    mri_path = scan['mri.nii']
    pet_path = scan['pet.nii']

    show_data("path", [mri_path, pet_path])

    image_registration(mri_path, pet_path, f"{IMG_REG}/pet.nii")

    preprocess_mri(mri_path)
    preprocess_pet(f"{IMG_REG}/pet.nii")

    copyfile(f"{TEMP_OUTPUT}mri.nii",
             f"{PREPROCESSED}/{src_name}/{key}/mri.nii")
    copyfile(f"{TEMP_OUTPUT}pet.nii",
             f"{PREPROCESSED}/{src_name}/{key}/pet.nii")

    remove_dir([SKULL_STRIP, IMG_REG, DENOISE, PETPVC,
               BAIS_COR, TEMP_OUTPUT, IMG_REG])


def preprocess_mri(mri_path):
    intensity_normalization(mri_path, f"{DENOISE}/mri")
    skull_strip(f"{DENOISE}/mri.nii")
    upzip_gz(f"{SKULL_STRIP}/mri_masked.nii.gz", f"{SKULL_STRIP}/mri_sk.nii")
    bias_correction(f"{SKULL_STRIP}/mri_sk.nii", f"{TEMP_OUTPUT}/mri.nii")


def preprocess_pet(pet_path):
    skull_strip(pet_path)
    upzip_gz(f"{SKULL_STRIP}/pet_registered_masked.nii.gz",
             f"{SKULL_STRIP}/pet_sk.nii")
    petpvc(f"{SKULL_STRIP}/pet_sk.nii", f"{TEMP_OUTPUT}/pet.nii")


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

    total_files = len(extracted_files)
    count = 0

    for k in sub_scan:
        count += 1
        if(k not in preprocessed_files):
            preprocess(k, src_name, sub_scan)
        update_progress(count, total_files)


def driver_stup():
    sub_scan = {}
    extracted_files = get_nii_files([EXTRACT+"/filtered_adni_4"])
    for i in extracted_files:
        folder = get_folder_name(i['path'])
        if(folder not in sub_scan.keys()):
            sub_scan[folder] = {}
            sub_scan[folder].update({i['name']: i['path']})
        else:
            sub_scan[folder].update({i['name']: i['path']})
    preprocess("002_S_2073_2", "sample", sub_scan)


def stub():
    print("STUB")
    driver_stup()
    src_name = dest_name = "sample"
    print("ZIPPING")
    make_archive(f"{PREPROCESSED}/{src_name}", f"{ZIPPED}/{dest_name}.zip")


def process_data():
    nii_files = []
    downloaded_files = []

    # Downloaded files
    for file_name in os.listdir(DOWNLOAD):
        file_path = DOWNLOAD+"/"+file_name
        downloaded_files.append({"name": file_name, "path": file_path})

    for file in downloaded_files:
        src_name = file['name'][:-4]
        dest_name = src_name.replace("filtered", "preprocessed")
        show_data("name", [src_name, dest_name])

        extracted_paths = extract([file])
        extracted_files = get_nii_files(extracted_paths)

        print("PREPROCESSING")
        driver(extracted_files, src_name)

        print("ZIPPING")
        make_archive(f"{PREPROCESSED}/{src_name}", f"{ZIPPED}/{dest_name}.zip")

        # print("REMOVING")
        # shutil.rmtree(f"{PREPROCESSED}/{src_name}")


if __name__ == "__main__":
    print("PREPROCESSING")
    make_dir([DOWNLOAD, EXTRACT, ADNI, CANCER, METADATA_ADNI,
             METADATA_CANCER, PREPROCESSED, ZIPPED])
    # Testing
    stub()
    # Process
    # process_data()
