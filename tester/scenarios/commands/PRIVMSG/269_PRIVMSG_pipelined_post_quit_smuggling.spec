# 269_PRIVMSG_pipelined_post_quit_smuggling.spec
# Malicious Actor: Pipelining commands after QUIT in a single TCP packet
# Attacker sends 'QUIT :Leaving\r\nPRIVMSG Bob :I am still talking\r\n' in one burst.
# Expected: Server closes/aborts processing on QUIT; smuggled PRIVMSG is discarded and not delivered.
# Bug: handle_line continues through remaining buffer because client object exists until buffer drains.
CLIENTS C1, C2

# Setup C1 (Attacker)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2 (Target)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Attacker pipelines QUIT and PRIVMSG in single burst
C1 SEND QUIT :Leaving\r\nPRIVMSG Bob :Ghost message
C1 EXPECT ERROR :Closing connection
C2 NO_RECV :Alice!* PRIVMSG Bob :Ghost message
