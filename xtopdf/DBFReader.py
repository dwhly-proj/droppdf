
# DBFReader.py
# Purpose: A class that reads a DBF file.
# Provides methods to access the metadata and the data in the file.

# Author: Vasudev Ram

# $Id: DBFReader.py,v 1.3 2003/03/09 20:23:38 vasudev Exp vasudev $

# $Log: DBFReader.py,v $
# Revision 1.3  2003/03/09 20:23:38  vasudev
# Added RCS Id and Log keywords.
#

#
# Description:
#   Reads a .DBF file given as a constructor argument.
#   Provides methods to get the following information from the file:

#   - the file header (as a dictionary), comprising:
#       - the DBF version (signature)
#       - the date of last update of the file
#       - the number of data records in the file
#       - the DBF header length in bytes
#       - the DBF record length in bytes
#       - the number of fields in the file

#   - the field headers (as a list of 4 lists) for each field, comprising:
#       - the field name
#       - the field type
#       - the field length
#       - the field decimals
#		each of the 4 lists contains as many items as the number of fields
#		in a DBF data record

#   - the data records:
#       - the actual records, sequentially, from first to last
#		- each record is returned as a tuple containing two items:
#			- a single character string, the record-deleted indicator
#			- a list of strings; each string is the value of a field
#				of the record

##------------------------ imports ---------------------------------------

import os
import sys
import copy
import string
from struct import *

##------------------------ DBFReader -----------------------------------

class DBFReader:

	'''Class that provides metadata and data from a DBF file.
	'''

	def __init__(self, dbf_fn):

		'''DBFReader constructor.
			dbf_fn arg: filename of the DBF file. Should be either
			absolute path, or accessible from current dir of caller app.
		'''

		self.__dbf_fn = dbf_fn    # the DBF file name
		self.__dbf_fil = None     # the DBF file object
		self.__dbf_file_header = None    # the DBF file header
		self.__dbf_field_headers = None    # the DBF field headers

		self.__dbf_rec_len = None    # the DBF data record length
		self.__dbf_num_recs = None    # the num. of data records
		self.__dbf_num_flds = None    # the num. of fields in a data record

		self.__dbf_file_header_len = 32    # the DBF file header length
		self.__dbf_field_header_len = 32    # the length of a DBF field header
		self.__dbf_field_len = None    # the list of DBF field lengths

		# CONSTANTS - DON'T MODIFY

		# the byte offset (from the start of the file) of the file header
		self.__DBF_FILE_HEADER_OFFSET = 0

		# the byte offset (from the start of the file) of the 1st field header
		self.__DBF_FIELD_HEADER_OFFSET = 32

		# the byte offset (from the start of the file) of the 1st data record
		self.__DBF_DATA_REC_OFFSET = None    # value set later in the code

		# the serial number of the current data record
		self.__dbf_curr_record_num = None

##------------------------ DBFReader.open ----------------------------

	def open(self):

		'''
		Public method.
		Open the filename "self.__dbf_fn" in read mode and 
		save the file object created.
		Use mode "rb" for portability between Lin/Win.
		Check for already opened file.
		Save the file and field headers as instance variables.
		'''

		# check if file already open
		if self.__dbf_fil == None:
			pass
		else:
			print sys.argv[0] + \
			":DBFReader.open(): error: file already open: " + self.__dbf_fn
			sys.exit(1)

		# open the file
		try:
			f = file(self.__dbf_fn, "rb")
			self.__dbf_fil = f
		except IOError:
			sys.stderr.write(sys.argv[0] + ": DBFReader.open(): " + \
			"error opening file " + self.__dbf_fn + \
			": IOError. Exiting.\n")
			sys.exit(1)

		# read the file header and save it in a member variable
		self.read_dbf_file_header()

		# read the field headers and save them in a member variable
		self.read_dbf_field_headers()

##------------------------ DBFReader.read_dbf_file_header ----------------

	def read_dbf_file_header(self):

		'''
		Public method.
		If not already called,
			call __read_dbf_file_header() to read the DBF file
			header.
			(Deep) copy the return value.
		Return the copy.
		'''

		# check if file header already read
		if self.__dbf_file_header == None:
			# if not, read it
			self.__dbf_file_header = self.__read_dbf_file_header()

		# save the rec_len for easy access
		self.__dbf_rec_len = self.__dbf_file_header["rec_len"]

		# save the num_recs for easy access
		self.__dbf_num_recs = self.__dbf_file_header["num_recs"]

		# save the num_flds for easy access
		self.__dbf_num_flds = self.__dbf_file_header["num_flds"]

		# deep-copy the file header; return the copy; this is to
		# prevent accidental modification by callers
		self.dbf_file_header_copy = copy.deepcopy(self.__dbf_file_header)
		return self.dbf_file_header_copy

