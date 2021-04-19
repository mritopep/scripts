source /work/miniconda/etc/profile.d/conda.sh &> null.txt
conda init bash &> null.txt
conda activate denoise &> null.txt
soft/denoise.py -i $1 -o $2 &&  echo 'passed' > ./logs/$3 || echo 'failed' > ./logs/$3
