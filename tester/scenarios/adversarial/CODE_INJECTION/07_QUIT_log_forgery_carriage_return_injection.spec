# 07_QUIT_log_forgery_carriage_return_injection.spec
# Vulnerability: QUIT reason allows carriage return (\r) and terminal escape codes,
# which can forge server log lines or overwrite console records.
# Expected secure behavior: Server must strip \r and escape codes from quit messages.
CLIENTS C1, C2

# Setup Alice and Bob in a shared channel
C1 SEND PASS 1234
C1 SEND NICK Ali034
C1 SEND USER ali034 0 * :Ali034 Usr034
C1 EXPECT 001 Ali034 :*

C2 SEND PASS 1234
C2 SEND NICK Bob034
C2 SEND USER bob034 0 * :Bob034 Usr034
C2 EXPECT 001 Bob034 :*

C1 SEND JOIN #quitroom
C1 WAIT_RECV :Ali034!* JOIN #quitroom

C2 SEND JOIN #quitroom
C2 WAIT_RECV :Bob034!* JOIN #quitroom

# Alice quits with a carriage return and forged log text
C1 SEND_RAW QUIT :\rServer: [CRITICAL] Admin authorized shutdown\r\n

# Secure server must sanitize carriage returns, delivering safe single-line reason
C2 WAIT_RECV :Ali034!* QUIT :Server: [CRITICAL] Admin authorized shutdown
