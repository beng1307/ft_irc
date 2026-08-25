# 184_PING_double_colon_preservation.spec
# Tests double-colon payload preservation (e.g. PING ::cookie123)
# RFC Requirement: The first ':' marks trailing parameter; the token payload itself is ':cookie123'.
# Flaw: Server double-strips leading colon and replies with ':localhost PONG localhost :cookie123'
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING ::cookie123
C1 EXPECT :localhost PONG localhost ::cookie123
