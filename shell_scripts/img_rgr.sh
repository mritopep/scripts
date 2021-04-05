source /work/miniconda/etc/profile.d/conda.sh
conda init bash
conda activate simple_itk && \
soft/image_rgr.py $1 $2
