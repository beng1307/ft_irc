# 64_MODE_spoofed_prefix_rejection.spec
# Adversarial Security: Client injects fake IRC prefix ":victim!user@host" in MODE command line.
# Expected: Server must reject or ignore spoofed prefix and not attribute actions to the spoofed entity.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Attacker64
C1 SEND USER attacker64 0 * :Attacker64
C1 EXPECT 001 Attacker64 :*

# Attacker attempts to spoof command with leading prefix
C1 SEND_RAW :Victim!vic@host MODE #chan +i\r\n
# Server treats command as invalid token (not matching command list)
C1 EXPECT 421 Attacker64 Unknown command.
