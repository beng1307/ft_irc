# 42_MODE_user_mode_query.spec
# Tests querying or setting user mode (e.g., MODE Alice, MODE Alice +i)
# Expected: Server responds with 221 RPL_UMODEIS (or appropriate numeric reply).
# Bug: Server drops the command silently without any response because target does not start with '#'.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali159
C1 SEND USER ali159 0 * :Ali159
C1 EXPECT 001 Ali159 :*

# Query own user modes
C1 SEND MODE Ali159
C1 EXPECT 221 Ali159 :*
