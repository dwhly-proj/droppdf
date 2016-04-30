
# WritePDF.py - Write (plain text to a) PDF file.

# Author: Vasudev Ram

# $Id: WritePDF.py,v 1.6 2003/03/09 20:08:46 vasudev Exp vasudev $

# $Log: WritePDF.py,v $
# Revision 1.6  2003/03/09 20:08:46  vasudev
# Added RCS Id and Log keywords.
#

# Purpose: Reads any file containing plain text and writes it
#   to a PDF file.
# Description:
#   Reads a text file given as a command-line argument.
#   Writes the contents of the text file to a PDF file.
#   Uses the ReportLab Toolkit for generating PDF content.
#   URL: http://www.reportlab.com

##------------------------ imports ---------------------------------------

import sys
import os
import os.path
from file_utils import change_file_ext
import time
import string
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

##------------------------ main ------------------------------------------

def main():
	'''
	Open the text file (whose name is given on the command-line) in
	read mode. (Use mode "rb" for portability.) Read lines from it and
	write them to a PDF file whose name is derived by changing the
	text file's extension to ".pdf", if the extension is ".txt", or
	else by appending ".pdf" to the text file name. Print a default
	header and footer at the top and bottom of each page, which
	includes the (input) text file name, the date/time at which the
	PDF file was generated, and the page number. A default number of
	lines per page is used to ensure that there is no truncation of
	lines at the end of a page.
	'''

	# check for right # of args
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)

	# get input text file name
	txt_fn = sys.argv[1]

	# and open it for reading
	try:
		txt_fil = file(txt_fn, "rb")       # text file object
	except IOError:
		sys.stderr.write(sys.argv[0] + ": IO Error while opening file '" + \
		txt_fn + "'. Exiting\n")
		sys.exit(1)

	# set output file name based on input file name
	pdf_fn = change_file_ext(txt_fn, '.txt', '.pdf')

	# create the RL canvas object to write PDF content on.
	canv = canvas.Canvas(pdf_fn)

	# initialize a dict with the file-related vars
	file_info = {}
	file_info["txt_fn"] = txt_fn    # text file name
	file_info["txt_fil"] = txt_fil    # text file object
	file_info["pdf_fn"] = pdf_fn    # PDF file name
	file_info["pdf_canv"] = canv    # ReportLab PDF canvas object

	# set the page options. This var does not change during the
	# writing of the PDF file.
	pag_opt = {}  # dict for page options

	# set font info
	pag_opt["font_name"] = "Courier"
	pag_opt["font_size"] = 10

	pag_opt["lines_per_page"] = 72     # num. of lines to print on each page
	pag_opt["hdr_lines"] = 3                  # num. of lines in header
	pag_opt["ftr_lines"] = 3                  # num. of lines in footer

	# num. of lines in body of page
	pag_opt["body_lines"] = \
		pag_opt["lines_per_page"] - pag_opt["hdr_lines"] - pag_opt["ftr_lines"]

	# basename part of txt_fn (for PDF header/footer)
	pag_opt["txt_basename"] = os.path.split(txt_fn)[1]

	# date/time PDF file was generated (for PDF header/footer)
	pag_opt["gen_date_time"] = time.asctime()

	# PDF header string
	pag_opt["hdr_str"] = \
	    string.ljust("Source file: " + pag_opt["txt_basename"], 20) + \
		string.center("Generated: " + pag_opt["gen_date_time"], 40)

	# PDF footer string (same as header string)
	pag_opt["ftr_str"] = pag_opt["hdr_str"]

	# write the PDF file using the file info and page options
	write_pdf(file_info, pag_opt)

	# close the text file
	txt_fil.close()

##------------------------ usage -----------------------------------------

def usage():
	'''
	Prints help about the usage of the program on stderr.
	'''
	sys.stderr.write("Usage: " + sys.argv[0] + " text_file\n")
	sys.stderr.write("where text_file is the name of a text file.\n")
	sys.stderr.write(sys.argv[0] + " writes the contents of text_file\n")
	sys.stderr.write("to a PDF file with the same name but extension '.pdf'\n")

##------------------------ print_body() ----------------------------------

