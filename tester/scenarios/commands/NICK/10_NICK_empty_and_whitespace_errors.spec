# 10_NICK_empty_and_whitespace_errors.spec
# Tests missing parameters and whitespace-only arguments for NICK.
CLIENTS C1

C1 SEND PASS 1234

# NICK with no parameters -> ERR_NONICKNAMEGIVEN (431)
C1 SEND NICK
C1 EXPECT 431 * :No nickname given

# NICK with whitespace only -> ERR_NONICKNAMEGIVEN (431)
C1 SEND NICK    
C1 EXPECT 431 * :No nickname given

# Client can still successfully set nickname and register
C1 SEND NICK Alice10
C1 SEND USER user10 0 * :Alice 10
C1 EXPECT 001 Alice10 :*
C1 EXPECT_CONNECTED

