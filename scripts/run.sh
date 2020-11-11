SUFFIX=""
DATA_DIR=""
CLUSTER=""
OUTPUT="/dev/stdout"
SIFT="0"

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

if [ $SUFFIX -eq 128 ]
then
    SIFT="1"
else
    SIFT="0"
fi

echo "Data directory '$DATA_DIR'"
echo "Feature dim: $SUFFIX"
echo "Cluster size: $CLUSTER"
echo "Output '$OUTPUT'"

mkdir -p $DATA_DIR/keys

for d in `cat $DATA_DIR/train.txt | grep "[369]0\.color\.jpg$"`
do
    cp `echo "$d" | sed "s/jpg$/key/"` "$DATA_DIR/keys/`echo "$d" | sed "s/\.color\.jpg/\.key/" | sed "s/\//\./g"`"
done

# python scripts/bof.py $DATA_DIR/keys --size=$CLUSTER --sift=$SIFT --target=$DATA_DIR/clusters.$CLUSTER.txt > $OUTPUT

python scripts/calc.py $DATA_DIR/train.txt > $OUTPUT

mv bundle.ours $DATA_DIR/bundle.ours

./ACG_Localizer/build/src/Bundle2Info_$SUFFIX $DATA_DIR/bundle.ours $DATA_DIR/train.txt $DATA_DIR/bundle.info > $OUTPUT

./ACG_Localizer/build/src/compute_desc_assignments_$SUFFIX $DATA_DIR/bundle.info 1 $CLUSTER $DATA_DIR/clusters.$CLUSTER.txt $DATA_DIR/bundle.desc_assignments.integer_mean.voctree.clusters.$CLUSTER.bin 6 1 0 > $OUTPUT

