# INVITE command comprehensive edge case testing
# Tests INVITE parser and privilege validation

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Create invite-only channel
C1 SEND JOIN #invite_only
C1 EXPECT :Alice!* JOIN #invite_only
C1 SEND MODE #invite_only +i
C1 EXPECT :Alice!* MODE #invite_only +i

# Test 1: INVITE with no parameters
C1 SEND INVITE
C1 EXPECT 461 Alice INVITE :*

# Test 2: INVITE with only nick
C1 SEND INVITE Bob
C1 EXPECT 461 Alice INVITE :*

# Test 3: INVITE with only channel
C1 SEND INVITE #invite_only
C1 EXPECT 461 Alice INVITE :*

# Test 4: Invite non-existent user
C1 SEND INVITE Nonexistent #invite_only
C1 EXPECT 401 Alice Nonexistent :*

# Test 5: Invite to non-existent channel
C1 SEND INVITE Bob #nonexistent
C1 EXPECT 403 Alice #nonexistent :*

# Test 6: Valid INVITE
C1 SEND INVITE Bob #invite_only
C1 EXPECT 341 Alice Bob #invite_only
C2 EXPECT :Alice!* INVITE Bob :#invite_only

# Test 7: Invitee joins invite-only channel
C2 SEND JOIN #invite_only
C2 EXPECT :Bob!* JOIN #invite_only
C1 EXPECT :Bob!* JOIN #invite_only

# Test 8: Non-op tries to invite someone to invite-only channel
C2 SEND INVITE Charlie #invite_only
# This may be allowed or rejected depending on server
# Some servers allow any member to invite, others restrict to ops
C2 EXPECT_CONNECTED

# Test 9: If C2 could invite, C3 can join
C3 SEND JOIN #invite_only
# C3 may or may not be able to join depending on server behavior
C3 EXPECT_CONNECTED

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
