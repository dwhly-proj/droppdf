
# file_utils.py - Miscellaneous file utility functions.

# Author: Vasudev Ram

# $Id: file_utils.py,v 1.1 2003/03/10 18:52:31 vasudev Exp vasudev $

# $Log: file_utils.py,v $
# Revision 1.1  2003/03/10 18:52:31  vasudev
# Initial revision
#

# Note: whenever a new function is added to this file, also add
# some tests for it in main().

##------------------------ imports ---------------------------------------

import string

##------------------------ change_file_ext() -----------------------------

def change_file_ext(old_filename, old_ext, new_ext):
	'''
	Changes the extension of old_filename.
	If the substring old_ext occurs at the end of the filename,
	then replace it with new_ext. Else append new_ext.
	'''
	old_len = len(old_ext)
	if string.lower(old_filename[-old_len:]) == string.lower(old_ext):
		new_filename = old_filename[:-old_len] + new_ext
	else:
		new_filename = old_filename + new_ext

	return new_filename

##------------------------ main() ----------------------------------------

def main():
	'''
	Test the functions in this module.
		Test the function change_file_ext()
	'''
	fn1 = 'abc.txt'
	print "fn1 = ", fn1, " change_file_ext(fn1, '.txt', '.pdf') = ", \
		change_file_ext(fn1, '.txt', '.pdf')
	fn2 = 'abc'
	print "fn2 = ", fn2, " change_file_ext(fn2, '.txt', '.pdf') = ", \
		change_file_ext(fn2, '.txt', '.pdf')

##------------------------ GLOBAL CODE -----------------------------------

if __name__ == "__main__":
	main()
	
##------------------------ EOF -------------------------------------------
