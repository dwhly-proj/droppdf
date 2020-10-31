#!/bin/bash

source venv/bin/activate

filename=$1

outfile="${filename/'.pdf'/'_ocr.pdf'}"

ocrmypdf $1 $outfile
