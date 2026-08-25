# 11_NICK_spoofed_prefix_injection.spec
# Malicious actor attempts to spoof a client prefix (:Victim NICK AttackerNick)
# to force-rename another client or impersonate someone else.
# Expected: Server rejects the spoofed prefix or ignores it, never renaming Victim.
CLIENTS C1, C2

# C1 registers as Victim
C1 SEND PASS 1234
C1 SEND NICK Victim
C1 SEND USER victim 0 * :Victim
C1 EXPECT 001 Victim :*

# C2 registers as Attacker
C2 SEND PASS 1234
C2 SEND NICK Attacker
C2 SEND USER attacker 0 * :Attacker
C2 EXPECT 001 Attacker :*

# Attacker attempts to send spoofed prefix targeting Victim
C2 SEND_RAW :Victim NICK HackedNick\r\n
# Victim must remain unaffected as 'Victim'
C1 SEND PING localhost
C1 EXPECT :localhost PONG localhost :localhost
C1 EXPECT_CONNECTED
