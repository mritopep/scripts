source /work/miniconda/etc/profile.d/conda.sh &> null.txt
conda init bash &> null.txt
conda activate simple_itk &> null.txt
soft/bias_field_correction.py $1 $2 &&  echo 'passed' > ./logs/$3 || echo 'failed' > ./logs/$3
