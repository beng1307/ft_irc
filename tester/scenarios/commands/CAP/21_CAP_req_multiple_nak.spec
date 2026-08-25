# 21_CAP_req_multiple_nak.spec
# Tests requesting multiple capabilities simultaneously in CAP REQ.
# Expected: Server replies with 'CAP * NAK :multi-prefix sasl account-notify' rejecting all unsupported capabilities.
# Bug: Server drops CAP REQ silently with 0 bytes.
CLIENTS C1

C1 SEND CAP LS
C1 EXPECT :localhost CAP * LS :
C1 SEND CAP REQ :multi-prefix sasl account-notify
C1 EXPECT :localhost CAP * NAK :multi-prefix sasl account-notify
