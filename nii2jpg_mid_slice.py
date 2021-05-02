# -*- coding: utf-8 -*-
import scipy
import numpy
import shutil
import os
import nibabel
import imageio
import sys
import getopt

def nii_jpg(inputfile, subid, outputfile, name):
    image_array = nibabel.load(inputfile).get_fdata()
    if len(image_array.shape) == 4:
        nx, ny, nz, nw = image_array.shape
        total_volumes = image_array.shape[3]
        total_slices = image_array.shape[2]
        for current_volume in range(0, total_volumes):
            mid_slice = total_slices//2
            data = image_array[:, :, mid_slice, current_volume]
            image_name = f"{subid}_{name}.jpg"
            imageio.imwrite(image_name, data)
            print('Saved.')
            src = image_name
            shutil.move(src, outputfile)
            print(image_name, 'Saved.', image_array.shape, "mid :", mid_slice)
    else:
        print("-------------->  Not shape 4")
        print(inputfile)
    del image_array
    del data


def generate_jpg(input_folder,output_folder):
    data_dir_list = os.listdir(input_folder)
    print(len(data_dir_list))
    mri = 'mri.nii'
    pet = 'pet.nii'
    sub_count = 0
    for sub in data_dir_list:
        mri_path = os.path.join(input_folder, sub, mri)
        outputfile = os.path.join(output_folder, "adni_MRI")
        nii_jpg(mri_path, sub_count, outputfile, "mri")

        pet_path = os.path.join(input_folder, sub, pet)
        outputfile = os.path.join(output_folder, "adni_PET")
        nii_jpg(pet_path, sub_count, outputfile, "pet")

        sub_count += 1
    print('--> Completed')
