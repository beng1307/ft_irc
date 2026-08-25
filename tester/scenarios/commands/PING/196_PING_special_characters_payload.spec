# 196_PING_special_characters_payload.spec
# Tests PING token containing symbols and punctuation marks
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali282
C1 SEND USER ali282 0 * :Ali282 Smith
C1 EXPECT 001 Ali282 :*

C1 SEND PING :!@#$%^&*()_+-=[]{}|;,.<>?
C1 EXPECT :localhost PONG localhost :!@#$%^&*()_+-=[]{}|;,.<>?
