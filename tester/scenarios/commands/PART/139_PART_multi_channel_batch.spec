# 139_PART_multi_channel_batch.spec
# Tests RFC 2812 §3.2.2 multi-channel batch parting syntax: PART #chan1,#chan2 [<Part Message>]
# Expected: Client parts both #chan1 and #chan2, broadcasting PART notifications on both channels.
# Bug: Server treats '#chan1,#chan2' as a single literal channel name instead of splitting by comma, returning 403.
CLIENTS C1, C2

# Setup: Alice joins #chan1 and #chan2
C1 SEND PASS 1234
C1 SEND NICK Ali208
C1 SEND USER ali208 0 * :Ali208
C1 EXPECT 001 Ali208 :*
C1 SEND JOIN #chan1
C1 EXPECT :Ali208!* JOIN #chan1
C1 SEND JOIN #chan2
C1 EXPECT :Ali208!* JOIN #chan2

# Setup: Bob joins #chan1 and #chan2
C2 SEND PASS 1234
C2 SEND NICK Bob208
C2 SEND USER bob208 0 * :Bob208
C2 EXPECT 001 Bob208 :*
C2 SEND JOIN #chan1
C2 EXPECT :Bob208!* JOIN #chan1
C1 WAIT_RECV :Bob208!* JOIN #chan1
C2 SEND JOIN #chan2
C2 EXPECT :Bob208!* JOIN #chan2
C1 WAIT_RECV :Bob208!* JOIN #chan2

# Alice batch parts both channels with reason
C1 SEND PART #chan1,#chan2 :Leaving all
C1 EXPECT :Ali208!* PART #chan1 :Leaving all
C2 EXPECT :Ali208!* PART #chan1 :Leaving all
C1 EXPECT :Ali208!* PART #chan2 :Leaving all
C2 EXPECT :Ali208!* PART #chan2 :Leaving all
