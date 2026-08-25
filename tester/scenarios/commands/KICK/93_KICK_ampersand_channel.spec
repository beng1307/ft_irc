# 93_KICK_ampersand_channel.spec
# Tests KICK on local channels starting with '&' prefix (&localchan).
# Expected: Server supports kicking from '&' prefixed channels.
CLIENTS C1, C2

# Alice registers and creates &localchan
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN &localchan
C1 EXPECT :Alice!* JOIN &localchan

# Bob registers and joins &localchan
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN &localchan
C2 EXPECT :Bob!* JOIN &localchan
C1 WAIT_RECV :Bob!* JOIN &localchan

# Alice kicks Bob from &localchan
C1 SEND KICK &localchan Bob :local kick
C1 EXPECT :Alice!* KICK &localchan Bob :local kick
C2 EXPECT :Alice!* KICK &localchan Bob :local kick
