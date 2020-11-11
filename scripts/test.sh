SUFFIX=""
DATA_DIR=""
CLUSTER=""
OUTPUT="/dev/stdout"

if [ $# -ge 3 ]
then
    DATA_DIR=$1
    SUFFIX=$2
    CLUSTER=$3
else
    echo "Usage: $0 data_directory feature_dim clusters_size [verbose=1]"
    exit;
fi

if [ $# -ge 4 ]
then
    if [ $4 -eq 0 ]
    then
        OUTPUT="/dev/null"
    else
        OUTPUT="/dev/stdout"
    fi
fi

echo "Data directory '$DATA_DIR'"
echo "Feature dim: $SUFFIX"
echo "Cluster size: $CLUSTER"
echo "Output '$OUTPUT'"

cat $DATA_DIR/test.txt | sed "s/\.jpg/\.key/" > $DATA_DIR/list.query.keys.txt

./ACG_Localizer/build/src/acg_localizer_active_search_$SUFFIX $DATA_DIR/list.query.keys.txt $DATA_DIR/bundle.ours $CLUSTER $DATA_DIR/clusters.$CLUSTER.txt $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.$CLUSTER.bin 0 /dev/null 150 1 1 1 10 > $OUTPUT

python scripts/extract.py $DATA_DIR/list.query.keys.txt $DATA_DIR/info.txt > $OUTPUT

./RansacLib/build/examples/localization_with_gt $DATA_DIR/info.txt temp 20 200 0 1 .color.corr >$DATA_DIR/temp 2>/dev/null

rm temp.log temp.times.txt temp.stats.txt

cat $DATA_DIR/temp | grep "Median" && cat $DATA_DIR/temp | grep "5cm" && cat $DATA_DIR/temp | grep "20cm"
