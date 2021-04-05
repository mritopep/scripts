source /work/miniconda/etc/profile.d/conda.sh &> null.txt
conda init bash &> null.txt
conda activate simple_itk &> null.txt
soft/image_rgr.py $1 $2 $3
