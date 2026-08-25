# 59_MODE_channel_destruction_and_mode_leak_isolation.spec
# Security / Lifecycle: Ensure modes are destroyed when the channel becomes empty and not leaked to recreated channel.
# Expected: Recreated channel resets to default modes (+), completely isolated from previous channel instance.
CLIENTS C1, C2

# C1 is Alice
C1 SEND PASS 1234
C1 SEND NICK Ali176
C1 SEND USER ali176 0 * :Ali176
C1 EXPECT 001 Ali176 :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob176
C2 SEND USER bob176 0 * :Bob176
C2 EXPECT 001 Bob176 :*

# Alice creates #ephemeral and configures all modes
C1 SEND JOIN #ephemeral
C1 EXPECT 353 Ali176 = #ephemeral :@Ali176
C1 EXPECT 366 Ali176 #ephemeral :End of /NAMES list

C1 SEND MODE #ephemeral +it
C1 EXPECT :Ali176!* MODE #ephemeral +it

C1 SEND MODE #ephemeral +k secret123
C1 EXPECT :Ali176!* MODE #ephemeral +k secret123

C1 SEND MODE #ephemeral +l 5
C1 EXPECT :Ali176!* MODE #ephemeral +l 5

# Alice parts, destroying the empty channel
C1 SEND PART #ephemeral :Destroying channel
C1 EXPECT :Ali176!* PART #ephemeral :Destroying channel

# Bob recreates #ephemeral
C2 SEND JOIN #ephemeral
C2 EXPECT 353 Bob176 = #ephemeral :@Bob176
C2 EXPECT 366 Bob176 #ephemeral :End of /NAMES list

# Bob checks modes: must be cleanly reset to default without key, invite-only, or limit
C2 SEND MODE #ephemeral
C2 EXPECT 324 Bob176 #ephemeral +
