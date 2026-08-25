# 157_PART_ampersand_channel.spec
# Tests RFC 1459/2812 local channel '&' prefix support with PART.
CLIENTS C1, C2

# Setup: Alice and Bob in &local
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN &local
C1 EXPECT :Alice!* JOIN &local

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN &local
C2 EXPECT :Bob!* JOIN &local
C1 WAIT_RECV :Bob!* JOIN &local

# Alice parts &local
C1 SEND PART &local :Leaving local
C1 EXPECT :Alice!* PART &local :Leaving local
C2 EXPECT :Alice!* PART &local :Leaving local
