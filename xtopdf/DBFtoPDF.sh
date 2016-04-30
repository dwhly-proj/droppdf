#!/bin/bash
# DBFtoPDF.sh
# A bash script to run ReadDBF.py and WritePDF.py in sequence,
# to generate a PDF file from a DBF file's metadata and data.

# Author: Vasudev Ram

# $Id: DBFtoPDF.sh,v 1.1 2003/03/22 15:03:08 vasudev Exp vasudev $
# $Log: DBFtoPDF.sh,v $
# Revision 1.1  2003/03/22 15:03:08  vasudev
# Initial revision
#
# Revision 1.2  2003/03/09 20:02:45  vasudev
# Minor changes, tested - ok.
#

# check correct num. of args
if [ $# -ne 1 ]
then
	echo "Usage: $0 dbf_file"
	echo "where dbf_file is the name of a DBF file"
	echo "This program will write dbf_file's"
	echo "metadata and data to a PDF file."
	exit 1
fi

# setup filenames - DBF, text, PDF
dbf_file=$1
txt_file="$dbf_file.txt"
pdf_file="$dbf_file.pdf"

# run ReadDBF.py on the DBF file
python2.2 ReadDBF.py $dbf_file >$txt_file
retval=$?
if [ $retval -ne 0 ]
then
	echo "$0: ReadDBF.py failed"
	exit $retval
fi

# run WritePDF.py on the text file
python2.2 WritePDF.py $txt_file
retval=$?
if [ $retval -ne 0 ]
then
	echo "$0: WritePDF.py failed"
	exit $retval
fi

# cleanup and exit
echo "$0: output is in $pdf_file"
rm $txt_file
exit 0

