BASE_PATH=$(dirname $0)
DATA_DIR="TODO"
LOG="12k.log"

if [ $# -ge 1 ]
then
    echo "Data directory '$1'"
    DATA_DIR=$1
else
    echo "Usage: $0 data_directory"
    exit
fi

if [ $# -ge 2 ]
then
    LOG=$2
fi

echo "Log path '$LOG'"

mkdir -p $DATA_DIR/pose && python3 bin/analyze.py $DATA_DIR/$LOG $DATA_DIR/pose && python3 bin/error.py $DATA_DIR/test.txt $DATA_DIR/pose && cat result.txt | grep median && rm -rf $DATA_DIR/pose
