import os
import pickle
import gzip
import shutil

def upzip_gz(input,output):
    with gzip.open(input, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def store_data(data,path):
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

def update_progress(curr_count,total_count):
    progress = int((curr_count/total_count)*100)
    print('[{0}] {1}%'.format('#'*(progress/10), progress))

def lock(data,val):
    if val:
        return data[:2]
    else:
        return data

def show_data(tag,data):
    for num,data in enumerate(data):
        print(f"{tag}:{num} - {data}")

def list_directory(dir):
    try:
        return os.listdir(dir)
    except:
        print("NO DIR")

def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)
