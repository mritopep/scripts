import os

PWD = str(os.path.dirname(os.path.abspath(__file__)))
DATA = PWD.replace("/scripts", "/data")
SCRIPT = PWD.replace("/scripts", "/scripts")
TOKEN = PWD.replace("/scripts", "/tokens")

# Locations
DOWNLOAD = f'{DATA}/downloads'
ADNI = f'{DATA}/dataset/adni'
CANCER = f'{DATA}/dataset/cancer'
EXTRACT = f'{DATA}/extracts'
METADATA_ADNI = f'{DATA}/metadata/adni'
METADATA_CANCER = f'{DATA}/metadata/cancer'
DIVIDE = f'{DATA}/parts'
PREPROCESSED = f'{DATA}/preprocessed_data'
ZIPPED = f'{DATA}/zip_data'
PICKLE = f'{DATA}/pickle'
POSTPROCESS = f'{DATA}/postprocess'

# Temp
SKULL_STRIP = f'{DATA}/temp/skull_strip'
IMG_REG = f'{DATA}/temp/img_reg'
DENOISE = f'{DATA}/temp/denoise'
PETPVC = f'{DATA}/temp/petpvc'
BAIS_COR = f'{DATA}/temp/bias_cor'
TEMP_OUTPUT = f'{DATA}/temp/output'

# Postprocess Temp
SSIM = f'{DATA}/temp/ssim'
FEATURE = f'{DATA}/temp/feature_selection'
MRI_SLICE = "/content/drive/MyDrive/slice/adni_MRI"
PET_SLICE = "/content/drive/MyDrive/slice/adni_PET"

# Shell Scripts
SHELL = f"{SCRIPT}/shell_scripts"

# Full paths
DATA_PATHS = [DOWNLOAD, ADNI, CANCER, EXTRACT, METADATA_ADNI,
              METADATA_CANCER, DIVIDE, PREPROCESSED, ZIPPED, PICKLE]
TEMP_PATHS = [SKULL_STRIP, IMG_REG, DENOISE, PETPVC, BAIS_COR, TEMP_OUTPUT]
SCRIPT_PATHS = []
POSTPROCESS_TEMP_PATHS = [SSIM, FEATURE]
