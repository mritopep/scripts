import os
import xml.etree.ElementTree as ET
from shutil import copyfile
import shutil
import numpy as np

from general import make_dir, get_data, store_data, remove_dir, upzip_gz, show_data, list_directory, update_progress, make_archive
from paths import *

def get_metadata(dataset):
    labels={}
    for r, d, f in os.walk(dataset):
          for file in f:
              if file.endswith(".xml") and file.startswith("ADNI"):
                file_path=os.path.join(r, file)
                subId,research_group = get_xml_data(file_path)
                if(subId not in labels.keys()):
                    labels[subId]=research_group
    return labels

def get_xml_data(path):
    tree = ET.parse(path)
    root = tree.getroot()
    subId=root.find("./project/subject/subjectIdentifier").text
    research_group=root.find("./project/subject/researchGroup").text
    return [subId,research_group]


if __name__ == "__main__":
    make_dir(DATA_PATHS)
    make_dir(SCRIPT_PATHS)
    metadata=get_metadata(METADATA_ADNI)
    print(metadata)
    store_data(metadata,"labels.pkl")

