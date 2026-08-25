# 11_NICK_spoofed_prefix_injection.spec
# Malicious actor attempts to spoof a client prefix (:Victim NICK AttackerNick)
# to force-rename another client or impersonate someone else.
# Expected: Server rejects the spoofed prefix or ignores it, never renaming Victim.
CLIENTS C1, C2

# C1 registers as Victim
C1 SEND PASS 1234
C1 SEND NICK Vic193
C1 SEND USER vic193 0 * :Vic193
C1 EXPECT 001 Vic193 :*

# C2 registers as Attacker
C2 SEND PASS 1234
C2 SEND NICK Atk193
C2 SEND USER atk193 0 * :Atk193
C2 EXPECT 001 Atk193 :*

# Attacker attempts to send spoofed prefix targeting Victim
C2 SEND_RAW :Vic193 NICK HackedNick\r\n
# Victim must remain unaffected as 'Victim'
C1 SEND PING localhost
C1 EXPECT :localhost PONG localhost :localhost
C1 EXPECT_CONNECTED
