# 135_TOPIC_persistence_across_part_and_rejoin.spec
# Tests that topic persists in channel across member PART and re-JOIN
# Expected: Client parting and rejoining finds the topic still set.
CLIENTS C1, C2

# Alice creates channel and sets topic
C1 SEND PASS 1234
C1 SEND NICK Ali363
C1 SEND USER ali363 0 * :Ali363
C1 EXPECT 001 Ali363 :*
C1 SEND JOIN #persist
C1 EXPECT :Ali363!* JOIN #persist
C1 SEND TOPIC #persist :Everlasting Topic
C1 EXPECT :Ali363!* TOPIC #persist :Everlasting Topic

# Bob joins, parts, and rejoins
C2 SEND PASS 1234
C2 SEND NICK Bob363
C2 SEND USER bob363 0 * :Bob363
C2 EXPECT 001 Bob363 :*
C2 SEND JOIN #persist
C2 EXPECT :Bob363!* JOIN #persist
C1 WAIT_RECV :Bob363!* JOIN #persist

C2 SEND PART #persist :Leaving temporarily
C2 EXPECT :Bob363!* PART #persist :Leaving temporarily
C1 WAIT_RECV :Bob363!* PART #persist :Leaving temporarily

C2 SEND JOIN #persist
C2 EXPECT :Bob363!* JOIN #persist
C1 WAIT_RECV :Bob363!* JOIN #persist

# Bob queries topic after rejoining
C2 SEND TOPIC #persist
C2 EXPECT 332 Bob363 #persist :Everlasting Topic
