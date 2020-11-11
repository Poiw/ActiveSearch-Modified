rm -rf ./ACG_Localizer/build && mkdir ./ACG_Localizer/build && cd ./ACG_Localizer/build
sed -i "s/const\ int\ dim\ =\ [0-9]*;/const\ int\ dim\ =\ 256;/" ../src/features/feature_loader.hh && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j8 && mv src/Bundle2Info src/Bundle2Info_256 && mv src/acg_localizer_active_search src/acg_localizer_active_search_256 && mv src/compute_desc_assignments src/compute_desc_assignments_256 && sed -i "s/const\ int\ dim\ =\ [0-9]*;/const\ int\ dim\ =\ 128;/" ../src/features/feature_loader.hh && make -j8 && mv src/Bundle2Info src/Bundle2Info_128 && mv src/acg_localizer_active_search src/acg_localizer_active_search_128 && mv src/compute_desc_assignments src/compute_desc_assignments_128
echo "build done."
echo "test..."

STATUS="1"
src/Bundle2Info_128 > /dev/null
STATUS=`expr $? \* $STATUS`
src/compute_desc_assignments_128 > /dev/null
STATUS=`expr 256 - $? \* $STATUS`
src/acg_localizer_active_search_128 > /dev/null
STATUS=`expr $? \* $STATUS`
src/Bundle2Info_256 > /dev/null
STATUS=`expr $? \* $STATUS`
src/compute_desc_assignments_256 > /dev/null
STATUS=`expr 256 - $? \* $STATUS`
src/acg_localizer_active_search_256 > /dev/null
STATUS=`expr $? \* $STATUS`

if [ $STATUS -eq 1 ]
then
    echo "test done."
else
    echo "test failed."
fi
cd ../..
