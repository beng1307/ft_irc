# 201_PASS_empty_colon.spec
# PASS : (empty trailing argument) sends empty password "", which fails match against server password
CLIENTS C1

C1 SEND_RAW PASS :\r\n
C1 EXPECT 464 * :Password incorrect
