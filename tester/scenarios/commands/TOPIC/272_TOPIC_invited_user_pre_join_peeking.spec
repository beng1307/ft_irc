# 272_TOPIC_invited_user_pre_join_peeking.spec
# Tests that an invited user (in invited_fds but not yet joined) cannot peek at or set the topic of an invite-only channel (+i).
# Expected: Server rejects pre-join TOPIC command with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# Alice creates invite-only channel and sets topic
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #inviteonly
C1 EXPECT :Alice!* JOIN #inviteonly
C1 SEND MODE #inviteonly +i
C1 EXPECT :Alice!* MODE #inviteonly +i
C1 SEND TOPIC #inviteonly :Confidential Pre-Meeting Notes
C1 EXPECT :Alice!* TOPIC #inviteonly :Confidential Pre-Meeting Notes

# Bob connects and gets invited
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C1 SEND INVITE Bob #inviteonly
C1 EXPECT 341 Alice Bob #inviteonly
C2 EXPECT :Alice!* INVITE Bob :#inviteonly

# Bob tries to peek at topic before joining
C2 SEND TOPIC #inviteonly
C2 EXPECT 442 Bob #inviteonly :You're not on that channel

# Bob tries to set topic before joining
C2 SEND TOPIC #inviteonly :Premature Change
C2 EXPECT 442 Bob #inviteonly :You're not on that channel
