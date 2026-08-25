# 93_KICK_ampersand_channel.spec
# Tests KICK on local channels starting with '&' prefix (&localchan).
# Expected: Server supports kicking from '&' prefixed channels.
CLIENTS C1, C2

# Alice registers and creates &localchan
C1 SEND PASS 1234
C1 SEND NICK Ali148
C1 SEND USER ali148 0 * :Ali148
C1 EXPECT 001 Ali148 :*
C1 SEND JOIN &localchan
C1 EXPECT :Ali148!* JOIN &localchan

# Bob registers and joins &localchan
C2 SEND PASS 1234
C2 SEND NICK Bob148
C2 SEND USER bob148 0 * :Bob148
C2 EXPECT 001 Bob148 :*
C2 SEND JOIN &localchan
C2 EXPECT :Bob148!* JOIN &localchan
C1 WAIT_RECV :Bob148!* JOIN &localchan

# Alice kicks Bob from &localchan
C1 SEND KICK &localchan Bob148 :local kick
C1 EXPECT :Ali148!* KICK &localchan Bob148 :local kick
C2 EXPECT :Ali148!* KICK &localchan Bob148 :local kick
