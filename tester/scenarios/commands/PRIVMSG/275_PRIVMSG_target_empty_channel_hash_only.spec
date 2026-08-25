# 275_PRIVMSG_target_empty_channel_hash_only.spec
# Malicious / Edge Input: Targeting a single '#' character or invalid channel prefix alone
# Expected: Server replies with 403 ERR_NOSUCHCHANNEL (# :No such channel) without crash or state corruption.
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 sends PRIVMSG to solitary '#'
C1 SEND PRIVMSG # :Hello empty hash
C1 EXPECT 403 Alice # :No such channel

# C1 sends PRIVMSG to solitary '&'
C1 SEND PRIVMSG & :Hello empty ampersand
C1 EXPECT 403 Alice & :No such channel
