source /work/miniconda/etc/profile.d/conda.sh
conda init bash
conda activate denoise && \
soft/denoise.py -i $1 -o $2
