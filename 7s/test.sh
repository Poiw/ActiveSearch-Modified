BASE_PATH=$(dirname $0)
SUFFIX=""
IMAGE_DIR="TODO"
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

cat $DATA_DIR/test.txt | sed "s/\.jpg/\.key/" > $DATA_DIR/list.query.keys.txt

../master/ACG_Localizer/build/src/acg_localizer_active_search$SUFFIX $DATA_DIR/list.query.keys.txt $DATA_DIR/bundle.ours 12000 $DATA_DIR/clusters.12k.txt $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.12k.bin 0 $DATA_DIR/results.txt 150 1 1 1 10 > $DATA_DIR/12k.log

rm -rf $DATA_DIR/pose
mkdir -p $DATA_DIR/pose

python3 bin/analyze.py $DATA_DIR/12k.log $DATA_DIR/pose

python3 bin/error.py $DATA_DIR/test.txt $DATA_DIR/pose
