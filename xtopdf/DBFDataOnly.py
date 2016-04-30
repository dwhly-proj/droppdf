
# DBFDataOnly.py
# Purpose: A progam to read only the data records from a list of
# DBF files specified on the command line.

# Author: Vasudev Ram

# $Id: DBFDataOnly.py,v 1.2 2003/03/10 19:32:21 vasudev Exp vasudev $

# $Log: DBFDataOnly.py,v $
# Revision 1.2  2003/03/10 19:32:21  vasudev
# Added RCS Id and Log keywords.
#

##------------------------ imports ---------------------------------------

import os
import sys
import string
from DBFReader import DBFReader

##------------------------ main ------------------------------------------

def main():
	'''
	A progam to read only the data records from a list of
	DBF files specified on the command line. Records read
	are written to standard output.
	'''

	# check for correct num. of args
	if len(sys.argv) == 1:
		usage()
		sys.exit(1)

	# loop over args, print records from each arg (which should be
	# a DBF file)
	for f in sys.argv[1:]:
		print_data(f)

	sys.exit(0)

##------------------------ usage() -----------------------------------

def usage():
	'''
	Print usage message.
	'''

	sys.stderr.write("Usage: python " + sys.argv[0] + " dbf_file ...\n")
	sys.stderr.write(sys.argv[0] + " reads the dbf_file(s) and writes,\n")
	sys.stderr.write("to standard output, only their data records,\n")
	sys.stderr.write("formatted for further processing.\n")

##------------------------ print_data --------------------------------

def print_data(f): 
	'''Print the data records only from the DBF filename "f".
	'''

	# create the DBFReader instance from the filename
	dr = DBFReader(f)

	# open it
	dr.open()

	# position instance's file pointer to start of 1st data record
	dr.reset()
	
	# loop for all records in the file
	while (dr.has_next_record()):

		# get the record as a tuple consisting of the deleted flag,
		# and a list of the fields as strings
		lis1 = dr.next_record()

		# extract the list of fields from the tuple
		lis2 = lis1[1]

		# build up a single string representing the record, from all the
		# fields, delimited by the "|" character
		s = ""
		for item in lis2[0:-1]:
			s = s + "%s|" % (item)

		# print the record string
		s = s + lis2[-1]
		print s

	# close the DBFReader
	dr.close()

##------------------------ Global code -----------------------------------

# invoke main
if __name__ == '__main__':
	main()

##------------------------ EOF -------------------------------------------
