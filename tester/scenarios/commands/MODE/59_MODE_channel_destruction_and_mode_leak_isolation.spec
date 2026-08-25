# 59_MODE_channel_destruction_and_mode_leak_isolation.spec
# Security / Lifecycle: Ensure modes are destroyed when the channel becomes empty and not leaked to recreated channel.
# Expected: Recreated channel resets to default modes (+), completely isolated from previous channel instance.
CLIENTS C1, C2

# C1 is Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #ephemeral and configures all modes
C1 SEND JOIN #ephemeral
C1 EXPECT 353 Alice = #ephemeral :@Alice
C1 EXPECT 366 Alice #ephemeral :End of /NAMES list

C1 SEND MODE #ephemeral +it
C1 EXPECT :Alice!* MODE #ephemeral +it

C1 SEND MODE #ephemeral +k secret123
C1 EXPECT :Alice!* MODE #ephemeral +k secret123

C1 SEND MODE #ephemeral +l 5
C1 EXPECT :Alice!* MODE #ephemeral +l 5

# Alice parts, destroying the empty channel
C1 SEND PART #ephemeral :Destroying channel
C1 EXPECT :Alice!* PART #ephemeral :Destroying channel

# Bob recreates #ephemeral
C2 SEND JOIN #ephemeral
C2 EXPECT 353 Bob = #ephemeral :@Bob
C2 EXPECT 366 Bob #ephemeral :End of /NAMES list

# Bob checks modes: must be cleanly reset to default without key, invite-only, or limit
C2 SEND MODE #ephemeral
C2 EXPECT 324 Bob #ephemeral +
