# 265_PASS_spoofed_prefix_rejection.spec
# Adversarial Scenario: Client sends spoofed prefix (:attacker PASS 1234\r\n)
# Server extracts ':attacker' as command verb and rejects with 421 ERR_UNKNOWNCOMMAND
CLIENTS C1

C1 SEND_RAW :attacker PASS 1234\r\n
C1 EXPECT 421 * Unknown command.
