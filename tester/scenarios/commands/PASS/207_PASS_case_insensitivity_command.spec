# 207_PASS_case_insensitivity_command.spec
# IRC command names are case-insensitive. 'pass 1234' must be accepted.
CLIENTS C1

C1 SEND pass 1234
C1 SEND NICK PassAlice207
C1 SEND USER alice207 0 * :Alice Smith
C1 EXPECT 001 PassAlice207 :*
