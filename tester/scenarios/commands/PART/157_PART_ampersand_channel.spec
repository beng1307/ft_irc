# 157_PART_ampersand_channel.spec
# Tests RFC 1459/2812 local channel '&' prefix support with PART.
CLIENTS C1, C2

# Setup: Alice and Bob in &local
C1 SEND PASS 1234
C1 SEND NICK Ali226
C1 SEND USER ali226 0 * :Ali226
C1 EXPECT 001 Ali226 :*
C1 SEND JOIN &local
C1 EXPECT :Ali226!* JOIN &local

C2 SEND PASS 1234
C2 SEND NICK Bob226
C2 SEND USER bob226 0 * :Bob226
C2 EXPECT 001 Bob226 :*
C2 SEND JOIN &local
C2 EXPECT :Bob226!* JOIN &local
C1 WAIT_RECV :Bob226!* JOIN &local

# Alice parts &local
C1 SEND PART &local :Leaving local
C1 EXPECT :Ali226!* PART &local :Leaving local
C2 EXPECT :Ali226!* PART &local :Leaving local
