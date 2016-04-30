
# ReadDBF.py

# Author: Vasudev Ram

# $Id: ReadDBF.py,v 1.4 2003/03/09 20:19:09 vasudev Exp vasudev $

# $Log: ReadDBF.py,v $
# Revision 1.4  2003/03/09 20:19:09  vasudev
# Added RCS Id and Log keywords.
#

# Purpose: Reads information from a .DBF file and prints it
#   to standard output.
# Description:
#   Reads a .DBF file given as a command-line argument.
#   Prints the following information to stdout, with identifying labels:

#   - the file header:
#       - the DBF version (signature)
#       - the date of last update of the file
#       - the number of data records in the file
#       - the DBF header length in bytes
#       - the DBF record length in bytes
#       - the number of fields in the DBF file

#   - the field headers for each field:
#       - the field name
#       - the field type
#       - the field length
#       - the field decimals

#   - the data records:
#       - the actual records, one per line, preceded by a sequential
#           record number, a colon and a space. A delimiter character
#           (ASCII 30) is printed between fields, and before the first
#           and after the last field, to visually demarcate the fields.

##------------------------ imports ---------------------------------------

import os
import sys
import string
from struct import *

##------------------------ create_sep ------------------------------------

def create_sep(size, str_list):
	'''
	Create and returns a dictionary of strings
	meant to be used as separators in output.

	Each string in the list "str_list" (of strings) becomes
	one of the keys in the dictionary.
	The corresponding value for the key is just the same string
	repeated "size" times, concatenated together.

	Example call:
		sep = create_sep(60, ["-", "*"]

	Example use of return value:
		print sep["*"]
	'''
	
	sep = {}
	for str in str_list:
		# check that str is non-empty
		assert len(str) != 0
		if len(str) == 0:
			continue
		# create a string of (approximately) size chars from str,
		# repeated the appropriate # of times
		sep[str] = str * (size / len(str))
	return sep

##------------------------ GLOBAL CODE -----------------------------------

# Initialize separators
sep = create_sep(60, [ "=", "-", "*" ] )

##------------------------ open_file -------------------------------------

def open_file(dbf_fn):
	'''
	Open the filename "dbf_fn" in read mode and 
	return the file object created. Use mode "rb" for
	portability.
	'''
	f = file(dbf_fn, "rb")
	return f

##------------------------ get_dbf_hdr -----------------------------------

def get_dbf_hdr(f):
	'''
	Read the DBF file header info via file object f.
	Create and return a dictionary containing the
	DBF file's file header information. Each key
	is a string representing the name of a file header 
	item such as the number of records in the DBF file;
	each corresponding value is the value of that item.
	f.read() returns strings; conversion, when needed, is
	done by indexing into the tuple returned by unpack()'ing
	the returned string.
	'''
	dbf_hdr = {}	# an empty dictionary

	# read version - 1 byte
	c = f.read(1)
	tmp = unpack('B', c)
	dbf_hdr['ver'] = tmp[0]

	# read last update date - 3 bytes
	# Note: this program does not handle Y2K issues.
	c = f.read(3)
	tmp = unpack('3B', c)
	tmp2 = "%02s/%02s/%02s" % (tmp[0], tmp[1], tmp[2])
	# replace spaces by zeroes
	dbf_hdr['last_update'] = string.replace(tmp2, ' ', '0')

	# read num recs - 4 bytes
	c = f.read(4)
	tmp = unpack('4B', c)
	# num_recs is stored as a 32-bit (4-byte) integer in
	# little-endian format - the formula below converts it
	# to a Python integer
	dbf_hdr['num_recs'] =  tmp[0] + 256 * \
	(tmp[1] + 256 * (tmp[2] + 256 * (tmp[3])))

	# read DBF hdr len - 2 bytes
	c = f.read(2)
	tmp = unpack('2B', c)
	# hdr_len is stored as a 16-bit (2-byte) integer in
	# little-endian format - the formula below converts it
	# to a Python integer
	dbf_hdr['hdr_len'] = tmp[0] + 256 * tmp[1]

	# read DBF rec len - 2 bytes
	c = f.read(2)
	tmp = unpack('2B', c)
	# rec_len is stored as a 16-bit (2-byte) integer in
	# little-endian format - the formula below converts it
	# to a Python integer
	dbf_hdr['rec_len'] = tmp[0] + 256 * tmp[1]

	# Calculate # of fields in the DBF as follows:
	# complete hdr consists of file hdr info +
	# field hdrs info + 1 byte for hdr terminator 0x0D;
	# so size used by field hdrs info is (total hdr size
	# - file hdr size - 1) == hdr_len - 32 - 1
	# since file hdr size is 32 bytes. 
	# Then, # of fields is field hdr size / 32, since
	# each field hdr is 32 bytes; hence the formula below.
	dbf_hdr['num_flds'] = (dbf_hdr['hdr_len'] - 32 - 1) / 32

	# read and discard 20 reserved bytes (considered
	# as part of file hdr) - to reach start of dbf field hdrs
	#Now file ptr in f is positioned at
	# start of field hdrs area.
	c = f.read(20)
	
	# return the file header info, as a dict
	return dbf_hdr

