from os import listdir
from os import system as run
from general import get_data

nii_files = get_data("/content/data/pickle/nii_files.pkl")
print(len(nii_files)/2)

folder = "../data"
new_folder = "new_data"
subjects = listdir(folder)
g = 1

for subject in subjects:
    mr_file = folder + "/"+ subject + "/mri.nii"
    pet_file = folder + "/" + subject + "/pet.nii"
    t1 = "A/train/" + str(g)
    t2 = "B/train/" + str(g)
    g += 1
    run("med2image -i " + mr_file + " -o " + new_folder + t1)
    run("med2image -i " + pet_file + " -o " + new_folder + t2)

