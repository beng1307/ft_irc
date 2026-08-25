# 272_PRIVMSG_spoofed_client_prefix_rejection.spec
# Malicious Actor: Attempting to send forged prefix on PRIVMSG (e.g. :admin PRIVMSG Bob :Banned)
# Expected: Server rejects client-supplied prefix with 421 Unknown command or strips prefix without spoofing.
CLIENTS C1, C2

# Setup C1 (Attacker)
C1 SEND PASS 1234
C1 SEND NICK Ali304
C1 SEND USER ali304 0 * :Ali304
C1 EXPECT 001 Ali304 :*

# Setup C2 (Target)
C2 SEND PASS 1234
C2 SEND NICK Bob304
C2 SEND USER bob304 0 * :Bob304
C2 EXPECT 001 Bob304 :*

# Attacker attempts to forge prefix as 'admin'
C1 SEND :admin PRIVMSG Bob304 :You have been banned
C1 EXPECT 421 Ali304 Unknown command.
C2 NO_RECV :admin* PRIVMSG Bob304 :You have been banned
