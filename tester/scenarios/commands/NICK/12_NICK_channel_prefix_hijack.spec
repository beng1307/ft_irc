# 12_NICK_channel_prefix_hijack.spec
# Malicious actor attempts to set nickname to a channel identifier (#general or &secret).
# If allowed, channel routing becomes ambiguous and breaks PRIVMSG/JOIN/KICK.
# Expected: Server rejects nickname starting with '#' or '&' with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK #general
C1 EXPECT 432 * #general :Erroneous nickname

C1 SEND NICK &secret
C1 EXPECT 432 * &secret :Erroneous nickname
