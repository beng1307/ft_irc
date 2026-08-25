# 218_PASS_pipelined_registration.spec
# Registration commands sent together in a single TCP payload frame
CLIENTS C1

C1 SEND_RAW PASS 1234\r\nNICK PAlicePip\r\nUSER alicepipe 0 * :Ali246 Pipe\r\n
C1 EXPECT 001 PAlicePip :*
