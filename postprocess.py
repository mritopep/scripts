import numpy as np
import nibabel
import os
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image 
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
  print (im.size) 

def mse(img1, img2):	
	err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
	err /= float(img1.shape[0] * img1.shape[1])
	return err
	
def compare_images(img1,img2, title):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    _mse = mse(img1, img2)
    _ssim = ssim(img1, img2)
    return [_mse,_ssim]

def extract_images(output_folder):
    files = os.listdir(output_folder)
    length = len(files)
    mid_img = files[length/2]
    upper_img = files[:(length/2)][length/4]
    lower_img = files[(length/2):][length/4]
    return [upper_img,mid_img,lower_img]

def adjust_gamma(image, gamma=0.15):
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	return cv2.LUT(image, table)

def post_preprocess():
    files = os.listdir(f"{EXTRACT}")



if __name__ == "__main__":
    post_preprocess()