##------------------------ DBFReader.__read_dbf_file_header ----------------

	def __read_dbf_file_header(self):

		'''
		Private method.
		Reads the DBF file header and returns it
		as a dictionary. Meant to be called only by
		public method DBFReader.read_dbf_file_header().

		Gets the DBF file's file header information. Each key
		is a string representing the name of a file header 
		item such as the number of records in the DBF file;
		each corresponding value is the value of that item.
		f.read() returns strings; conversion, when needed, is
		done by indexing into the tuple returned by unpack()'ing
		the returned strings.
		'''

		dbf_hdr = {}	# an empty dictionary

		# alias self.__dbf_fil for less typing
		f = self.__dbf_fil

		# position file pointer to start of file header
		f.seek(self.__DBF_FILE_HEADER_OFFSET)

		# read version - 1 byte
		c = f.read(1)
		tmp = unpack('B', c)
		dbf_hdr['ver'] = tmp[0]

		# read last update date - 3 bytes
		c = f.read(3)
		tmp = unpack('3B', c)   # unpack as bytes
		tmp2 = "%02s/%02s/%02s" % (tmp[0], tmp[1], tmp[2])
		# replace spaces by zeroes
		dbf_hdr['last_update'] = string.replace(tmp2, ' ', '0')

		# read num recs - 4 bytes - integer, little-endian format
		c = f.read(4)
		tmp = unpack('4B', c)
		# convert it into a Python integer
		dbf_hdr['num_recs'] =  tmp[0] + 256 * \
		(tmp[1] + 256 * (tmp[2] + 256 * (tmp[3])))

		# read DBF hdr len - 2 bytes - integer, little-endian format
		c = f.read(2)
		tmp = unpack('2B', c)
		# convert it into a Python integer
		dbf_hdr['hdr_len'] = tmp[0] + 256 * tmp[1]

		# read DBF rec len - 2 bytes - integer, little-endian format
		c = f.read(2)
		tmp = unpack('2B', c)
		# convert it into a Python integer
		dbf_hdr['rec_len'] = tmp[0] + 256 * tmp[1]

		# Calculate # of fields in the DBF as follows:
		# complete hdr consists of file hdr + fld hdrs
		# + 1 byte for hdr terminator 0x0D.
		# So size used by fld hdrs is (total hdr size
		# - file hdr size - 1) == hdr_len - 32 - 1,
		# since file hdr size is 32 bytes. 
		# Then, # of fields is fld hdr size / 32, since
		# each fld hdr is 32 bytes.
		# Hence the formula below.
		dbf_hdr['num_flds'] = (dbf_hdr['hdr_len'] - 32 - 1) / 32

		# return the file header as a dict
		return dbf_hdr

##------------------------ DBFReader.read_dbf_field_headers --------------

	def read_dbf_field_headers(self):

		'''
		Public method.
		If not already called,
			call __read_dbf_field_headers() to read the DBF field
			headers.
			(Deep) copy the return value.
		Return the copy.
		'''

		# check if field headers already read
		if self.__dbf_field_headers == None:
			# if not, read them
			self.__dbf_field_headers = self.__read_dbf_field_headers()

		# deep-copy the field headers; return the copy; this is to
		# prevent accidental modification by callers
		self.dbf_field_headers_copy = copy.deepcopy(self.__dbf_field_headers)
		return self.dbf_field_headers_copy


##------------------------ DBFReader.__read_dbf_field_headers ------------

	def __read_dbf_field_headers(self):

		'''
		Private method.
		Reads and returns the DBF field headers.
		Read the DBF field headers from the file.
		Create a list, "dbf_fld", containing the
		field headers. "dbf_fld" is a list containing
		4 lists. Each of these lists has "self.__dbf_num_flds" items.
		The 4 lists are :
		- fld_nam : the field names
		- fld_typ : the field types
		- fld_len : the field lengths
		- fld_dec : the field decimals
		f.read() returns strings; conversion, when needed, is
		done by (indexing into the tuple returned by) unpack().
		Return "dbf_fld".
		'''

		fld_nam = []
		fld_typ = []
		fld_len = []
		fld_dec = []

		# alias self.__dbf_fil for less typing
		f = self.__dbf_fil

		# position file pointer to start of 1st field header
		f.seek(self.__DBF_FIELD_HEADER_OFFSET)

		fld_num = 0

		# loop "self.__dbf_num_flds" times
		while (fld_num < self.__dbf_num_flds):

			# read & store fld name - 10 bytes
			c = f.read(10)
			# field name is NULL-padded (ASCII 0), so change
			# NULLs to spaces
			fld_nam.append(string.replace(c, "\0", " "))

			# read and discard 1 reserved byte - 
			# null terminator for fld name
			c = f.read(1)

			# read & store fld type - 1 byte
			c = f.read(1)
			tmp = unpack('c', c)    # unpack as string
			fld_typ.append(tmp[0])

			# read and discard fld data addr (in mem) - 4 bytes
			c = f.read(4)

			# read & store fld len - 1 byte
			c = f.read(1)
			tmp = unpack('B', c)    # unpack as byte
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
		
		# save the field lengths list in a member variable for easy access
		self.__dbf_field_len = fld_len
		
		# return the field headers as a list of 4 lists
		return dbf_fld

