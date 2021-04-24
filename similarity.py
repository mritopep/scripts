from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image 

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





 

