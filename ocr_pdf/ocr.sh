#!/bin/bash

#source venv/bin/activate

filename=$1

outfile="${filename/'.pdf'/'_ocr.pdf'}"

#echo 'XXX' 
echo $filename
echo $outfile

#if ocr fails because it has text, just copy the file with new name 
if ocrmypdf $1 $outfile | grep -q 'page already has text'; then
    cp $filename $outfile
fi
