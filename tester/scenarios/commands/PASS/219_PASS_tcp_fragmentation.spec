# 219_PASS_tcp_fragmentation.spec
# PASS command received in multiple fragmented TCP chunks
CLIENTS C1

C1 SEND_RAW PA
C1 SEND_RAW SS\x201234\r\n
C1 SEND NICK PAliceFra
C1 SEND USER alicefrag 0 * :Alice Frag
C1 EXPECT 001 PAliceFra :*

