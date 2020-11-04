data="heads/sift"
img="heads"
as_path="../master/ACG_Localizer/build/src" #"/usr/local/bin"
suffix="" #"_128"
cluster="TODO"
if [ $# -ge 1 ]
then
    cluster=$1
else
    echo "invalid command"
    exit;
fi

ksize=`echo $cluster | sed "s/clusters\.//" | sed "s/\.txt$//"`
size=`echo $ksize | sed "s/k/000/"`
echo $ksize
cat $data/test.txt | sed "/[1-9].color.jpg$/d" | sed "s/\.jpg/\.key/" > $data/list.query.keys.txt
$as_path/compute_desc_assignments$suffix $data/bundle.info 1 $size $data/clusters.$ksize.txt $data/bundle.desc_assignments.integer_mean.voctree.clusters.$ksize.bin 6 1 0 > $data/$ksize.log
$as_path/acg_localizer_active_search$suffix $data/list.query.keys.txt $data/bundle.ours $size $data/clusters.$ksize.txt $data/bundle.desc_assignments.integer_mean.voctree.clusters.$ksize.bin 0 $data/results.txt 125 1 1 1 10 > $data/$ksize.log
rm -rf $data/pose
mkdir -p $data/pose
python3 bin/analyze.py $data/$ksize.log $data/pose > quiet.log
python3 bin/error.py $data/list.query.keys.txt $data/pose > quiet.log
cat result.txt | grep median
mv result.txt $data/result.$ksize.txt
rm -f quiet.log
