# 279_USER_line_injection_lf_smuggling.spec
# Malicious Actor: IRC Line Smuggling via embedded \n (without \r) in USER command
# An attacker sends 'USER alice\nNICK hijacked 0 * :Real\r\n' to smuggle a newline into the username.
# Expected: Server rejects raw LF or sanitizes username so downstream broadcasts are not split.
# Bug: Raw \n is stored in username, splitting downstream ':Alice!alice\nNICK@localhost' messages.
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob401
C2 SEND USER bob401 0 * :Bob401
C2 EXPECT 001 Bob401 :*
C2 SEND JOIN #security
C2 EXPECT 353 Bob401 = #security :@Bob401

C1 SEND PASS 1234
C1 SEND NICK Ali401
C1 SEND USER ali401\nNICK 0 * :Real
C1 EXPECT 432 * :Erroneous nickname
