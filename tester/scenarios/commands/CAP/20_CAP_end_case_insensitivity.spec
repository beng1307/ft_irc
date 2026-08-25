# 20_CAP_end_case_insensitivity.spec
# Tests case-insensitivity of 'CAP end' during registration.
# Expected: 'CAP end' finishes negotiation and allows normal registration.
# Bug: Server checks arguments[0] == "END" case-sensitively, failing on lowercase 'end'.
CLIENTS C1

C1 SEND CAP ls
C1 EXPECT :localhost CAP * LS :
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 SEND CAP end
C1 EXPECT 001 Alice :*
