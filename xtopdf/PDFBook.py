
# PDFBook.py - From a set of text files representing the chapters of
# a book, create a PDF file of the book's content.

# Author: Vasudev Ram

# Purpose: Reads a set of text files containing the chapters of a book
# and writes them to a single PDF file.

# Description:
#   Takes two command-line arguments:
#   - an output PDF file
#   - a "chapter list file"; this text file contains a list of lines.
#     Each line should consist of two fields, separated by a colon:
#     - a text file name; the file contains a chapter of a book
#     - the chapter heading as a string
#   Reads each of the text files, and creates, in the output PDF file,
#   a book with the contents of each chapter; the corresponding
#   chapter heading becomes the header and footer for the pages
#   comprising that chapter in the PDF file.

# $Id: PDFBook.py,v 1.3 2003/03/09 20:56:21 vasudev Exp vasudev $

# $Log: PDFBook.py,v $
# Revision 1.3  2003/03/09 20:56:21  vasudev
# Added RCS Id and Log keywords.
#

##------------------------ imports ---------------------------------------

import sys
import os
import os.path
import string
from PDFWriter import PDFWriter

##------------------------ usage -----------------------------------------

def usage():

	sys.stderr.write("Usage: python " + sys.argv[0] + \
	" pdf_file chapter_list_file\n")
	sys.stderr.write('''where
	pdf_file is the name of the PDF file to create, and
	chapter_list_file is the name of a text file containing
	information about chapters, one chapter per line.
	Format of this file:
	   Each line consists of two fields, separated by a colon.
	   Field 1 is the name of the text file containing a chapter.
	   Field 2 is the chapter title, to be used as the header/footer.
	''')
	sys.stderr.write(sys.argv[0] + " creates a PDF book from the chapters.\n")

##------------------------ main ------------------------------------------

def main():

	'''
	Program to create a PDF book from chapters contained in text files,
	one chapter per file.
	Command line args are:
	1. The name of the PDF file to create.
	2. The name of a text file containing info about chapters.
	   Format of this file:
	   Each line consists of two fields, separated by a colon.
	   Field 1 is the name of the text file containing a chapter.
	   Field 2 is the chapter title, to be used as the header/footer.
	'''
	
	# check for proper args
	if len(sys.argv) != 3:
		usage()
		sys.exit(1)

	# get the PDF file name and create the PDFWriter from it
	book_fn = sys.argv[1]
	pw = PDFWriter(book_fn)

	# set the font name and size for the PDF file
	pw.setFont("Courier", 10)

	# get the chapter list file name and open it, checking for I/O errors
	try:
		chap_list_fn = sys.argv[2]
		chap_list_fil = file(chap_list_fn)
	except IOError:
		sys.stderr.write(sys.argv[0] + ": IOError: while opening file " + \
		chap_list_fn + ". Exiting.\n")
		sys.exit(1)

	i = 0

	# loop over all the lines in the chapter list file
	for lin in chap_list_fil:
			i = i + 1
			if lin[-1] == "\n":
				lin = lin[:-1] # remove the trailing newline
			# split line into two fields, chapter file name and chapter title
			i = string.find(lin, ":")
			if (i == -1):
				sys.stderr.write(sys.argv[0] + \
				": Chapter list file format error: Line #" + \
				str(i) + " has no colon delimiter. Exiting.\n")
				chap_list_fil.close()
				sys.exit(0)
			chap_fn = lin[:i]
			chap_title = lin[i + 1:]
			# write the chapter to the PDF file
			write_chapter(pw, chap_fn, chap_title)

	pw.close()
	
##------------------------ write_chapter ---------------------------------

def write_chapter(pw, chap_fn, chap_title):

	# set the chapter title as the header/footer
	pw.setHeader(chap_title)
	pw.setFooter(chap_title)

	# open the chapter file, and send all its text to the PDFWriter
	try:
		chap_fil = file(chap_fn)
	except IOError:
		sys.stderr.write(sys.argv[0] + ": IOError: while opening chapter" + \
		" file " + chap_fn + ". Exiting.\n")
		sys.exit(1)
	for lin in chap_fil:
		pw.writeLine(lin)

	# close the chapter file
	chap_fil.close()

##------------------------ Global code -----------------------------------

# invoke main
if __name__ == "__main__":
	main()
	
##------------------------ EOF -------------------------------------------
