out_path="./logid/"
rm -rf $out_path
mkdir $out_path
cd $out_path/../raw
echo $(pwd)

ls -d */ | while read dirname
do
    cd $dirname
    echo "$out_path${dirname%/}.txt"
    ls *mjlog | while read name
    do
        echo ${name%&*} >> "$out_path${dirname%/}.txt"
    done
    cd ..
done

echo "done"
