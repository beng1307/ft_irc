# 257_PASS_pipelined_duplicate_pass_storm.spec
# Adversarial Attack: Multiple duplicate PASS commands flooded in a single TCP packet
CLIENTS C1

C1 SEND_RAW PASS 1234\r\nNICK PassStorm\r\nUSER passstorm 0 * :Storm\r\nPASS 1234\r\nPASS 1234\r\nPASS 1234\r\n
C1 EXPECT 001 PassStorm :*
C1 EXPECT 462 PassStorm :You may not reregister
C1 EXPECT 462 PassStorm :You may not reregister
C1 EXPECT 462 PassStorm :You may not reregister
