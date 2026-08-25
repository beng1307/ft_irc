# 56_MODE_target_not_on_channel_operator_attempt.spec
# Edge Case: Operator attempts to promote/demote a user who is registered on the server but not in the target channel.
# Expected: Server returns 441 ERR_USERNOTINCHANNEL; no operator flags are applied or broadcast.
CLIENTS C1, C2

# C1 is Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 is Bob (connected to server, but in different channel or lobby)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #chanA
C1 EXPECT 353 Alice = #chanA :@Alice
C1 EXPECT 366 Alice #chanA :End of /NAMES list

# Alice tries to promote Bob in #chanA when Bob is not on #chanA
C1 SEND MODE #chanA +o Bob
C1 EXPECT 441 Alice Bob #chanA :They aren't on that channel

# Alice tries to demote Bob in #chanA
C1 SEND MODE #chanA -o Bob
C1 EXPECT 441 Alice Bob #chanA :They aren't on that channel
