# 263_PASS_double_cr_line_delimiters.spec
# Delimiter anomaly: Double \r before \n in 'PASS 1234\r\r\n'
# Delimited line is 'PASS 1234\r', parameter extracted is '1234\r', which mismatches '1234'
CLIENTS C1

C1 SEND_RAW PASS 1234\r\r\n
C1 EXPECT 464 * :Password incorrect
