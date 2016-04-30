# awk script to sum up and print fields 3, 4 and 5 of the input
{ s3 += $3; s4 += $4; s5 += $5 }
END { print "sum of field 3:", s3
      print "sum of field 4:", s4
      print "sum of field 5:", s5 }
