import os

DATA_PWD = str(os.path.dirname(os.path.abspath(__file__))).replace("/scripts","/data")
SCRIPT_PWD = str(os.path.dirname(os.path.abspath(__file__)))

# Locations
DOWNLOAD=f'{DATA_PWD}/downloads'
ADNI=f'{DATA_PWD}/dataset/adni'
CANCER=f'{DATA_PWD}/dataset/cancer'
EXTRACT=f'{DATA_PWD}/extracts'
METADATA_ADNI=f'{DATA_PWD}/metadata/adni'
METADATA_CANCER=f'{DATA_PWD}/metadata/cancer'
DIVIDE=f'{DATA_PWD}/parts'
PREPROCESSED=f'{DATA_PWD}/preprocessed_data'
ZIPPED=f'{DATA_PWD}/zip_data' 
PICKLE=f'{DATA_PWD}/pickle'  


# Temp
SKULL_STRIP=f'{DATA_PWD}/temp/skull_strip'
IMG_REG=f'{DATA_PWD}/temp/img_reg'
DENOISE=f'{DATA_PWD}/temp/denoise'
PETPVC=f'{DATA_PWD}/temp/petpvc'
BAIS_COR=f'{DATA_PWD}/temp/bias_cor'
TEMP_OUTPUT=f'{DATA_PWD}/temp/output'
IMG_REG=f'{DATA_PWD}/temp/img_reg'

# Shell Scripts
SHELL = f"{SCRIPT_PWD}/shell_scripts"