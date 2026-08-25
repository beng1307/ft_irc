# 268_TOPIC_irc_command_injection_payload.spec
# Tests adversarial payload containing raw IRC command strings (e.g. KICK, MODE, QUIT) in topic.
# Expected: Server treats the payload strictly as topic data string and does not execute the injected commands.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali369
C1 SEND USER ali369 0 * :Ali369
C1 EXPECT 001 Ali369 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali369!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob369
C2 SEND USER bob369 0 * :Bob369
C2 EXPECT 001 Bob369 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob369!* JOIN #lobby
C1 WAIT_RECV :Bob369!* JOIN #lobby

# Alice sets topic with injected command strings
C1 SEND TOPIC #lobby :KICK #lobby Bob369 :banned && MODE #lobby +o Atk369
C1 EXPECT :Ali369!* TOPIC #lobby :KICK #lobby Bob369 :banned && MODE #lobby +o Atk369
C2 EXPECT :Ali369!* TOPIC #lobby :KICK #lobby Bob369 :banned && MODE #lobby +o Atk369

# Verify Bob is still in channel (not kicked)
C2 SEND PRIVMSG #lobby :I am still here
C1 EXPECT :Bob369!* PRIVMSG #lobby :I am still here
