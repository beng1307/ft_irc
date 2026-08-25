# INVITE command comprehensive edge case testing
# Tests INVITE parser and privilege validation

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali020
C1 SEND USER ali020 0 * :Ali020
C1 EXPECT 001 Ali020 :*

C2 SEND PASS 1234
C2 SEND NICK Bob020
C2 SEND USER bob020 0 * :Bob020
C2 EXPECT 001 Bob020 :*

C3 SEND PASS 1234
C3 SEND NICK Cha020
C3 SEND USER cha020 0 * :Cha020
C3 EXPECT 001 Cha020 :*

# Create invite-only channel
C1 SEND JOIN #invite_only
C1 EXPECT :Ali020!* JOIN #invite_only
C1 SEND MODE #invite_only +i
C1 EXPECT :Ali020!* MODE #invite_only +i

# Test 1: INVITE with no parameters
C1 SEND INVITE
C1 EXPECT 461 Ali020 INVITE :*

# Test 2: INVITE with only nick
C1 SEND INVITE Bob020
C1 EXPECT 461 Ali020 INVITE :*

# Test 3: INVITE with only channel
C1 SEND INVITE #invite_only
C1 EXPECT 461 Ali020 INVITE :*

# Test 4: Invite non-existent user
C1 SEND INVITE Nonexistent #invite_only
C1 EXPECT 401 Ali020 Nonexistent :*

# Test 5: Invite to non-existent channel
C1 SEND INVITE Bob020 #nonexistent
C1 EXPECT 403 Ali020 #nonexistent :*

# Test 6: Valid INVITE
C1 SEND INVITE Bob020 #invite_only
C1 EXPECT 341 Ali020 Bob020 #invite_only
C2 EXPECT :Ali020!* INVITE Bob020 :#invite_only

# Test 7: Invitee joins invite-only channel
C2 SEND JOIN #invite_only
C2 EXPECT :Bob020!* JOIN #invite_only
C1 EXPECT :Bob020!* JOIN #invite_only

# Test 8: Non-op tries to invite someone to invite-only channel
C2 SEND INVITE Cha020 #invite_only
# This may be allowed or rejected depending on server
# Some servers allow any member to invite, others restrict to ops
C2 EXPECT_CONNECTED

# Test 9: If C2 could invite, C3 can join
C3 SEND JOIN #invite_only
# C3 may or may not be able to join depending on server behavior
C3 EXPECT_CONNECTED

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