def write_pdf(file_info, pag_opt):
	'''
	Write the contents of the text file to the PDF file.
	"file_info" contains the file-related vars needed.
	"pag_opt" has the page options such as header/footer strings.
	'''

	# get needed vars out of file_info dict
	txt_fil = file_info["txt_fil"]
	canv = file_info["pdf_canv"]

	# set the page settings dict. This dict *does* change during the
	# writing of the PDF file, hence is a different dict
	# from pag_opt, which remains constant during the writing.

	pag_set = {}    # an empty dict

	# set some page settings
	pag_set["x"] = 0.25 * inch             # x-coord for text output
	pag_set["top_y"] = 11.0 * inch         # y-coord for 1st line on each page
	pag_set["y"] = pag_set["top_y"]                # y-coord for text output
	pag_set["dy"] = 0.125 * inch           # inter-line spacing, delta-y

	pag_set["line_ctr"] = 0             # line counter, reset on each new page

	# set the font for the canvas
	canv.setFont(pag_opt["font_name"], pag_opt["font_size"])

	pag_set["page_saved"] = 0                 # page saved flag 0/1
	pag_set["page_num"] = 1                   # page number

	# write the header for the first page, before the main loop
	write_hdr(file_info, pag_opt, pag_set)

	# main loop to generate PDF file from text file
	for lin in txt_fil:

		# mark page as unsaved, since we are going to write a line to 
		# it immediately
		pag_set["page_saved"] = 0

		# write the line to the page at given coordinates
		canv.drawString(pag_set["x"], pag_set["y"], lin)
		
		# decrement the y-coordinate
		pag_set["y"] = pag_set["y"] - pag_set["dy"]

		# increment the line counter
		pag_set["line_ctr"] += 1

		# check if enough lines have been written to this page
		if pag_set["line_ctr"] >= pag_opt["body_lines"]:

			# write the footer for the page
			write_ftr(file_info, pag_opt, pag_set)

			# if the page is not saved, ...
			if not pag_set["page_saved"]:

				# do stuff to save page and start next page
				canv.save()
				pag_set["page_saved"] = 1   # mark page as saved
				pag_set["page_num"] += 1   # increment page number
				pag_set["line_ctr"] = 0     # reset line number
				pag_set["y"] = pag_set["top_y"]   # reset y-coordinate

				# need to re-init font info for each page - 
				# since the RL pdfgen package resets it on each page save
				canv.setFont(pag_opt["font_name"], pag_opt["font_size"])

				# write the header for the next page
				write_hdr(file_info, pag_opt, pag_set)

	# end of main loop

	# code below is for a boundary condition - when last page contains
	# less than "body_lines" lines of text - we decrement "y" till
	# we reach right position to write the footer, then write it.
	if pag_set["line_ctr"] < pag_opt["body_lines"]:
		lines_remaining = pag_opt["body_lines"] - pag_set["line_ctr"]
		pag_set["y"] = pag_set["y"] - (pag_set["dy"] * lines_remaining)
		write_ftr(file_info, pag_opt, pag_set)

	# also for boundary condition, to save the last page
	if not pag_set["page_saved"]:
		canv.save()

##------------------------ write_hdr() -----------------------------------

def write_hdr(file_info, pag_opt, pag_set):
	'''
	Write header for the current page.
	'''
	# get needed vars out of the file_info dict
	canv = file_info["pdf_canv"]

	# append page num. to the header here (because it varies each time
	# write_hdr() is called.
	hdr_lin = pag_opt["hdr_str"] + \
		string.rjust("Page: " + str(pag_set["page_num"]), 20)

	# write the header

	canv.drawString(pag_set["x"], pag_set["y"], "")   # empty line above header
	pag_set["y"] = pag_set["y"] - pag_set["dy"]    # bump y down

	canv.drawString(pag_set["x"], pag_set["y"], hdr_lin) # the actual header
	pag_set["y"] = pag_set["y"] - pag_set["dy"]    # bump y down

	canv.drawString(pag_set["x"], pag_set["y"], "")   # empty line below header
	pag_set["y"] = pag_set["y"] - pag_set["dy"]    # bump y down

##------------------------ write_ftr() -----------------------------------

def write_ftr(file_info, pag_opt, pag_set):
	'''
	Write footer for the current page.
	In current version, footer is same as header, so just
	call write_hdr().
	'''
	write_hdr(file_info, pag_opt, pag_set)

##------------------------ Global code -----------------------------------

if __name__ == "__main__":
	main()
	
##------------------------ EOF -------------------------------------------

