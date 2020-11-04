DATA_DIR="TODO"
if [ $# -ge 1 ]
then
    DATA_DIR=$1
else
    exit;
fi

mkdir -p $DATA_DIR/sift/keys
for d in `find $DATA_DIR -maxdepth 2 | grep "[05]0\.color\.key$"`
do
    cp $d `echo "$d" | sed "s/\.color\.key/\.key/" | sed "s/$DATA_DIR\///" | sed "s/\//\./" | sed "s/^/$DATA_DIR\/sift\/keys\//"`
done

python3 bin/bof.py $DATA_DIR/sift/keys --size=12000 --sift=1 --target=$DATA_DIR/sift/clusters.12k.txt

cp $DATA_DIR/test.txt $DATA_DIR/sift/test.txt
cp $DATA_DIR/train.txt $DATA_DIR/sift/train.txt

./run.sh $DATA_DIR $DATA_DIR/sift
./test.sh $DATA_DIR $DATA_DIR/sift

