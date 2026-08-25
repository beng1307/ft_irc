# 138_TOPIC_ampersand_channel_prefix.spec
# Tests TOPIC on channels with '&' prefix (&channel)
# Expected: Server properly handles TOPIC queries and updates on & channels.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali366
C1 SEND USER ali366 0 * :Ali366
C1 EXPECT 001 Ali366 :*
C1 SEND JOIN &localchan
C1 EXPECT :Ali366!* JOIN &localchan

# Alice sets topic on & channel
C1 SEND TOPIC &localchan :Local Channel Topic
C1 EXPECT :Ali366!* TOPIC &localchan :Local Channel Topic

# Alice queries topic
C1 SEND TOPIC &localchan
C1 EXPECT 332 Ali366 &localchan :Local Channel Topic
