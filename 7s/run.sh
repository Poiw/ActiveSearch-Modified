BASE_PATH=$(dirname $0)
IMAGE_DIR="TODO"
SUFFIX=""
DATA_DIR="data"

if [ $# -ge 1 ]
then
    echo "Images directory '$1'"
    IMAGE_DIR=$1
else
    echo "Usage: $0 image_directory [data_directory=./data]"
    exit;
fi

if [ $# -ge 2 ]
then
    DATA_DIR=$2
fi

echo "Data directory '$DATA_DIR'"

python3 bin/calc.py $DATA_DIR/train.txt

mv bundle.ours $DATA_DIR/bundle.ours

../master/ACG_Localizer/build/src/Bundle2Info$SUFFIX $DATA_DIR/bundle.ours $DATA_DIR/train.txt $DATA_DIR/bundle.info

../master/ACG_Localizer/build/src/compute_desc_assignments$SUFFIX $DATA_DIR/bundle.info 1 12000 $DATA_DIR/clusters.12k.txt $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.12k.bin 6 1 0