##------------------------ print_dbf_hdr ---------------------------------

def print_dbf_hdr(dbf_fn, dbf_hdr):
	'''
	Print the DBF file header information in dict "dbf_hdr"
	for the file "dbf_fn", with suitable labels.
	'''
	print sep["="]
	print "Information for DBF file: %s" % (dbf_fn)
	print sep["-"]
	print "File Header Information:"
	print sep["-"]

	# setup the labels for the output in this section
	lbl_dbf_ver = \
	"DBF version (signature)       : "
	lbl_last_update = \
	"Date of last update (YY/MM/DD): "
	lbl_num_recs = \
	"Number of data records        : "
	lbl_hdr_len = \
	"DBF header length in bytes    : "
	lbl_rec_len = \
	"DBF record length in bytes    : "
	lbl_num_flds = \
	"Number of fields in DBF file  : "

	# print the file header info with the labels
	print lbl_dbf_ver + str(dbf_hdr['ver'])
	print lbl_last_update + dbf_hdr['last_update']
	print lbl_num_recs + str(dbf_hdr['num_recs'])
	print lbl_hdr_len + str(dbf_hdr['hdr_len'])
	print lbl_rec_len + str(dbf_hdr['rec_len'])
	print lbl_num_flds + str(dbf_hdr['num_flds'])
	print sep["-"]

##------------------------ get_dbf_fld -----------------------------------

def get_dbf_fld(f, num_flds):
	'''
	"f" is the file object for the DBF file opened in read mode.
	"num_flds" is the # of fields in the DBF file. 
	Read the DBF field headers from "f".
	Create a list, "dbf_fld", containing the
	field headers. "dbf_fld" is a list containing
	4 lists. Each of these lists has "num_flds" items.
	The 4 lists are :
	- fld_nam : the field names
	- fld_typ : the field types
	- fld_len : the field lengths
	- fld_dec : the field decimals
	f.read() returns strings; conversion, when needed, is
	done by indexing into the tuple returned by unpack()'ing
	the strings.
	Return "dbf_fld".
	'''
	
	# initialize the 4 lists
	fld_nam = []
	fld_typ = []
	fld_len = []
	fld_dec = []

	fld_num = 0

	# loop "num_flds" times
	while (fld_num < num_flds):

		# read & store fld name - 10 bytes
		c = f.read(10)
		# Note: field name is NULL-padded (ASCII 0), so change
		# NULLs to spaces
		fld_nam.append(string.replace(c, "\0", " "))

		# read and discard 1 reserved bytes - 
		# null terminator for fld name
		c = f.read(1)

		# read & store fld type - 1 byte
		c = f.read(1)
		tmp = unpack('c', c)
		fld_typ.append(tmp[0])

		# read and discard fld data addr (in mem) - 4 bytes
		c = f.read(4)

		# read & store fld len - 1 byte
		c = f.read(1)
		tmp = unpack('B', c)
		fld_len.append(tmp[0])

		# read & store fld dec - 1 byte
		c = f.read(1)
		tmp = unpack('B', c)
		fld_dec.append(tmp[0])

		# read and discard 14 reserved bytes
		c = f.read(14)

		fld_num = fld_num + 1

	# read and discard 1 reserved byte - end-of-hdr sentinel (0x0D),
	# so that file pointer of f now points to start of the 1st
	# data record.
	c = f.read(1)

	# Now inner lists are populated. Create outer list from them.
	dbf_fld = [fld_nam, fld_typ, fld_len, fld_dec]
	
	# return the field headers info, as a list of 4 lists
	return dbf_fld

##------------------------ print_dbf_fld ---------------------------------

