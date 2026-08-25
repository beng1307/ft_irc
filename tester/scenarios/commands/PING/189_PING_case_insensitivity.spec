# 189_PING_case_insensitivity.spec
# Tests case-insensitivity of PING command name ('ping', 'Ping', 'PiNg')
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali275
C1 SEND USER ali275 0 * :Ali275 Smith
C1 EXPECT 001 Ali275 :*

C1 SEND ping lowercase
C1 EXPECT :localhost PONG localhost :lowercase

C1 SEND Ping capitalized
C1 EXPECT :localhost PONG localhost :capitalized

C1 SEND pInG mixedcase
C1 EXPECT :localhost PONG localhost :mixedcase
