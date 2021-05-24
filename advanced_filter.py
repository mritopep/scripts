import numpy as np
import pandas as pd
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
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.models import Sequential

# import
from get_data import extract, get_nii
from general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive, get_assigned
from paths import *

print("loading model")
model = VGG16(weights="imagenet", include_top=True)
# eliminating the last layer of VGG16- 4096 features
cust_model = Sequential()
for layer in model.layers[:-1]:  # excluding last layer
    cust_model.add(layer)

df = pd.DataFrame(columns=['subject_id', 'type', 'mse', 'ssim', 'distance'])

MEAN_SSIM = 0
MEAN_MSE = 0
MEAN_DIST = 0


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


def get_image_features(image_file_name):
    image = load_img(image_file_name, target_size=(224, 224))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    features = cust_model.predict(image)
    return features


def adjust_gamma(image, gamma=0.15):
    gamma = 0.15
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    image = cv2.LUT(image, table).astype(np.uint8)
    return image


def nii_jpg(inputfile, outputfile, type):
    print("Saving slice")
    print(inputfile, outputfile, type)
    image_array = nibabel.load(inputfile).get_fdata()
    total_slices = image_array.shape[2]
    mid_slice = total_slices//2
    data = image_array[:, :, mid_slice]
    image_name = f"{type}.jpg"
    imageio.imwrite(image_name, data)
    if(type == 'mri'):
        img = cv2.imread(image_name, 0)
        img = adjust_gamma(img)
        cv2.imwrite(image_name, img)
    src = image_name
    try:
        os.remove(outputfile+"/"+image_name)
    except:
        pass
    shutil.move(src, outputfile)
    print("Slice Saved")


def dimension_check(path, type):
    # print("\nDIMENSION CHECK\n")
    dim = nii_dimension(path)
    if(dim[1] >= 192 and dim[1] <= 256):
        return True
    return False


def structural_similarity(path, type):
    # print("\nSTRUCTURAL SIMILARITY\n")
    if type == "mri":
        slice_path = MRI_SLICE
    else:
        slice_path = PET_SLICE
    nii_jpg(path, SSIM, type)
    # total_mse = 0
    # total_ssim = 0
    # count = 0
    # for file in os.listdir(slice_path):
    #     count += 1
    #     path = os.path.join(slice_path, file)
    #     img1 = cv2.imread(path)
    #     img1 = cv2.resize(img1, (256, 256), interpolation=cv2.INTER_NEAREST)
    #     img2 = cv2.imread(f"{SSIM}/{type}.jpg")
    #     img2 = cv2.resize(img2, (256, 256), interpolation=cv2.INTER_NEAREST)
    #     mse, ssim = compare_images(img1, img2)
    #     total_mse += mse
    #     total_ssim += ssim
    # mean_mse = total_mse//count
    # mean_ssim = total_ssim//(count/100)
    # global MEAN_MSE, MEAN_SSIM
    # MEAN_MSE = mean_mse
    # MEAN_SSIM = mean_ssim
    return True


def feature_selection(path, type):
    # print("\nFEATURE SELECTION\n")
    threshold_mri = 55
    threshold_pet = 45
    if type == "mri":
        slice_path = MRI_SLICE
    else:
        slice_path = PET_SLICE
    print(slice_path)
    test_image = get_image_features(path)
    total_distance = 0
    count = 0
    for file in os.listdir(slice_path):
        count += 1
        path = os.path.join(slice_path, file)
        base_image = get_image_features(path)
        dist = np.linalg.norm(base_image-test_image)
        total_distance += dist
    mean_distance = total_distance//count
    global MEAN_DIST
    MEAN_DIST = mean_distance
    if type == "mri":
        if (mean_distance < threshold_mri ) : return True
    else:
        if (mean_distance < threshold_pet ) : return True
    return False


def get_folder_name(path):
    return path.split("/")[-2]


