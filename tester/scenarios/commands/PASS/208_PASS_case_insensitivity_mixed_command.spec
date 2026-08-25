# 208_PASS_case_insensitivity_mixed_command.spec
# Mixed case command 'PaSs 1234' must be accepted.
CLIENTS C1

C1 SEND PaSs 1234
C1 SEND NICK PAlice208
C1 SEND USER ali236 0 * :Ali236 Smith
C1 EXPECT 001 PAlice208 :*
