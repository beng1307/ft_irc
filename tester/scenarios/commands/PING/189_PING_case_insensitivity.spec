# 189_PING_case_insensitivity.spec
# Tests case-insensitivity of PING command name ('ping', 'Ping', 'PiNg')
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND ping lowercase
C1 EXPECT :localhost PONG localhost :lowercase

C1 SEND Ping capitalized
C1 EXPECT :localhost PONG localhost :capitalized

C1 SEND pInG mixedcase
C1 EXPECT :localhost PONG localhost :mixedcase