##------------------------ DBFReader.reset -------------------------------

	def reset(self):

		'''
		Public method.
		Reset the self.__dbf_fil variable's file pointer to point
		to the start of the 1st data record.
		Update the self.__curr_rec_num variable if there are any records.
		'''

		if self.__DBF_DATA_REC_OFFSET == None:
			self.__DBF_DATA_REC_OFFSET = \
				self.__dbf_file_header_len + \
				(self.__dbf_field_header_len * self.__dbf_num_flds) + 1

		self.__dbf_fil.seek(self.__DBF_DATA_REC_OFFSET)

		if self.__dbf_num_recs > 0:
			self.__dbf_curr_record_num = 1


##------------------------ DBFReader.has_next_record ---------------------

	def has_next_record(self):

		'''
		Public method.
		Returns 1 (true) if there is a next record to be read,
		else 0 (false).
		'''

		# if no records in file, cannot be any next record
		if self.__dbf_num_recs == 0:
			return 0

		# if current record num. is between 1 and the total num.
		# of records, there is a next record that can be read
		if (self.__dbf_curr_record_num >= 1) and \
			(self.__dbf_curr_record_num <= self.__dbf_num_recs):
			return 1
		else:
			return 0

##------------------------ DBFReader.next_record -------------------------

	def next_record(self):

		'''
		Public method.
		Reads the next record.
		Returns it as a tuple consisting of:
			- a deleted flag : ' ' => not deleted, 'D' => deleted
			- a list of fields; each field is returned as a string,
			  the same way that they are stored in the DBF file.
		'''

		# alias self.__dbf_fil for less typing
		f = self.__dbf_fil

		# read the deleted flag and convert it to more user-friendly form
		del_flag = f.read(1)
		if (del_flag == '*'):
			del_flag = 'D'
		#else: # if its not a "*" it must be a " ", do nothing
			# pass

		# create a list for the fields of the record
		flds = []
		
		# loop "self.__dbf_num_flds" times :
		# read each field and add it to the list
		for i in range(self.__dbf_num_flds):
			fld_i = f.read(self.__dbf_field_len[i])
			flds.append(fld_i)

		# create a tuple from the deleted flag and the fields of the record
		rec = (del_flag, flds)

		# bump up the current record #
		self.__dbf_curr_record_num += 1
		
		# return the data record as a list of strings
		return rec

##------------------------ DBFReader.close ---------------------------

	def close(self):

		'''
		Public method.
		Closes the DBF file object dbf_fil.
		'''

		self.__dbf_fil.close()

##------------------------ usage -----------------------------------------

def usage():

	'''
	Print a usage message.
	'''
	sys.stderr.write("Usage: python " + sys.argv[0] + " dbf_file\n")
	sys.stderr.write("where dbf_file is the name of a .DBF file.\n")
	sys.stderr.write("The metadata and data of dbf_file\n")
	sys.stderr.write("are written to standard output.\n")


##------------------------ main ------------------------------------------

def main():

	'''
	Main function to test DBFReader class.
	'''

	# check correct num. of args
	if (len(sys.argv) != 2):
		usage()
		sys.exit(1)

	# instantiate a DBFReader object from the arg
	dr = DBFReader(sys.argv[1])
	# call its open() method to read in the metadata
	dr.open()

	# get the file header
	file_header = dr.read_dbf_file_header()

	# extract num_flds item from the file header
	num_flds = file_header["num_flds"]

	# print the file header's keys and values
	print "File header :"
	print
	for k in file_header.keys():
		print "key:", k, "value:", str(file_header[k])
	print

	# get the field headers into a list
	field_headers = dr.read_dbf_field_headers()

	print "Field headers :"
	print
	# print num_flds
	print 'num_flds = ', num_flds

	# extract the 4 inner lists from the field headers list
	fld_nam, fld_typ, fld_len, fld_dec = (
		field_headers[0], 
		field_headers[1], 
		field_headers[2], 
		field_headers[3] )

	# print a heading for the field headers output
	print "%12s|%8s|%8s|%8s" % (" Name ", " Type ", " Length ", " Decimals ")

	# print the field headers
	for i in range(num_flds):
		print "%12s|%8s|%8d|%8d" % (
		fld_nam[i], fld_typ[i], fld_len[i], fld_dec[i] )
	print

	# reset file pointer to start of 1st data record
	dr.reset()

	print "Data records:"
	print
	
	# read and print all the data records
	while dr.has_next_record():
		r = dr.next_record()
		print r
	print

	# close the DBFReader
	dr.close()

##------------------------ Global code -----------------------------------

# invoke main

if __name__ == '__main__':
	main()

##------------------------ EOF - DBFReader.py ----------------------------

