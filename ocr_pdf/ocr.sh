#!/bin/bash

#source venv/bin/activate
rt LC_ALL=C.UTF-8
export LANG=C.UTF-8

filename=$1

cd /home/www-data/droppdf/ocr_pdf

. venv/bin/activate

outfile="${filename/'.pdf'/'_ocr.pdf'}"

#if ocr fails because it has text, just copy the file with new name 
if ocrmypdf $1 $outfile | grep -q 'page already has text'; then
    cp $filename $outfile
fi

filename=$1

outfile="${filename/'.pdf'/'_ocr.pdf'}"

#echo 'XXX' 
echo $filename
echo $outfile

#if ocr fails because it has text, just copy the file with new name 
if ocrmypdf $1 $outfile | grep -q 'page already has text'; then
    cp $filename $outfile
fi
