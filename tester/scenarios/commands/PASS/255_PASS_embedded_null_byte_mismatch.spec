# 255_PASS_embedded_null_byte_mismatch.spec
# Adversarial Attack: Embedded null byte in password payload (PASS 1234\x00extra\r\n)
# Must not truncate at null byte and falsely authenticate against '1234'
CLIENTS C1

C1 SEND_RAW PASS 1234\x00extra\r\n
C1 EXPECT 464 * :Password incorrect
