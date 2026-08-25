# 224_PASS_tab_delimiter_rejection.spec
# PASS separated by tab (\t) instead of space is not a valid IRC command token and must return 421 ERR_UNKNOWNCOMMAND
CLIENTS C1

C1 SEND_RAW PASS\t1234\r\n
C1 EXPECT 421 * Unknown command.
