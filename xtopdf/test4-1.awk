# awk script to count and print the num. of occurrences of each
# unique value in field 2 of the input
{ ct[$2]++ }
END { for (k in ct) 
      print k, "occurs", ct[k], "times" }
 
