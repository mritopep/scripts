import os
import pickle
import gzip
import shutil

from paths import *


def upzip_gz(input, output):
    with gzip.open(input, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def store_data(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def get_data(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def make_dir(dirs):
    for dir in dirs:
        try:
            os.makedirs(dir)
        except:
            pass


def remove_dir(dirs):
    for dir in dirs:
        try:
            os.removedirs(dir)
        except:
            pass


def update_progress(curr_count, total_count):
    progress = int((curr_count/total_count)*100)
    bar = int(progress/2)
    print(f"\r[{'#'*bar}] {progress}%", end="\r")


def download_progress(curr_byte):
    gb_data = 1024*1024*1024
    progress = int((curr_byte/gb_data)*100)
    bar = int(progress/2)
    print(f"\r[{'#'*bar}] {progress}%", end="\r")


def lock(data, val):
    if val:
        return data[:2]
    else:
        return data


def show_data(tag, data):
    for num, data in enumerate(data):
        print(f"\n{tag}:{num} - {data}\n")


def list_directory(dir):
    try:
        return os.listdir(dir)
    except:
        print("\nNO DIR\n")
        return []


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


def cred_store():
    print("\nMENU\n0.Whole Dataset\n1.Antony\n2.George\n3.Ashia\n4.Harishma\n")
    n = input("Please Enter your number:")
    store_data(n, f"{PICKLE}/cred.pkl")


def get_assigned():
    cred = 0
    cred = get_data(f"{PICKLE}/cred.pkl")
    if(cred == "1"):
        return ["filtered_adni_1.zip", "filtered_adni_2.zip"]
    elif(cred == "2"):
        return ["filtered_adni_3.zip", "filtered_adni_5.zip", "filtered_adni_6.zip"]
    elif(cred == "4"):
        return ["filtered_adni_7.zip", "filtered_adni_8.zip", "filtered_adni_9.zip"]
    elif(cred == "3"):
        return ["filtered_adni_10.zip", "filtered_adni_11.zip"]
    else:
        return ['filtered_adni_4.zip', 'filtered_adni_11.zip', 'filtered_adni_5.zip', 'filtered_adni_9.zip', 'filtered_adni_6.zip', 'filtered_adni_2.zip', 'filtered_adni_7.zip', 'filtered_adni_3.zip', 'filtered_adni_8.zip', 'filtered_adni_1.zip', 'filtered_adni_10.zip']
