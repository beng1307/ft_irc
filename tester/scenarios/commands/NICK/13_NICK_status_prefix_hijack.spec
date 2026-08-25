# 13_NICK_status_prefix_hijack.spec
# Malicious actor attempts to set nickname with channel status prefix (@Admin or +Voice).
# Expected: Server rejects nickname starting with '@' or '+' with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK @Admin
C1 EXPECT 432 * @Admin :Erroneous nickname

C1 SEND NICK +Voice
C1 EXPECT 432 * +Voice :Erroneous nickname
