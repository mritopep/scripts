source /work/miniconda/etc/profile.d/conda.sh
conda init bash
conda activate simple_itk && \
soft/bias_field_correction.py $1 $2
