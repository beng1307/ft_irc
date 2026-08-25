# 42_MODE_user_mode_query.spec
# Tests querying or setting user mode (e.g., MODE Alice, MODE Alice +i)
# Expected: Server responds with 221 RPL_UMODEIS (or appropriate numeric reply).
# Bug: Server drops the command silently without any response because target does not start with '#'.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Query own user modes
C1 SEND MODE Alice
C1 EXPECT 221 Alice :*
