BASE_PATH=$(dirname $0)
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

python3 bin/calc.py $DATA_DIR/train.txt

mv bundle.ours $DATA_DIR/bundle.ours

../ACG-Localizer-master/build/src/Bundle2Info_128 $DATA_DIR/bundle.ours $DATA_DIR/train.txt $DATA_DIR/bundle.info

cat $DATA_DIR/test.txt | sed "s/\.jpg/\.key/" > $DATA_DIR/list.query.keys.txt

mkdir -p $DATA_DIR/pose

for d in `find $DATA_DIR -maxdepth 1 | egrep "clusters\..*\.txt$"`
do
    cluster_type=`echo $d | sed "s/$DATA_DIR\/clusters\.//" | sed "s/\.txt$//"`
    cluster_size=`echo $cluster_type | sed "s/k/000/"`
    echo "$cluster_type"
    ../ACG-Localizer-master/build/src/compute_desc_assignments $DATA_DIR/bundle.info 1 $cluster_size $d $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.$cluster_type.bin 6 1 0
    ../ACG-Localizer-master/build/src/acg_localizer_active_search_128 $DATA_DIR/list.query.keys.txt $DATA_DIR/bundle.ours $cluster_size $d $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.$cluster_type.bin 0 $DATA_DIR/results.txt 150 1 1 1 10 > $DATA_DIR/$cluster_size.log
done


