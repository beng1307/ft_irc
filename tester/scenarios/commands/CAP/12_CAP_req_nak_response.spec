# 12_CAP_req_nak_response.spec
# Tests IRCv3 CAP REQ negotiation when requesting capabilities.
# Expected: Server responds with CAP * NAK :multi-prefix since no capabilities are supported.
# Bug: Server drops CAP REQ silently with 0 bytes, deadlocking IRCv3 clients during handshake.
CLIENTS C1

C1 SEND CAP LS
C1 EXPECT :localhost CAP * LS :
C1 SEND CAP REQ :multi-prefix
C1 EXPECT :localhost CAP * NAK :multi-prefix
