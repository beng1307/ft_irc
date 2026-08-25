# 148_PART_sole_member_channel_destroyed.spec
# Tests that when the last member parts a channel, the channel is destroyed,
# resetting modes/topic, and the next person to join becomes operator.
CLIENTS C1, C2

# Alice creates #temp and sets key +k secret
C1 SEND PASS 1234
C1 SEND NICK Ali217
C1 SEND USER ali217 0 * :Ali217
C1 EXPECT 001 Ali217 :*
C1 SEND JOIN #temp
C1 EXPECT :Ali217!* JOIN #temp
C1 SEND MODE #temp +k secret
C1 EXPECT :Ali217!* MODE #temp +k secret

# Alice parts #temp (channel now empty -> destroyed)
C1 SEND PART #temp :Done
C1 EXPECT :Ali217!* PART #temp :Done

# Bob joins #temp without key (should succeed because channel was destroyed and modes reset)
C2 SEND PASS 1234
C2 SEND NICK Bob217
C2 SEND USER bob217 0 * :Bob217
C2 EXPECT 001 Bob217 :*
C2 SEND JOIN #temp
C2 EXPECT :Bob217!* JOIN #temp
C2 EXPECT 353 Bob217 = #temp :@Bob217
C2 EXPECT 366 Bob217 #temp :End of /NAMES list
