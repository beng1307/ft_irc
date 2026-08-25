# 107_TOPIC_persistence_across_part_and_rejoin.spec
# Tests that topic persists in channel across member PART and re-JOIN
# Expected: Client parting and rejoining finds the topic still set.
CLIENTS C1, C2

# Alice creates channel and sets topic
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #persist
C1 EXPECT :Alice!* JOIN #persist
C1 SEND TOPIC #persist :Everlasting Topic
C1 EXPECT :Alice!* TOPIC #persist :Everlasting Topic

# Bob joins, parts, and rejoins
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #persist
C2 EXPECT :Bob!* JOIN #persist
C1 WAIT_RECV :Bob!* JOIN #persist

C2 SEND PART #persist :Leaving temporarily
C2 EXPECT :Bob!* PART #persist :Leaving temporarily
C1 WAIT_RECV :Bob!* PART #persist :Leaving temporarily

C2 SEND JOIN #persist
C2 EXPECT :Bob!* JOIN #persist
C1 WAIT_RECV :Bob!* JOIN #persist

# Bob queries topic after rejoining
C2 SEND TOPIC #persist
C2 EXPECT 332 Bob #persist :Everlasting Topic
