# 281_USER_spoofed_client_prefix_rejection.spec
# Malicious Actor: Client-Side Prefix Spoofing
# An attacker sends a forged server/user prefix ':spoofed.net USER alice 0 * :Real'
# Expected: Server rejects command with 421 Unknown command per RFC 2812 §2.3.1.
CLIENTS C1

C1 SEND :spoofed.server.net USER alice 0 * :Alice
C1 EXPECT 421 * Unknown command.

C1 SEND :attacker!hacker@evil.com USER alice 0 * :Alice
C1 EXPECT 421 * Unknown command.
