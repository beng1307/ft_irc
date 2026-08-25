# 23_JOIN_multi_channel.spec
# Tests RFC 1459/2812 multi-channel batch join syntax (e.g. JOIN #chan1,#chan2)
# Expected: Client joins #chan1 and #chan2 separately, receiving names list for both channels.
# Bug: Server treats '#chan1,#chan2' as a single literal channel name instead of splitting by comma.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali106
C1 SEND USER ali106 0 * :Ali106
C1 EXPECT 001 Ali106 :*

# Batch join two channels
C1 SEND JOIN #chan1,#chan2
C1 EXPECT * JOIN *#chan1*
C1 EXPECT 353 Ali106 = #chan1 :*Ali106*
C1 EXPECT 366 Ali106 #chan1 :End of /NAMES list
C1 EXPECT * JOIN *#chan2*
C1 EXPECT 353 Ali106 = #chan2 :*Ali106*
C1 EXPECT 366 Ali106 #chan2 :End of /NAMES list
