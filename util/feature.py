import os
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.models import Sequential

print("loading model")
model = VGG16(weights="imagenet", include_top=True)

#eliminating the last layer of VGG16- 4096 features
cust_model = Sequential()
for layer in model.layers[:-1]: #excluding last layer
    cust_model.add(layer)

# read annotation file
data = pd.read_csv('annotations_2.csv',usecols=['img_names', 'labels', 'class_names'])

# Feature extraction 
def get_image_features(image_file_name):
    
    image = load_img(image_file_name, target_size=(224, 224))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    features = cust_model.predict(image)    
    return features
#(num_data,features_size)

image_features_list=[]
count=0
for img in tqdm(data.img_names):
    image_features=get_image_features(img)
    image_features_list.append(image_features)

image_features_arr=np.asarray(image_features_list)
print(image_features_arr.shape)
del image_features_list 
#freeing space

image_features_arr = np.rollaxis(image_features_arr,1,0)
image_features_arr = image_features_arr[0,:,:]
print(image_features_arr.shape)

pickle.dump(image_features_arr, open('feature_vectors.pkl', 'wb'))
np.savetxt('feature_vectors.txt',image_features_arr)

#feature_vectors = np.loadtxt('feature_vectors_400_samples.txt')
# (num_data,features_size)