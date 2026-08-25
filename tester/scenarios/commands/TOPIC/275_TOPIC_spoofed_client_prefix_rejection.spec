# 275_TOPIC_spoofed_client_prefix_rejection.spec
# Tests client attempting to forge a server or client prefix on TOPIC command line.
# Expected: Server rejects command starting with colon as 421 ERR_UNKNOWNCOMMAND or invalid command.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice attempts to spoof prefix
C1 SEND :FakePrefix TOPIC #lobby :Spoofed Topic
C1 EXPECT 421 Alice :FakePrefix :Unknown command
