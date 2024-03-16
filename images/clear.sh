#!/bin/sh

# Count the number of files
file_count=$(find . -maxdepth 1 -type f | wc -l)

imp_files=7

scanned_imgs=$(expr $file_count - $imp_files)

i=1
while [ $i -le $scanned_imgs ]; do
    rm "scanned_img_${i}.jpg"
    i=$(expr $i + 1)
done

echo "Scanned images are deleted from the images directory."
