
# PDFWriter.py - Write (plain text to a) PDF file.

# Author: Vasudev Ram

# Purpose: Reads any file containing plain text and writes it
#   to a PDF file.
# Description:
#   A class to provide a service of converting plain text to PDF.
#   Provides a writeLine() method and related methods for
#   writing the text to a PDF file.

# $Id: PDFWriter.py,v 1.4 2003/03/09 20:45:05 vasudev Exp vasudev $

# $Log: PDFWriter.py,v $
# Revision 1.4  2003/03/09 20:45:05  vasudev
# Added RCS Id and Log keywords.
#

##------------------------ imports ---------------------------------------

import sys
import os
import os.path
from file_utils import change_file_ext
import time
import string
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

##------------------------ PDFWriter -------------------------------------

class PDFWriter:

	'''
	A class to provide an API for writing lines of plain text
	to a PDF file.
	'''

##------------------------ PDFWriter.__init__ ----------------------------

	def __init__(self, pdf_fn):
		'''
		Constructor.
		"pdf_fn" arg is the name of the PDF file to be created.
		'''
		
		self.__pdf_fn = pdf_fn         # file name of PDF file
		self.__canv = canvas.Canvas(pdf_fn)     # canvas to write on
		self.__font_name = None       # font name
		self.__font_size = None       # font size
		self.__header_str = None      # header string (partial)
		self.__footer_str = None      # footer string (partial)
	
		self.__lines_per_page = 72     # num. of lines to print on each page
		self.__hdr_lines = 3           # num. of lines in header
		self.__ftr_lines = 3           # num. of lines in footer

		# num. of lines in body of page is total lines per page minus
		# header lines minus footer lines
		self.__body_lines = \
			self.__lines_per_page - self.__hdr_lines - self.__ftr_lines

		self.__x = 0.25 * inch         # x-coord for text output
		self.__top_y = 11.0 * inch     # y-coord for 1st line on each page
		self.__y = self.__top_y        # y-coord for text output
		                               # (changes for each line)
		self.__dy = 0.125 * inch       # inter-line spacing, delta-y

		self.__line_ctr = 0            # line counter, reset on each new page
		self.__page_saved = 0          # page saved flag: 0=unsaved, 1=saved
		self.__page_num = 0            # page number

##------------------------ PDFWriter.setFont -----------------------------

	def setFont(self, font_name, font_size):

		'''
		Public method.
		Save the font info in class members variables and reset the font
		for the canvas.
		'''

		self.__font_name = font_name
		self.__font_size = font_size
		self.__resetFont()
	
##------------------------ PDFWriter.__resetFont -------------------------

	def __resetFont(self):

		'''
		Private method.
		(Re)set the font for the canvas from saved values.
		'''

		self.__canv.setFont(self.__font_name, self.__font_size)
	
##------------------------ PDFWriter.setHeader ---------------------------

	def setHeader(self, header_str):

		'''
		Public method.
		Save the header string in a member variable.
		This method can be called anytime while writing the PDF output -
		the new value will take effect in the next header written.
		'''

		self.__header_str = header_str
		
	
##------------------------ PDFWriter.setFooter ---------------------------

	def setFooter(self, footer_str):

		'''
		Public method.
		Save the footer string in a member variable.
		This method can be called anytime while writing the PDF output -
		the new footer value will take effect in the next footer written.
		'''
		
		self.__footer_str = footer_str
	
##------------------------ PDFWriter.writeLine ---------------------------

	def writeLine(self, lin):

		'''
		Public method.
		Write a line of text, "lin", to the PDF file.
		Take care of doing a next page (footer/header) if needed -
		using __endPage() / __beginPage().
		Update the line counter.
		Call __writeLine() to actually write the line.
		'''

		# this fragment is executed only before the first body line is
		# written to a page.
		if self.__line_ctr == 0:
			self.__beginPage()

		# this fragment is executed for every line of the page,
		# including the first and last
		self.__writeLine(lin)    # actually write the line
		self.__line_ctr += 1     # update the line counter

		# this fragment is executed only after the last body line is
		# written to a page.
		if self.__line_ctr >= self.__body_lines:
			self.__endPage()

##------------------------ PDFWriter.__writeLine -------------------------

	def __writeLine(self, lin):

		'''
		Private method.
		Write a line of text, "lin", to the PDF file.
		'''
		# mark page as unsaved
		self.__page_saved = 0

		# write the line to the PDF file
		self.__canv.drawString(self.__x, self.__y, lin)

		# update the y coordinate
		self.__y = self.__y - self.__dy

##------------------------ PDFWriter.__beginPage -------------------------

	def __beginPage(self):

		'''
		Private method.
		Do stuff to begin a new page.
		'''

		# increment the page number
		self.__page_num += 1   

		# reset the y coordinate to the top of the page
		self.__y = self.__top_y

		# re-init font info for each new page
		self.__resetFont()
		
		# write the page header
		self.__writeHeader()

##------------------------ PDFWriter.__endPage ---------------------------

	def __endPage(self):

		'''
		Private method.
		Do stuff to end and save the current page.
		'''

		# code below is for boundary condition - when last page contains
		# less than "body_lines" lines of text - we decrement "y" till
		# we reach right position for footer, then write footer.

		if self.__line_ctr < self.__body_lines:
			lines_remaining = self.__body_lines - self.__line_ctr
			self.__y = self.__y - (self.__dy * lines_remaining)

		# write the page footer
		self.__writeFooter()

		# if page is not saved, save it and update saved flag
		if not self.__page_saved:
			self.__canv.save()      # call the save method of the canvas
			self.__page_saved = 1   # mark as saved
			self.__line_ctr = 0     # reset line counter for next page

