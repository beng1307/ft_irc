# 196_PING_special_characters_payload.spec
# Tests PING token containing symbols and punctuation marks
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :!@#$%^&*()_+-=[]{}|;,.<>?
C1 EXPECT :localhost PONG localhost :!@#$%^&*()_+-=[]{}|;,.<>?
