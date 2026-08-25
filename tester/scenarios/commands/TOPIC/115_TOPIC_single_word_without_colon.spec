# 115_TOPIC_single_word_without_colon.spec
# Tests RFC 2812 §3.2.4: TOPIC <channel> [<topic>]
# Expected: Setting a single-word topic without a leading colon sets the topic and broadcasts to channel members.
# Bug: Server uses !line.contains(" :") to detect topic setting. Single word topic without colon is treated as a query, returning 331/332.
CLIENTS C1, C2

# Alice registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Ali343
C1 SEND USER ali343 0 * :Ali343
C1 EXPECT 001 Ali343 :*
C1 SEND JOIN #testchan
C1 EXPECT :Ali343!* JOIN #testchan

# Bob registers and joins channel
C2 SEND PASS 1234
C2 SEND NICK Bob343
C2 SEND USER bob343 0 * :Bob343
C2 EXPECT 001 Bob343 :*
C2 SEND JOIN #testchan
C2 EXPECT :Bob343!* JOIN #testchan
C1 WAIT_RECV :Bob343!* JOIN #testchan

# Alice sets topic without colon
C1 SEND TOPIC #testchan SingleWordTopic
C1 EXPECT :Ali343!* TOPIC #testchan :SingleWordTopic
C2 EXPECT :Ali343!* TOPIC #testchan :SingleWordTopic

# Bob queries topic
C2 SEND TOPIC #testchan
C2 EXPECT 332 Bob343 #testchan :SingleWordTopic
