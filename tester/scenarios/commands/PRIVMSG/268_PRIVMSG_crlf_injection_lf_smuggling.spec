# 268_PRIVMSG_crlf_injection_lf_smuggling.spec
# Malicious Actor: IRC Protocol / Line Injection via embedded \n in PRIVMSG payload
# An attacker sends 'PRIVMSG Bob :Hello\nKICK #chan Alice\r\n' to inject a command into Bob's stream.
# Expected: Server sanitizes raw LF/CR or rejects the line so recipient stream is not corrupted.
# Bug: Raw \n is delivered verbatim to Bob, causing downstream protocol desynchronization / line injection.
CLIENTS C1, C2

# Setup C1 (Attacker)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2 (Victim)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Attacker sends message containing raw unescaped LF
C1 SEND PRIVMSG Bob :Hello\nKICK #chan Alice
# Victim should NOT receive unescaped raw LF that splits IRC protocol lines
C2 NO_RECV :Alice!* PRIVMSG Bob :Hello\nKICK #chan Alice
