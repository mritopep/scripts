source /work/miniconda/etc/profile.d/conda.sh
conda init bash
conda activate skull_strip && \
skull_strip.py -i $1 -o $2
