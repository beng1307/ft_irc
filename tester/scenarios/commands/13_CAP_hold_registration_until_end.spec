# 13_CAP_hold_registration_until_end.spec
# Tests IRCv3 registration hold: welcome burst (001) must be delayed until CAP END.
# Expected: Server holds registration while in CAP negotiation; 001 is only sent after CAP END.
# Bug: Server registers immediately upon receiving USER, ignoring ongoing CAP negotiation.
CLIENTS C1

C1 SEND CAP LS
C1 EXPECT :localhost CAP * LS :
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
# Server should NOT send 001 yet (quiet period)
C1 EXPECT_NONE 200ms
C1 SEND CAP END
C1 EXPECT 001 Alice :*