def print_dbf_fld(dbf_fld, num_flds):
	'''
	"dbf_fld" is the list of lists containing the
	DBF field header.
	"num_flds" is the # of fields in the DBF file.
	Get the individual lists from "dbf_fld" into the lists
	"fld_nam", "fld_typ", "fld_len" and "fld_dec".
	Print the info contained in these lists. 
	'''
	print "Field Header Information:"
	print sep["-"]
	print "%3s%13s%7s%8s%10s" % \
		  ("#", "Field name", "Type", "Length", "Decimals")
	print sep["-"]

	# Extract the inner lists from the outer list "dbf_fld"
	fld_nam = dbf_fld[0]
	fld_typ = dbf_fld[1]
	fld_len = dbf_fld[2]
	fld_dec = dbf_fld[3]
	
	fld_num = 0

	# loop "num_flds" times
	while (fld_num < num_flds):
		print "%3s" % (fld_num + 1) , 
		print "%13s" % (fld_nam[fld_num]) , 
		print "%4s" % (fld_typ[fld_num]) ,
		print "%5s" % (fld_len[fld_num]) ,
		print "%7s" % (fld_dec[fld_num])
		fld_num = fld_num + 1
		
	print sep["-"]

##------------------------ get_dbf_data_rec ------------------------------

def get_dbf_data_rec(f, fld_len, num_flds):
	'''
	Read and return a data record from the DBF file object "f".
	Use the field lengths in "fld_len" to
	know how many bytes to read for each field.
	"num_flds" is the # of fields in each data record.
	'''
	fld_num = 0

	# Set a visible field separator char for display.
	# Print this separator before first field, between
	# each field, and after last field to clearly
	# demarcate fields in the record.
	fld_sep = chr(30)
	data_rec = fld_sep

	# read and discard del flag
	c = f.read(1)

	# loop "num_flds" times
	while (fld_num < num_flds):
		# read the right # of bytes for each field
		data_fld = f.read(fld_len[fld_num])
		# append them to the data record string
		data_rec = data_rec + data_fld + fld_sep
		fld_num = fld_num + 1

	# return the data record (as a string)
	return data_rec
			
##------------------------ print_dbf_data --------------------------------

def print_dbf_data(f, num_recs, fld_len, num_flds):			
	'''
	Print all the "num_recs" data records from the DBF file 
	object "f". Use the field lengths in "fld_len" to
	know how many bytes to read for each field. (This var. is
	not used in this fn., but is passed to get_dbf_data_rec().)
	"num_flds" is the # of fields in each data record.
	'''
	print "DBF Data Records:"
	print sep["-"]
	rec_num = 0
	
	# loop "num_recs" times
	while (rec_num < num_recs):
		# get one record as a string
		data_rec = get_dbf_data_rec(f, fld_len, num_flds)
		# print it with a leading serial number
		print "%5d:" % (rec_num + 1) ,
		print "%s" % (data_rec)
		rec_num = rec_num + 1
		
	print sep["="]
		
##------------------------ usage -----------------------------------------
			
def usage():			
	'''
	Print a usage message.
	'''
	sys.stderr.write("Usage: python " + sys.argv[0] + " dbf_file\n")
	sys.stderr.write("where dbf_file is the name of a .DBF file.\n")
	sys.stderr.write("The metadata and data of dbf_file are written\n")
	sys.stderr.write("to standard output.\n")

##------------------------ main ------------------------------------------

def main():
	'''
	Program to read and print the metadata and data from a DBF
	file. Prints, to sys.stdout:
	- the DBF file header
	- the DBF field headers
	- the DBF data records
	all neatly formatted for human readers.
	'''

	# check for correct args
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)
	dbf_fn = sys.argv[1]

	# open dbf file
	try:
		f = open_file(dbf_fn)
	except IOError:
		sys.stderr.write(sys.argv[0] + ": IO Error while opening file '" + \
		dbf_fn + "'. Exiting\n")
		sys.exit(1)

	# read dbf header (metadata) into the dict "dbf_hdr"
	dbf_hdr = get_dbf_hdr(f)

	# get the number of records in the DBF file
	num_recs = dbf_hdr['num_recs']

	# get the number of fields in the DBF file
	num_flds = dbf_hdr['num_flds']

	# print dbf header, neatly formatted
	print_dbf_hdr(dbf_fn, dbf_hdr)
	
	# read dbf fields (metadata) into the list (of 4 lists) "dbf_fld"
	dbf_fld = get_dbf_fld(f, num_flds)

	# print dbf fields, neatly formatted
	print_dbf_fld(dbf_fld, num_flds)

	# extract field lengths list from dbf_fld
	fld_len = dbf_fld[2] # 3rd list contained in dbf_fld

	# (read and) print dbf records (data), neatly formatted
	print_dbf_data(f, num_recs, fld_len, num_flds)

	f.close()

##------------------------ GLOBAL CODE -----------------------------------

if __name__ == "__main__":
	main()
	
##------------------------ EOF -------------------------------------------

