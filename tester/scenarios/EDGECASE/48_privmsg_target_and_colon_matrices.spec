# Scenario 48: PRIVMSG Target and Colon Formatting Matrix
# Tests PRIVMSG errors (401, 403, 411, 412, 442) and preservation of messages with multiple colons
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali010
C1 SEND USER ali010 0 * :Ali010
C1 EXPECT 001 Ali010 :*

C2 SEND PASS 1234
C2 SEND NICK Bob010
C2 SEND USER bob010 0 * :Bob010
C2 EXPECT 001 Bob010 :*

# 411: No recipient
C1 SEND PRIVMSG
C1 EXPECT 411 Ali010 :*

# 412: No text to send
C1 SEND PRIVMSG Bob010
C1 EXPECT 412 Ali010 :*

# 401: Non-existent nick
C1 SEND PRIVMSG Nobody :Hello
C1 EXPECT 401 Ali010 Nobody :No such nick/channel

# 403: Non-existent channel
C1 SEND PRIVMSG #nonexistent :Hello
C1 EXPECT 403 Ali010 #nonexistent :No such channel

# Alice creates #privmsgroom
C1 SEND JOIN #privmsgroom
C1 EXPECT :Ali010!* JOIN #privmsgroom

# 404: Bob is not in #privmsgroom
C2 SEND PRIVMSG #privmsgroom :Hello from outside
C2 EXPECT 404 Bob010 #privmsgroom :Cannot send to channel



# Bob joins
C2 SEND JOIN #privmsgroom
C2 WAIT_RECV :Bob010!* JOIN #privmsgroom

# Message containing multiple colons inside text
C1 SEND PRIVMSG #privmsgroom :colon1: colon2: colon3 :colon4
C2 WAIT_RECV :Ali010!* PRIVMSG #privmsgroom :colon1: colon2: colon3 :colon4