def postprocess_file(subject_id, path, type, Dimension_Check=True, Feature_Selection=True, Structural_Similarity=True):
    print(
        f"\n------------------- {type.upper()} POSTPROCESS STARTED--------------------\n")
    if(Dimension_Check):
        if(not dimension_check(path, type)):
            return False
    if(Structural_Similarity):
        if(not structural_similarity(path, type)):
            return False
    if(Feature_Selection):
        if(not feature_selection(f"{SSIM}/{type}.jpg", type)):
            return False

    global MEAN_MSE, MEAN_SSIM, MEAN_DIST
    print(
        f'\nsubject_id : {subject_id} mse: {MEAN_MSE} ssim : {MEAN_SSIM} distance : {MEAN_DIST}\n')
    global df
    df = df.append({'subject_id': subject_id, 'type': type, 'mse': MEAN_MSE, 'ssim': MEAN_SSIM,
                    'distance': MEAN_DIST}, ignore_index=True)

    print(
        f"\n------------------- {type.upper()} POSTPROCESS COMPELETED--------------------\n")

    return True


def postprocess(key, src_name, sub_scan):
    scan = sub_scan[key]
    mri_path = scan['mri.nii']
    pet_path = scan['pet.nii']

    make_dir(POSTPROCESS_TEMP_PATHS)

    show_data("path", [key, mri_path, pet_path])

    # Pipeline Configuration
    Dimension_Check = True
    Feature_Selection = True
    Structural_Similarity = True

    if(not postprocess_file(key, mri_path, "mri", Dimension_Check=Dimension_Check, Feature_Selection=Feature_Selection, Structural_Similarity=Structural_Similarity)):
        return False

    if(not postprocess_file(key, pet_path, "pet", Dimension_Check=Dimension_Check, Feature_Selection=Feature_Selection, Structural_Similarity=Structural_Similarity)):
        return False

    make_dir([f"{POSTPROCESS}/{src_name}/{key}"])
    make_dir([f"{POSTPROCESS}/{src_name}/{key}/img"])

    print("COPYING FILES")

    shutil.copyfile(mri_path, f"{POSTPROCESS}/{src_name}/{key}/mri.nii")
    shutil.copyfile(pet_path, f"{POSTPROCESS}/{src_name}/{key}/pet.nii")
    shutil.copyfile(f"{SSIM}/mri.jpg",
                    f"{POSTPROCESS}/{src_name}/{key}/img/mri.jpg")
    shutil.copyfile(f"{SSIM}/pet.jpg",
                    f"{POSTPROCESS}/{src_name}/{key}/img/pet.jpg")

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

    postprocessed_files = list_directory(f"{POSTPROCESS}/{src_name}")

    total_files = len(sub_scan)
    count = 0

    print("\n"+"-"*25+"PROGRESS"+"-"*25+"\n")
    update_progress(count, total_files)
    print("\n"+"-"*58+"\n")

    for k in sub_scan:
        count += 1
        if(k not in postprocessed_files):
            if(not postprocess(k, src_name, sub_scan)):
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
        dest_name = src_name.replace("preprocessed", "postprocessed")
        
        if(f"{dest_name}.zip" in os.listdir(POST_ZIPPED)):
            continue

        show_data("name", [src_name, dest_name])

        extracted_paths = extract([file])
        extracted_files = get_nii(extracted_paths)

        print(f"\n{src_name.upper()} PREPROCESSING\n")
        driver(extracted_files, dest_name)

        global df
        df.to_csv(f"{POSTPROCESS}/{dest_name}/postprocess.csv")
        df = pd.DataFrame(columns=['subject_id', 'type', 'mse', 'ssim', 'distance'])

        print(f"\n{src_name.upper()} ZIPPING\n")
        make_archive(f"{POSTPROCESS}/{dest_name}", f"{POST_ZIPPED}/{dest_name}.zip")

    # print("REMOVING")
    # shutil.rmtree(f"{POSTPROCESS}")

if __name__ == "__main__":
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    df = pd.DataFrame(columns=['subject_id', 'type', 'mse', 'ssim', 'distance'])
    post_preprocess()
