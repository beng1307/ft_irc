# 148_PART_sole_member_channel_destroyed.spec
# Tests that when the last member parts a channel, the channel is destroyed,
# resetting modes/topic, and the next person to join becomes operator.
CLIENTS C1, C2

# Alice creates #temp and sets key +k secret
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #temp
C1 EXPECT :Alice!* JOIN #temp
C1 SEND MODE #temp +k secret
C1 EXPECT :Alice!* MODE #temp +k secret

# Alice parts #temp (channel now empty -> destroyed)
C1 SEND PART #temp :Done
C1 EXPECT :Alice!* PART #temp :Done

# Bob joins #temp without key (should succeed because channel was destroyed and modes reset)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #temp
C2 EXPECT :Bob!* JOIN #temp
C2 EXPECT 353 Bob = #temp :@Bob
C2 EXPECT 366 Bob #temp :End of /NAMES list
