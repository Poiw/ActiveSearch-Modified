IMAGE_DIR=""
DATA_DIR=""
OLD_SUFFIX=""
NEW_SUFFIX=""

if [ $# -ge 4 ]
then
    echo "Images directory '$1'"
    echo "Data directory '$2'"
    echo "Src suffix '$3'"
    echo "Dest suffix '$4'"
    IMAGE_DIR=$1
    DATA_DIR=$2
    OLD_SUFFIX=$3
    NEW_SUFFIX=$4
else
    echo "Usage: $0 image_directory data_directory src_suffix dest_suffix"
    exit;
fi

for d in `find $IMAGE_DIR | grep "$OLD_SUFFIX$"`
do
    cp $d `echo $d | sed "s/$OLD_SUFFIX$/$NEW_SUFFIX/"`
done

for d in `find $DATA_DIR | grep "$OLD_SUFFIX$"`
do
    cp $d `echo $d | sed "s/$OLD_SUFFIX$/$NEW_SUFFIX/"`
done
