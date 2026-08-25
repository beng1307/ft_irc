# 225_PASS_leading_space_rejection.spec
# Leading whitespace before command token violates IRC grammar and must return 421 ERR_UNKNOWNCOMMAND
CLIENTS C1

C1 SEND_RAW   PASS 1234\r\n
C1 EXPECT 421 * Unknown command.
