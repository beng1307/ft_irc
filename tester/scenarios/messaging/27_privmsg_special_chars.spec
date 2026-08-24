# PRIVMSG with special characters: tabs, multiple spaces, and printable control chars.
# Ensures server doesn't mangle or reject valid IRC messages.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Message with leading/trailing spaces
C1 SEND PRIVMSG Bob :   spaced message   
C2 WAIT_RECV :Alice!* PRIVMSG Bob :   spaced message   

# Message with tabs (should be preserved)
C1 SEND PRIVMSG Bob :hello	world	tab
C2 WAIT_RECV :Alice!* PRIVMSG Bob :hello	world	tab

# Message with punctuation
C1 SEND PRIVMSG Bob :!@#$%^&*()_+-={}[];'<>?,./~`
C2 WAIT_RECV :Alice!* PRIVMSG Bob :!@#$%^&*()_+-={}[];'<>?,./~`

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
