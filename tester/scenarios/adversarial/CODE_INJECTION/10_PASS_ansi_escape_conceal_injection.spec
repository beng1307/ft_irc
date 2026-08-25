# 10_PASS_ansi_escape_conceal_injection.spec
# Vulnerability: PASS parameter containing ANSI conceal codes is logged in server console buffers,
# hiding admin audit logs or masking authentication failures.
# Expected secure behavior: Server must treat ANSI characters in passwords literally without console escape execution,
# failing authentication when password doesn't match and logging securely.
CLIENTS C1

# C1 sends PASS with ANSI conceal code
C1 SEND_RAW PASS \x1b[8m1234\r\n
C1 EXPECT 464 * :Password incorrect

C1 EXPECT_CONNECTED
