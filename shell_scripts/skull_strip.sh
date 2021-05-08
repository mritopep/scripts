#!/bin/bash
source /work/miniconda/etc/profile.d/conda.sh &> ./logs/null.txt
conda init bash &> ./logs/null.txt
conda activate skull_strip &> ./logs/null.txt
soft/skull_strip.py -i $1 -o $2 &&  echo 'passed' > ./logs/$3 || echo 'failed' > ./logs/$3