##------------------------ PDFWriter.savePage ----------------------------

	def savePage(self):

		'''
		Public method.
		Save page.
		'''

		# call __endPage() to (end and) save the page
		self.__endPage()
		
##------------------------ PDFWriter.__writeHeader ---------------------

	def __writeHeader(self):

		'''
		Private method.
		Write page header.
		'''

		# to allow creating PDF files with no header text
		if self.__header_str == None or self.__header_str == "":
			return

		# append page num. to the header here (since it varies each time
		# __writeHeader() is called).
		hdr_lin = self.__header_str + \
			string.rjust("Page: " + str(self.__page_num), 20)

		# write the header: blank line + header line + blank line

		# empty line above header
		self.__canv.drawString(self.__x, self.__y, "")

		# bump y down
		self.__y = self.__y - self.__dy

		# the actual header
		self.__canv.drawString(self.__x, self.__y, hdr_lin)

		# bump y down
		self.__y = self.__y - self.__dy

		# empty line below header
		self.__canv.drawString(self.__x, self.__y, "")

		# bump y down
		self.__y = self.__y - self.__dy

		self.__page_saved = 0        # mark page as unsaved

##------------------------ PDFWriter.__writeFooter -----------------------

	def __writeFooter(self):

		'''
		Private method.
		Write page footer.
		'''

		# to allow creating PDF files with no footer text
		if self.__footer_str == None or self.__footer_str == "":
			return

		# append page num. to the footer here (since it varies each time
		# __writeFooter() is called).
		ftr_lin = self.__footer_str + \
			string.rjust("Page: " + str(self.__page_num), 20)

		# write the footer: blank line + footer line + blank line

		# empty line above footer
		self.__canv.drawString(self.__x, self.__y, "")

		# bump y down
		self.__y = self.__y - self.__dy

		# the actual footer
		self.__canv.drawString(self.__x, self.__y, ftr_lin)

		# bump y down
		self.__y = self.__y - self.__dy

		# empty line below footer
		self.__canv.drawString(self.__x, self.__y, "")

		# bump y down
		self.__y = self.__y - self.__dy

		self.__page_saved = 0        # mark page as unsaved

##------------------------ PDFWriter.close -------------------------------

	def close(self):

		'''
		Public method.
		Print footer of last page, if not already printed.
		Save the page.
		'''

		if not self.__page_saved:
			self.savePage()

##------------------------ usage -----------------------------------------

def usage():

	'''
	Usage message.
	'''
	sys.stderr.write(sys.argv[0] + ": Incorrect usage; see" + \
	" the code in main() for correct usage.\n")
	sys.stderr.write("Usage: python " + sys.argv[0] + \
	" <appropriate arguments>\n")

##------------------------ main ------------------------------------------

def main():

	'''
	Test driver function for PDFWriter class.
	'''

	lsa = len(sys.argv) 
	if lsa < 2:
		usage()
		sys.exit(1)
	
	# Create a PDFWriter instance
	pw = PDFWriter('testPDFWriter.pdf')
	# Set its font
	pw.setFont("Courier", 10)

	# Get the command line argument(s) to decide which test to run
	# from those below
	sw = sys.argv[1]

	# test1: sys.argv[2] should be the number of pages to generate
	if sw == "test1":

		if lsa != 3:
			usage()
			sys.exit(1)

		pw.setHeader("Test output 1 - A lines - PDFWriter.py - header")
		pw.setFooter("Test output 1 - A lines - PDFWriter.py - footer")

		# create a string of 60 A's
		lin = "A" * 60
		# number of pages is next argument
		num_pages = int(sys.argv[2])

		# 66 lines per page, num_pages pages
		for i in range(1, 66 * num_pages + 1):
			pw.writeLine(lin)
			# new page after every 33 lines
			if (i % 33) == 0:
				pw.savePage()
			print "i = ", i

	# test2: no extra args needed
	elif sw == "test2":
		
		if lsa != 2:
			usage()
			sys.exit(1)

		i = 1

		pw.setHeader("Test output 2 - stdio.m - PDFWriter.py - header")
		pw.setFooter("Test output 2 - stdio.m - PDFWriter.py - footer")

		# create a PDF file from filtered "man stdio" output
		ms = file("stdio.m")

		# loop over each line in ms
		for lin in ms:
			pw.writeLine(lin)
			print "i = ", i
			# new page after every 16 lines
			if (i % 16) == 0:
				pw.savePage()
			i = i + 1

	# test3: no extra args needed
	elif sw == "test3":
		
		if lsa != 2:
			usage()
			sys.exit(1)

		i = 1

		pw.setHeader("Test output 3 - file_a - PDFWriter.py - header")
		pw.setFooter("Test output 3 - file_a - PDFWriter.py - footer")

		# write contents of file_a to the PDF
		fa = file("file_a")
		for lin in fa:
			pw.writeLine(lin)
			print "i = ", i
			i = i + 1

		fa.close()

		i = 1

		pw.setHeader("Test output 3 - file_b - PDFWriter.py - header")
		pw.setFooter("Test output 3 - file_b - PDFWriter.py - footer")

		# write contents of file_b to the PDF
		fb = file("file_b")
		for lin in fb:
			pw.writeLine(lin)
			print "i = ", i
			i = i + 1

		fb.close()

	else:
		# add more tests here if needed (change else to elif)
		usage()
		sys.exit(1)

	# close the PDFWriter
	pw.close()
	
##------------------------ Global code -----------------------------------

if __name__ == "__main__":
	main()
	
##------------------------ EOF -------------------------------------------
