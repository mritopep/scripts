import numpy as np
import nibabel
import os
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image
from paths import *
import shutil
import imageio

# import
from get_data import extract, get_nii
from general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive, get_assigned
from paths import *


def nii_dimension(file):
    data = np.asarray(nibabel.load(file).dataobj).T
    row = data.shape[1]
    col = data.shape[2]
    return [row, col]


def convert_img(nii_file, output_folder):
    os.system("med2image -i " + nii_file + " -o " + output_folder)


def img_dimension(image):
    im = Image.open(image)
    print(im.size)


def mse(img1, img2):
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img1.shape[1])
    return err


def compare_images(img1, img2):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    _mse = mse(img1, img2)
    _ssim = ssim(img1, img2)
    return [_mse, _ssim]


def extract_images(output_folder):
    files = os.listdir(output_folder)
    length = len(files)
    mid_img = files[length/2]
    upper_img = files[:(length/2)][length/4]
    lower_img = files[(length/2):][length/4]
    return [upper_img, mid_img, lower_img]


def adjust_gamma(image, gamma=0.15):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def nii_jpg(inputfile, outputfile):
    image_array = nibabel.load(inputfile).get_fdata()
    total_slices = image_array.shape[2]
    mid_slice = total_slices//2
    data = image_array[:, :, mid_slice]
    image_name = "slice.jpg"
    imageio.imwrite(image_name, data)
    src = image_name
    shutil.move(src, outputfile)
    print("Slice Saved")

def dimension_check(path, type):
    mri_dim = nii_dimension(path)
    if(mri_dim[1] >= 192 and mri_dim[1] <= 256):
        return True
    return False

def structural_similarity(path, type):
    nii_jpg(path, f"{SSIM}/{type}")
    files = [f for f in os.listdir(MRI_SLICE) if os.path.isfile(os.path.join(MRI_SLICE, f))]
    total_mse = 0
    total_ssim = 0
    for file in files:
        mse,ssim = compare_images(file, f"{SSIM}/{type}/slice.jpg")
        total_mse += mse
        total_ssim += ssim
    mean_mse = total_mse//36
    mean_ssim = total_ssim//36
    print(f"Mean SSIM: {mean_ssim} Mean MSE: {mean_mse}")
    return True

def get_folder_name(path):
    return path.split("/")[-2]


def postprocess(path, type, Dimension_Check=True, Feature_Selection=True, Structural_Similarity=True):
    print("\n-------------------POSTPROCESS STARTED--------------------\n")
    if(Dimension_Check):
        return dimension_check(path, type)
    if(Structural_Similarity):
        return structural_similarity(path, type)
    if(Feature_Selection):
        return feature_selection(path, type)
    print("\n-------------------POSTPROCESS COMPELETED--------------------\n")
    return True


def postprocess(key, sub_scan):
    scan = sub_scan[key]
    mri_path = scan['mri.nii']
    pet_path = scan['pet.nii']

    make_dir(POSTPROCESS_TEMP_PATHS)

    show_data("path", [mri_path, pet_path])

    # Pipeline Configuration
    Dimension_Check = True
    Feature_Selection = True
    Structural_Similarity = True

    if(not postprocess(mri_path, "mri", Dimension_Check=Dimension_Check, Feature_Selection=Feature_Selection, Structural_Similarity=Structural_Similarity)):
        return False

    if(not postprocess(pet_path, "pet", Dimension_Check=Dimension_Check, Feature_Selection=Feature_Selection, Structural_Similarity=Structural_Similarity)):
        return False

    make_dir([f"{POSTPROCESS}/{key}"])

    shutil.copyfile(mri_path, f"{POSTPROCESS}/{key}/mri.nii")
    shutil.copyfile(pet_path, f"{POSTPROCESS}/{key}/pet.nii")

    remove_dir(POSTPROCESS_TEMP_PATHS)


def driver(extracted_files, src_name):
    postprocessed_files = []
    sub_scan = {}

    for i in extracted_files:
        folder = get_folder_name(i['path'])
        if(folder not in sub_scan.keys()):
            sub_scan[folder] = {}
            sub_scan[folder].update({i['name']: i['path']})
        else:
            sub_scan[folder].update({i['name']: i['path']})

    postprocessed_files = list_directory(f"{POSTPROCESS}")

    total_files = len(sub_scan)
    count = 0

    print("\n"+"-"*25+"PROGRESS"+"-"*25+"\n")
    update_progress(count, total_files)
    print("\n"+"-"*58+"\n")

    for k in sub_scan:
        count += 1
        if(k not in postprocessed_files):
            if(not postprocess(k, sub_scan)):
                continue
        print("\n"+"-"*25+"PROGRESS"+"-"*25+"\n")
        update_progress(count, total_files)
        print("\n"+"-"*58+"\n")


def post_preprocess():
    nii_files = []
    downloaded_files = []
    # Downloaded files
    for file_name in os.listdir(DOWNLOAD):
        file_path = f"{DOWNLOAD}/{file_name}"
        downloaded_files.append({"name": file_name, "path": file_path})

    for file in downloaded_files:
        src_name = file['name'][:-4]
        dest_name = src_name.replace("filtered", "preprocessed")

        if(f"{dest_name}.zip" in os.listdir(ZIPPED)):
            continue

        show_data("name", [src_name, dest_name])

        extracted_paths = extract([file])
        extracted_files = get_nii(extracted_paths)

        print(f"\n{src_name.upper()} PREPROCESSING\n")
        driver(extracted_files, src_name)

        print(f"\n{src_name.upper()} ZIPPING\n")
        make_archive(f"{POSTPROCESS}", f"{ZIPPED}/{dest_name}.zip")

    print("REMOVING")
    shutil.rmtree(f"{POSTPROCESS}")


if __name__ == "__main__":
    post_preprocess()
