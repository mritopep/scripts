import os

PWD = str(os.path.dirname(os.path.abspath(__file__)))
DATA = PWD.replace("/scripts/util","/data")
SCRIPT = PWD.replace("/scripts/util","/scripts")
TOKEN = PWD.replace("/scripts/util","/tokens")

# Locations
DOWNLOAD=f'{DATA}/downloads'
ADNI=f'{DATA}/dataset/adni'
CANCER=f'{DATA}/dataset/cancer'
EXTRACT=f'{DATA}/extracts'
METADATA_ADNI=f'{DATA}/metadata/adni'
METADATA_CANCER=f'{DATA}/metadata/cancer'
DIVIDE=f'{DATA}/parts'
PREPROCESSED=f'{DATA}/preprocessed_data'
ZIPPED=f'{DATA}/zip_data' 
PICKLE=f'{DATA}/pickle'  


# Temp
SKULL_STRIP=f'{DATA}/temp/skull_strip'
IMG_REG=f'{DATA}/temp/img_reg'
DENOISE=f'{DATA}/temp/denoise'
PETPVC=f'{DATA}/temp/petpvc'
BAIS_COR=f'{DATA}/temp/bias_cor'
TEMP_OUTPUT=f'{DATA}/temp/output'

# Shell Scripts
SHELL = f"{SCRIPT}/shell_scripts"