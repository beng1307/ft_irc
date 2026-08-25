# 63_INVITE_colon_prefix_target_nick.spec
# Tests colon prefix on first parameter (target nickname, e.g. INVITE :Bob #secret).
# Expected: Server strips colon and matches target 'Bob', returning 341 RPL_INVITING.
# Bug: Server treats target literally as ':Bob' and fails with 401 ERR_NOSUCHNICK.
CLIENTS C1, C2

# Alice61 registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Alice61
C1 SEND USER alice61 0 * :Alice
C1 EXPECT 001 Alice61 :*
C1 SEND JOIN #secret61
C1 EXPECT :Alice61!* JOIN #secret61
C1 SEND MODE #secret61 +i
C1 EXPECT :Alice61!* MODE #secret61 +i

# Bob61 registers
C2 SEND PASS 1234
C2 SEND NICK Bob61
C2 SEND USER bob61 0 * :Bob
C2 EXPECT 001 Bob61 :*

# Alice61 invites Bob61 with colon on first parameter; RFC 2812 §2.3.1 treats ':Bob61 #secret61' as single trailing parameter
C1 SEND INVITE :Bob61 #secret61
C1 EXPECT 461 Alice61 INVITE :Not enough parameters
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
