#!/bin/sh
cd ./tests/addons/
for FILE in *; do
    echo "\n";
    echo "Generating spl for $FILE";
    slim package $FILE;
done
for file in *.tar.gz; do
    echo "$file";
    mv "$file" "${file%.tar.gz}.spl"
done
mkdir ../src
mv *.spl ../src/
cd ../..