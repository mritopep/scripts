source /work/miniconda/etc/profile.d/conda.sh
conda init bash
conda activate petpvc && \
petpvc -i $1 -o $2 --pvc VC -x 6.0 -y 6.0 -z 6.0
