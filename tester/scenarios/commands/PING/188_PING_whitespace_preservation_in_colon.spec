# 188_PING_whitespace_preservation_in_colon.spec
# Tests trailing colon payload with leading/trailing spaces inside the colon
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :  spaces  
C1 EXPECT :localhost PONG localhost :  spaces  
