# 14_CAP_registered_client_nick_target.spec
# Tests CAP LS sent by an already registered client.
# Expected: Server replies with ':localhost CAP Alice LS :' targeting the client's nickname.
# Bug: Server hardcodes target as '*' (:localhost CAP * LS :), failing strict client parsers.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND CAP LS
C1 EXPECT :localhost CAP Alice LS :
